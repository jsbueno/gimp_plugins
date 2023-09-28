#!/usr/bin/env python

from gimpfu import *
from math import floor

def grad_squareficate (img, drawable, left_size, right_size, left_number, right_number,  divisions):

    pdb.gimp_image_undo_group_start (img)
    width=pdb.gimp_image_width (img)
    height=pdb.gimp_image_height (img)

    slice_width=floor(float(width)/divisions)+1
    slice_pixelize=float(right_size-left_size)/divisions
    if pdb.gimp_selection_is_empty(img):
        is_sel = False
        pdb.gimp_selection_all (img)
    else:
        is_sel = True
    selection = pdb.gimp_selection_save (img)
    for i in xrange (divisions):
        pdb.gimp_selection_load (selection)
        pdb.gimp_rect_select (img,floor (i*slice_width), 0,slice_width, height,
                              CHANNEL_OP_INTERSECT,0,0)
        ammount=left_size+i*slice_pixelize
        size = (i / float(divisions) * left_size + (divisions - i) / float(divisions) * right_size) 
        number = (i / float(divisions) * left_number + (divisions - i) / float(divisions) * right_number)

        pdb.python_fu_squarificate (img, drawable, number, size, size/ 5.0, 
                                    False, False, True, True)
    if is_sel:
        pdb.gimp_selection_load (selection)
    else:
        pdb.gimp_selection_none (img)
    pdb.gimp_image_undo_group_end (img)



register(
         "grad_squareficate",
         "Horizontal Gradient Squareficator",
         "Horizontal Gradient Sqaureficator - honest",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2005",
         "<Image>/Python-Fu/Alchemy/Gradient Squareficate",
         "*",
         [
                (PF_INT, "left_size", "square side at left", 10),
                (PF_INT, "right_size", "square side at right", 60),
                (PF_INT, "left_number", "how many squares on left", 100),
                (PF_INT, "right_number", "how many squares on right", 25),
                (PF_INT, "divisions", "how many divisions on the image", 10)
         ],
         [],
         grad_squareficate)

main()
