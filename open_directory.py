#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *
import os

def load_images_in_dir(image, drw, path):
    
    for filename in os.listdir(path):
        try:
            if filename.lower().split(".")[-1] in ("png", "jpg"):
                #import pdb as debug; debug.set_trace()
                image_id, layer_ids = pdb.gimp_file_load_layers(image,
                     os.path.join(path, filename))
                for id in layer_ids:
                    new_layer = gimp.Item.from_id(id)
                    pdb.gimp_image_add_layer(image, new_layer, 0)
        except Exception, error:
            print error
        


register(
        "open_images_in_dir",
        "Open all files in a directory",
        "Open all files in a directory",
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2012. Creative Commons Citation Needed license",
        "Open Images in Dir as Layers...",
        "*",
        [(PF_IMAGE, "image", "the image", None),
         (PF_DRAWABLE, "drw", "the drawable", None),
         (PF_DIRNAME,"path", "Directory to Open", "."),],
        [],
        load_images_in_dir,
        menu="<Image>/File/")

main()
