#!/usr/bin/env python

from gimpfu import *
from math import floor

def grad_blur (img, drawable, left_ammount, right_ammount, divisions):

    width=pdb.gimp_image_width (img)
    height=pdb.gimp_image_height (img)

    slice_width=floor(float(width)/divisions)+1
    slice_pixelize=float(right_ammount-left_ammount)/divisions

    for i in xrange (divisions):
        pdb.gimp_rect_select (img,floor (i*slice_width), 0,slice_width, height,
                              2,0,0)
        ammount=left_ammount+i*slice_pixelize
        #pdb.gimp_rect_select (0,floor (i*slice_width), 0,slice_width, height,2,0,0)
        pdb.gimp_selection_feather (img, ammount)
        pdb.plug_in_gauss_iir2 (img, drawable,ammount, ammount)





register(
         "grad_blur",
         "Horizontal Gradient Blurrer",
         "Horizontal Gradient Blurrer - honest",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2003",
         "<Image>/Python-Fu/Alchemy/Gradient Blur",
         "*",
         [
                (PF_INT, "left_ammount", "radius of blur at left", 1),
                (PF_INT, "right_ammount", "radius of blur at right", 10),
                (PF_INT, "divisions", "how many divisions on the image", 10),

         ],
         [],
         grad_blur)

main()
