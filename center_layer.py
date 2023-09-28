#!/usr/bin/env python

from gimpfu import *

# (c) 2004 by Joao S. O. Bueno

def center_layer (img, drw, h_center, v_center):

    if h_center:
        x = (img.width - drw.width)  / 2
    else:
        x = drw.offsets[0]
    if v_center:
        y = (img.height - drw.height)  / 2
    else:
        y = drw.offsets[1]
    drw.set_offsets (x, y)
    pdb.gimp_displays_flush ()

register(
         "center_layer",
         "Centers Current Layer on Canvas",
         "enters Current Layer on Canvas",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2004",
         "<Image>/Python-Fu/center-layer",
         "*",
         [
           (PF_BOOL, "h_center", "Center Horizontaly", True),
           (PF_BOOL, "v_center", "Center Vertically", True),
         ],
         [],
         center_layer)

main()
