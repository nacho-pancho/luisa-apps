# Applications and tools for the LUISA crowdsourcing transcription system

LUISA was originally developed as an online crowdsourced document transcription tool.
The idea is to transcribe in this way those documents that are too degraded for a commercial,
off-the-shelf optical character recognition systems (OCR) to produce a good result.

In the online system, users are fed with contigous blocks (words) of text, and they are asked to write 
the corresponding text and submit it back.

The tools in this repository deal with many tasks that need to be performed before and after the
manual transcription has taken place. 

With time, other _satellite_ applications besides automatic transcription were added.

Currently, the tools are arranged in the following modules:

*   clustering
*   degradacion
*   dictionaries
*   hashing
*   hdf5
*   ocr
*   postprocessing
*   preprocessing
*   scores
*   stamps
*   watermark

Below, we describe the overall process, and the modules (apps) involved. The other modules are described
in a separate section at the end of this document.

## Preamble: input data

The data that we process in LUISA consists of a large body (millions) of scanned pages; we have no access
to the original, physical pages. What we do have, is their digitized versions, which are available to us
only as binary images (black-white, no grayscale or color) of about 300-400 dpi. The images are rather large, 
about 15 megapixels each.

These scanned images were not produced from the documents, but from microfilmed versions of the original documents, through
a commercial microfilm scanner. Also, many of the original documents are severely degraded.

In summary, many of the images we have are of very bad quality: noisy, low contrast, grainy, etc. All these features make
commercial OCRs fail quite badly on them.

On the other hand, many images are in very good readability condition and can indeed be processed by an OCR.

Finally, we have an advantage with respect to other document transcription efforts: the layout of the documents is usually
very simple. There are no complicated multi-column documents, no frames or drawings, as one would see on a newspaper.
The exception is in those files which are scanned IDs or passports. However, we are not dealing with these now, and they make
up a very small portion of the corpus.

## Preprocessing

The following steps, included in the `preprocessing` module, perform those operations that are typically applied first
in an OCR pipeline.

*   denoising
*   blob / dark region removal
*   alignment (deskewing, straightening). The idea is to obtain an image where the text lines are perfectly horizontal
*   reduce images (optional): in some cases it may be a good idea to reduce the images and make them grayscale (little info is lost)
*   text line segmentation: detect and frame each line of text in the document
*   word (block) segmentation:  break each line of text into separate words

##  Readabilty assessment

In order to decide whether to send a given image to the crowdsourcing system LUISA, or to process it with an OCR,
we compute a readability score. The module `scores` contains code for computing this score on each image, as well as for training its parameters
using calibration data generated by volunteers.

## Postprocessing

Recall that users perform manual transcription one word at a time.
Thus, when a page is finished, the input obtained from users needs to be curated and assembled back into pages.

The main purpose of the `postprocessing` module is this.

During this process, bad results such as obvious errors, degenerate blocks (sometimes the segmentation produces _garbage_ blocks instead
of valid words),  unreadable outputs (also, some words are so badly distorted that not even people can read them), etc., are pruned.

Also, as a final step, advanced Natural Language Processing tools and methods are applied to further enhance the transcribed texts.


## Optical Character Recognition

The speed at which manual transcriptions are performed is quite slow for the volume of data that we have, and off-the-shelf
OCRs can only process about 20% of the files.

On the other hand, even if relatively small compared to the would corpus,  the number of manually transcribed pages that we have
is large enough (actually, quite large!) for training an OCR especifically to our data. 

We have been experimenting with this idea with very good results, using the open source Calamari OCR. This OCR is not really
aimed to the end user, but more as a module to be integrated (just as some of our tools) in the large software ecosystem 
developed by the people of the Berlin State Library.

Now, in order to produce good quality training data for the OCR, a much more aggresive pruning and cleansing is needed on the output
obtained from LUISA, for very different reasons. 

In summary, the `ocr` module contains tools for gathering the output of LUISA, discarding any data that might not correspond *exactly* with the
images (this is not really an issue for humans or Knowledge Extraction tools to be applied afterwards, but it is for training OCRs).

Also, the data is converted to a format that is suitable as an input to Calamari (HDF5 files with a particular inner structure).


# Supporting modules

## Dictionaries

The words contained in the Archive, and the language used therein, are often very different when compared to regular Spanish.
A lot of the useful information is made up by people's last names, which in Uruguay are very diverse, and have mutated due to
different spellings used in the past when immigrants came. Finally, many acronyms, codewords, etc., used by the Military have
to be included.

Therefore, to determine wheter some word is correctly spelled or not, it is important to have a domain-specific dictionary.
The module `dictionaries` includes dictionaries, words, names, acronyms, etc., gathered from standard sources or by hand, and compiles
them into two word lists: _words_ and _names_, which are then used by text correction tools in other modules.

## Hashing

The original file names, their locations, etc., are not a reliable method for identification. Also, we need to keep track of any
modifications, and defend ourselves from possible forgeries. Thus, it is fundamental to have a stable and standard method for mapping
the individual images that make up the corpus into unique identifiers. This module handles the computation and bookkeeping of hashes
used througout the project.

## Watermarking

As the documents are of sensitive nature, and the continuity of the project relies on our proper handling of them (in particular,
we must be able to determine the source of possible leaks), we perform a robust watermarking on the images.
This module implements several watermarking strategies.

## HDF5

The HDF5 is a compact file format for storing large datasets developed by Google. The Calamari system uses it as its main input format.
Furthermore, HDF5 is very flexible and allows an arbitrary organization of the data within the file.
Therefore, we need to be able to read and write this format using the specific organization defined by the Calamari team.
This is the purpose of the `hdf5` module.

# Satellite projects

Below we list other projects that are loosely part of LUISA, although they do not deal directly with document transcription.

## Stamp detection

One of the tasks that we set out to perform is to identify which stamps (rubber stamps) appear in different documents. Such information
is invaluable to determine the source and administrative route of the original documents. 

## Clustering

The aim of this subproject is to identify the _type_  of different documents: whether they are letters, tables, scanned IDs or passports, etc.

## Degradation

This subproject contains a simulator meant for data augmentation. The idea is to produce artificial training data by emulating the degradation
process that takes place from a pristine, typewritten document, down to the binary scanned image. It is not currently used.


