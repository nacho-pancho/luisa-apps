# -*- coding: utf-8 -*-
#
# interface for creating and manipulating HDF5 files containing LUISA training data
# compatible with the Calamari OCR
#
import os
import h5py
import numpy as np
import codecs

comp       = 'gzip'
# old H5PY API
string_type = h5py.special_dtype(vlen=np.dtype('int32'))
# old H5PY API, should be equivalent to h5py.vlen_dtype(np.dtype('uint8'))
pixel_type  = h5py.special_dtype(vlen=np.dtype('uint8'))
dim_type    = int

#
# a typical LUISA document contains about 50 lines of text
# we have around 2.000.000 documents, but far less are really good for training
# calamari.
#
MAX_SAMPLES = (2**20)


def create_codec():
    '''
    Calamari creates a 'custom codec' for transcripts which simply records
    every appearing character in all transcripts and then uses the index
    within that codec to map letters to numbers.
    Here we create a 'calamari-like' codec for the whole set of Latin-1 characters.
    This should be enough to represent any transcription introduced by users via LUISA
    '''
    codec = list()
    for i in range(32, 127):
        codec.append(codecs.decode(i.to_bytes(1, byteorder='big'), encoding='latin-1'))
    for i in range(160, 256):
        codec.append(codecs.decode(i.to_bytes(1, byteorder='big'), encoding='latin-1'))
    #codec = set(codec)
    codec.append('—')
    codec.append('“')
    codec.append('”')
    codec.append('€')
    return codec


class CalamariFile:
    def __init__(self, filename, mode='r', max_samples=MAX_SAMPLES):
        self.mode = mode
        if os.path.exists(filename):
            if mode not in {'r','r+','a'}:
                print('Invalid open mode')
                return None

            self.file = h5py.File(filename, mode)
            # find first non-empty entry
            self.sample_index = 0
            self.codec = create_codec()
            if mode == 'a':
                n = self.len()
                while self.sample_index < n:
                    if not len(self.file['images'][self.sample_index]):
                        break
                    self.sample_index += 1
        else:
            print('new file')
            self.file = h5py.File(filename, 'w')
            self.codec = create_codec()
            codec_data = [ord(c) for c in self.codec]
            self.file.create_dataset('codec',       data=codec_data)
            self.file.create_dataset('images',      (max_samples,),   dtype=pixel_type)
            self.file.create_dataset('images_dims', (max_samples, 2), dtype=dim_type)
            self.file.create_dataset('transcripts', (max_samples,),   dtype=string_type)
            self.sample_index = 0

    def write(self,image,text):
        if self.sample_index == self.len():
            print('Can\'t write. HDF5 file is full')
            return -1
        text_data = [self.codec.index(c) if c in self.codec else -1 for c in text]
        if len(text_data) == 0 or np.min(text_data) < 0:
            return -1
        if np.prod(image.shape) == 0:
            return -1
        image_data = image.astype(np.uint8).reshape(-1)
        self.file['transcripts'][self.sample_index] = text_data
        self.file['images'][self.sample_index]      = image_data
        self.file['images_dims'][self.sample_index] = [int(d) for d in image.shape]
        self.sample_index += 1
        return 0

    def set_image(self,i,image):
        image_data = image.astype(np.uint8).reshape(-1)
        self.file['images'][i]      = image_data
        self.file['images_dims'][i] = [int(d) for d in image.shape]

    def current_index(self):
        return self.sample_index

    def get_image(self,i):
        shape  = self.file['images_dims'][i]
        pixels = self.file['images'][i]
        return pixels.reshape(shape)

    def get_transcript(self,i):
        encoded_text = self.file['transcripts'][i]
        return ''.join(self.codec[c] for c in encoded_text)

    def set_transcript(self,i,text):
        encoded_text = [self.codec.index(c) for c in text]
        self.file['transcripts'][i] = encoded_text

    def len(self):
        return len(self.file['images'])

    def close(self):
        self.file.close()


if __name__ == "__main__":
    print('comienzo')

    cf = CalamariFile('prueba.h5',5,10)
    print('contexto HDF5')
    cf.write(np.zeros((10, 10), dtype=np.uint8), "test")
    cf.write(np.zeros((10, 15), dtype=np.uint8), "adsfsdfasd")
    cf.write(np.zeros((1, 10), dtype=np.uint8), "te345")
    print('afuera del contexto')
    cf.close()
    cf = CalamariFile('prueba.h5')
    print('number of records',cf.len())
    cf.close()


# Use --dataset HDF5 to switch mode.
#
# The content of a hd5-is:
#
#     images: list of raw images                                      SUPONGO QUE SON LOS BYTES DE LOS PIXELES
#     images_dims: the shape of the images (numpy arrays)             ESTO CASI SEGURO QUE ES LO QUE PUSE
#     codec: integer mapping to decode the transcripts (ASCII)     ESTO ES UNA LISTA CON EL CODEC (ASCII, UTF-8, etc.) DE CADA TRANSCRIPCION
#     transcripts: list of encoded transcripts using the codec  ESTE CASI SEGURO QUE ESTA BIEN
#
