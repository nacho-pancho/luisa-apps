#!/usr/bin/env python3
import os
import sys
import subprocess
import tkinter as tk
import tkinter.font as tkfont
import argparse
from PIL import Image,ImageTk,ImageDraw


#==============================================================================

index = 0
nimages = 0 
data = list()
tkimg = None
tktxt = None
tkentry = None
tknote = None

class datum:
    def __init__(self,imgname,text):
        self.imgname  = imgname
        self.text     = text
        self.cropbox  = None
        self.oldtext  = text
        self.__deleted  = False

    def deleted(self):
        return self.__deleted

    def delete(self):
        self.__deleted = True

    def undelete(self):
        self.__deleted = False

    def modify(self,newtext):
        print('oldtext',self.text,'newtext',newtext)
        self.text = newtext

    def modified(self):
        return self.oldtext != self.text

    def cropped(self):
        return self.cropbox is not None

    def crop(self,left,top,right,bottom):
        self.cropbox = (left,top,right,bottom)

    def uncrop(self):
        self.cropbox = None

    def revert(self):
        if self.oldtext is not None:
            self.text     = self.oldtext
        self.oldtext  = None
        self.crobpox  = None


#==============================================================================

def key_handler(e):
    if e.keysym == 'Up':
        go_back(1)
    elif e.keysym == 'Down':
        go_forward(1)
    elif e.keysym == 'Prior':
        go_back(50)
    elif e.keysym == 'Next':
        go_forward(50)
    #elif e.keysym == 'Home':
    #    go_back(1000000)
    #elif e.keysym == 'End':
    #    go_forward(1000000)
    elif e.keysym == 'F6':
        undelete_entry()
    elif e.keysym == 'F4':
        delete_entry()
    elif e.keysym == 'F2':
        apply()
    elif e.keysym == 'F8':
        revert_entry()
    elif e.keysym == 'F10':
        quit()
    elif e.keysym == 'Escape':
        quit()

#==============================================================================

def go_forward(howmuch):
    global index
    global nimages
    index += howmuch
    if index >= nimages:
        index = nimages -1
    refresh()

#==============================================================================

def go_back(howmuch):
    global index
    index -= howmuch
    if index < 0:
        index = 0
    refresh()

#==============================================================================

def delete_entry():
    global data,index
    data[index].delete()
    refresh()

#==============================================================================

def undelete_entry():
    global data,index
    data[index].undelete()
    refresh()

#==============================================================================

def revert_entry():
    global data,index
    data[index].revert()
    data[index].uncrop()
    refresh()

#==============================================================================

def text_down(ev):
    global data,index
    global tkentry
    pass

#==============================================================================

def text_up(ev):
    global data,index,tkentry
    data[index].modify(tkentry.get())
    refresh()

#==============================================================================

corner_1_x = None
corner_1_y = None
corner_2_x = None
corner_2_y = None

def begin_drag(ev):
    global corner_1_x,corner_1_y
    corner_1_x = ev.x
    corner_1_y = ev.y


#==============================================================================

def while_drag(ev):
    global corner_1_x,corner_1_y,corner_2_x,corner_2_y
    if corner_1_x is None:
        return
    corner_2_x = ev.x
    corner_2_y = ev.y
    refresh()

#==============================================================================

def end_drag(ev):
    global data, index
    global corner_1_x,corner_1_y,corner_2_x,corner_2_y
    corner_2_x = ev.x
    corner_2_y = ev.y
    if corner_1_x < corner_2_x:
        left  = corner_1_x
        right = corner_2_x
    else:
        left  = corner_2_x
        right = corner_1_x

    if corner_1_y < corner_2_y:
        top    = corner_1_y
        bottom = corner_2_y
    else:
        top    = corner_2_y
        bottom = corner_1_y
    corner_1_x = None
    corner_1_y = None
    corner_2_x = None
    corner_2_y = None
    data[index].crop(left,top,right,bottom)
    refresh()

#==============================================================================


def refresh():
    global tkimg,tktxt,tkentry
    global corner_1_x,corner_1_y,corner_2_x,corner_2_y
    img = Image.open(data[index].imgname)
    #
    # show cropbox, if any
    #
    if data[index].cropped():
        img  = img.convert("RGB")
        draw = ImageDraw.Draw(img,"RGB")
        left,top,right,bottom = data[index].cropbox
        top = 0
        w,h = img.size
        draw.rectangle([0,0,left,h],fill=(20,100,200),width=2)
        draw.rectangle([right,0,w,h],fill=(20,100,200),width=2)
        #draw.rectangle([left,top,right,bottom],fill=None,outline=(20,100,200),width=3)
        #
        # hack: here is the only place where I can access the original image size
        #
        if data[index].cropbox[1] != 0 or data[index].cropbox[3] != h:
            data[index].cropbox = (left,0,right,h)
    elif corner_1_x is not None:
        draw = ImageDraw.Draw(img)
        w,h = img.size
        left = min(corner_1_x,corner_2_x)
        right = max(corner_1_x,corner_2_x)
        #draw.rectangle([left,0,right,h],fill=None,outline=100,width=2)
        draw.rectangle([0,0,left,h],fill=(160),width=2)
        draw.rectangle([right,0,w,h],fill=(160),width=2)
    img = ImageTk.PhotoImage(img)
    tkimg.image    = img
    tkimg['image'] = img
    tktxt.set(data[index].text)
    tkentry['textvariable'] = tktxt
    #
    # text is name of image
    #
    _,basename = os.path.split(data[index].imgname)
    newtext = f'{basename} ({index:6d}/{nimages:6d})'

    if data[index].deleted():
        tknote['text'] = newtext + ' **deleted**'
        tknote['fg'] = 'red'
    else:
        tknote['text'] = newtext
        tknote['fg'] = 'green'
        if data[index].modified():
            tknote['text'] = newtext + ' **modified**'
            tknote['fg'] = 'brown'
            tkentry['fg'] = 'brown'
        else:
            tkentry['fg'] = 'black'
        if data[index].cropped():
            tknote['fg'] = 'orange'
            tknote['text'] = tknote['text'] + ' **cropped**'
    return



#==============================================================================

def apply():
    bitacora = open('bitacora.txt','w')
    for i,d in enumerate(data):
        #ipath,txt,deleted,modified = d
        path, iname = os.path.split(d.imgname)
        basename, ext = os.path.splitext(iname)
        tname = os.path.join(din, basename + '.gt.txt')
        if d.deleted():
            print('item ',i,'will be deleted')
            print('path',d.imgname,'text',d.text)
            # BACKUP
            ibak = os.path.join(dout, iname)
            tbak = os.path.join(dout, basename + '.gt.txt')
            subprocess.run(['cp',d.imgname,ibak])
            subprocess.run(['cp', tname, tbak])
            # DELETE
            subprocess.run(['rm','-f',d.imgname])
            subprocess.run(['rm','-f',tname])
            print(i,'D',file=bitacora)

        else:
            changed = False
            if d.modified():
                changed = True
                print('item',i,'will be modified')
                print('path', d.imgname, 'old text',d.oldtext, 'new text', d.text)
                #
                # BACKUP
                #
                ibak = os.path.join(dout, iname)
                tbak = os.path.join(dout, basename + '.gt.txt')
                subprocess.run(['cp',d.imgname,ibak])
                subprocess.run(['cp', tname, tbak])
                # MODIFY
                with open(tname,'w') as f:
                    print(d.text,file=f)
                #
                # CROP 
                #
            if d.cropped():
                changed = True
                print('item',i,' will be cropped to ',d.cropbox)
                #
                # BACKUP
                #
                ibak = os.path.join(dout, iname)
                tbak = os.path.join(dout, basename + '.gt.txt')
                subprocess.run(['cp',d.imgname,ibak])
                subprocess.run(['cp', tname, tbak])
                #
                # SAVE CROPPED
                #
                img = Image.open(d.imgname)
                img = img.crop(d.cropbox)
                img.save(d.imgname,compression='ccitt_group4')
            if changed:
                print(i,'M',file=bitacora)
            else:
                print(i,'U',file=bitacora)
    bitacora.close()
    exit(0)


#==============================================================================


def quit():
    print('quit ')
    exit(0)


#==============================================================================


if __name__ == '__main__':
    print('VERSION 2')
    ap = argparse.ArgumentParser()
    ap.add_argument("--font_size", type=int, default=20,
                    help="font size")
    ap.add_argument("--img_ext", type=str, default="gif",
                    help="image format extension")
    ap.add_argument("--text_ext", type=str, default="gt.txt",
                    help="ground truth text file extension")
    ap.add_argument("--bakdir", type=str, default="",
                    help="backup dir (defaults to 'backup' under source dir)")
    ap.add_argument("indir", type=str, help="source dir")
    args = vars(ap.parse_args())
    ext = args["img_ext"]
    txext = args["text_ext"]
    din = args["indir"]
    if len(args["bakdir"]):
        dout = args["bakdir"]
    else:
        dout = os.path.join(din,'backup')
    if not os.path.exists(dout):
        os.makedirs(dout,exist_ok=True)

    images = sorted([f for f in os.listdir(din) if os.path.isfile(os.path.join(din, f)) and f[-3:].lower() == ext ])
    index = 0
    nimages = len(images)
    if nimages == 0:
        print('no images found')
        exit(1)
    for i,f in enumerate(images):
        imgfname = os.path.join(din,f)
        txtfname = os.path.join(din,f[:-3]+'gt.txt')
        with open(txtfname,'r') as f:
            txt = f.readline().strip()
        # image name, text, to be deleted, to be modified
        data.append(datum(imgfname,txt)) 
        if i > 0 and not i % 1000:
            print(f'{i:08d}/{nimages:08d}')
    #
    # interface
    #
    win = tk.Tk()
    win.bind('<KeyPress>',key_handler)

    txtfont = tkfont.Font(family="Helvetica",size=args["font_size"])
    tkentry = tk.Entry(win,font=txtfont,width=80,borderwidth=5)
    tktxt   = tk.StringVar(win)
    tktxt.set(data[index].text)
    tkentry['textvariable'] = tktxt
    tkentry.bind("<KeyPress>",text_down)
    tkentry.bind("<KeyRelease>",text_up)
    tkentry['bg'] = 'white'
    tkentry.pack()

    img = Image.open(data[index].imgname)
    img = ImageTk.PhotoImage(img)
    tkimg = tk.Label(win,image=img)
    tkimg.bind("<Button>",begin_drag)
    tkimg.bind("<ButtonRelease>",end_drag)
    tkimg.bind("<Motion>",while_drag)
    tkimg.image = img
    tkimg.pack()

    _,basename = os.path.split(data[index].imgname)
    tknote = tk.Label(win,text=f'{basename} ( {index:6d} / {nimages:6d} ) ',font=txtfont)
    tknote.pack()
    refresh()

    win.mainloop()


#==============================================================================

