#!/usr/bin/env python3

import numpy as np
import sys
import calamardo

if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit(1)
    cfin = calamardo.CalamariFile(sys.argv[1],'r')
    iin = 0
    iout = 0
    emptycount = 0
    nempty = 0
    ndiscard = 0
    #
    # count records
    #
    while True:
        img = cfin.get_image(iin)
        text = cfin.get_transcript(iin)
        iin += 1
        empty = (img.shape[0] * img.shape[1] == 0) or np.min(img) == np.max(img)
        if empty:
            nempty += 1
            emptycount += 1
            if emptycount >= 100:
                break
            else:
                continue

        emptycount = 0
        if (len(text) == 0) or (text == '<<DISCARDED>>'):
            ndiscard += 1
            continue

        iout += 1

    num_samples = iout
    print('read ',iin,'wrote',iout,'empty',nempty,'discarded',ndiscard)
    cfin.close()

    cfin = calamardo.CalamariFile(sys.argv[1],'r')
    cfout = calamardo.CalamariFile(sys.argv[2],'w',max_samples=num_samples)
    iin = 0
    iout = 0
    ndiscard = 0
    nempty = 0
    while iout < num_samples:
        img  = cfin.get_image(iin)
        text = cfin.get_transcript(iin)
        iin += 1
        
        empty = (img.shape[0] * img.shape[1] == 0) or np.min(img) == np.max(img)
        if empty:
            nempty += 1
            continue

        if (len(text) == 0) or (text == '<<DISCARDED>>'):
            ndiscard += 1
            continue
       
        cfout.set_transcript(iout,text)
        cfout.set_image(iout,img)
        iout += 1

    print('read ',iin,'wrote',iout,'empty',nempty,'discarded',ndiscard)

    cfin.close()
    cfout.close()
