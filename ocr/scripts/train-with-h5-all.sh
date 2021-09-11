#!/bin/bash
calamari-train --dataset HDF5 --use_train_as_val --num_threads 8 --samples_per_epoch 10000 --train_data_on_the_fly --files 90ref.h5 80ref.h5 luisa.h5
# CER = 24%
#calamari-train --files=train/*.tif --validation val/*.tif --samples_per_epoch 4000  --num_threads 4
#calamari-train --dataset FILE --files ${1}/*tif --use_train_as_val --num_threads 6 --samples_per_epoch 2000
# CER = 25%
#calamari-train --files=train/*.tif --validation val/*.tif --samples_per_epoch 10000  --num_threads 4 --line_height 64
#calamari-train --files=train/*.tif --validation val/*.tif --samples_per_epoch 1000  --num_threads 4 --line_height 64


