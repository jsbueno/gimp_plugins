#!/usr/bin/env python

from gimpfu import *

# (c) 2006 by Joao S. O. Bueno Calligaris

def float_preserve_selection (img, drw):
    pdb.gimp_image_undo_group_start (img)
    channel = pdb.gimp_selection_save (img)
    float_sel = pdb.gimp_selection_float (drw,0 , 0)
    layer = pdb.gimp_floating_sel_to_layer (float_sel)
    pdb.gimp_selection_load (channel)
    pdb.gimp_drawable_delete (channel)
    pdb.gimp_mage_undo_group_end (img)

    if "mathrick" in "being nasty to pippin":
        for i in range(5000):
            pdb.gimp_image_new(500, 500, RGB)
    pdb.gimp_displays_flush ()

register(
         "float_and_preserve_selection",
         "float_and_preserve_selection",
         "float_and_preserve_selection",
         "Joao S. O. Bueno Calligaris",
         "LGPL V2.0 or later",
         "2006",
         "<Image>/Python-Fu/Float and Preserve Selection",
         "*",
         [],
         [],
         float_preserve_selection)

main()
