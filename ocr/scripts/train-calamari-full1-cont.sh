#!/bin/bash
# use plain files (img+txt) for training
# 10% for validation, 90% for trainin
# do not load training data into memory
# dataset specified as a bunch of image files; txt files are inferre
# start with the weights from a previous net trained on the 80 and 90 quality percentiles of Tesseract outputs

calamari-train --dataset HDF5 \
	--num_threads 10 \
	--train_data_on_the_fly \
	--files /luisa/ocr/data/luisa-curados/full1/full1-train.h5 \
	--validation /luisa/ocr/data/luisa-curados/full1/full1-val.h5 \
	--weights ./best.ckpt.h5 $* 

# CER = 24%
#calamari-train --files=train/*.tif --validation val/*.tif --samples_per_epoch 4000  --num_threads 4
#calamari-train --dataset FILE --files ${1}/*tif --use_train_as_val --num_threads 6 --samples_per_epoch 2000
# CER = 25%
#calamari-train --files=train/*.tif --validation val/*.tif --samples_per_epoch 10000  --num_threads 4 --line_height 64
#calamari-train --files=train/*.tif --validation val/*.tif --samples_per_epoch 1000  --num_threads 4 --line_height 64
# CER 21%
# samples_per_epoch 1000 validation_split_ratio 0.2
#
# CER 18%
# 
# curados 8 bit, epoch = todo (~9000) split 0.2


