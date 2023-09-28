#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *

def save_flat_copy (img, drw):
    #there seens to be a problem with progress init in cvs head as 04-11-2006. Will check later.
    #pdb.gimp_progress_init ("saving flattened image", -1)
    pdb.gimp_progress_update (0.2)
    n_img = pdb.gimp_image_duplicate (img)
    filename = pdb.gimp_image_get_filename (img)
    pdb.gimp_image_set_filename (n_img, filename)
    name =  pdb.gimp_image_get_name (img)
    drw = pdb.gimp_image_flatten (n_img)
    pdb.gimp_progress_update (0.5)
    pdb.gimp_file_save (n_img, drw, filename, name)
    #this removes only the memory copy of the duplicate image
    pdb.gimp_progress_update (1.0)

    pdb.gimp_image_delete (n_img)
    #mark original image as "saved"
    pdb.gimp_image_clean_all (img)


register(
        "save_flat_copy",
        "Saves a flattentd version of the image, no questions asked",
        "saves the image with the current filename, avoiding the export dialog",
        "Joao S. O. Bueno Calligaris",
        "GPL applies",
        "2006",
        "<Image>/Filters/Work/Save Flat Image",
        "*",
        [],
        [],
        save_flat_copy)
main ()