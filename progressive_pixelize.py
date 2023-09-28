#!/usr/bin/env python

from gimpfu import *
from math import floor

def grad_pixelize (img, drawable, left_ammount, right_ammount, divisions, test_text):

    width=pdb.gimp_image_width (img)
    height=pdb.gimp_image_height (img)
    print test_text
    slice_width=floor(float(width)/divisions)+1
    slice_pixelize=float(right_ammount-left_ammount)/divisions

    for i in xrange (divisions):
        pdb.gimp_rect_select (img,floor (i*slice_width), 0,slice_width, height,
                              2,0,0)
        ammount=left_ammount+i*slice_pixelize
        #pdb.gimp_rect_select (0,floor (i*slice_width), 0,slice_width, height,2,0,0)
        pdb.plug_in_pixelize2 (img, drawable,ammount, ammount)





register(
         "grad_pixelize",
         "Horizontal Gradient Pixelizer",
         "Horizontal Gradient Pixelizer - honest",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2003",
         "<Image>/Python-Fu/Alchemy/Gradient Pixelize",
         "*",
         [
                (PF_INT, "left_ammount", "ammount to pixelize at left", 1),
                (PF_INT, "right_ammount", "ammount to pixelize at right", 10),
                (PF_INT, "divisions", "how many divisions on the image", 10),
                (PF_TEXT, "test_text", "Text to test the PF_TEXT", "teste\ndeverdade")
         ],
         [],
         grad_pixelize)

main()
