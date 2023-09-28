#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *

def dup_visible_layers(img, drw, merge):
    pdb.gimp_image_undo_group_start (img)
    new_layers = []
    
    for layer in img.layers:
        if layer.visible:
            new_layers.append (layer.copy())
            layer.visible = 0
    count = 0
    for layer in new_layers:
        img.add_layer (layer, count)
        count += 1
    if merge:
        pdb.gimp_image_merge_visible_layers (img, EXPAND_AS_NECESSARY)
   
    pdb.gimp_image_undo_group_end (img)
    
    
register(
        "dup_visible_layers",
        "Merge All Visible Layers, preserving the originals ",
        "dup_visible_layers (img, drw) -> None",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2004",
        "<Image>/Python-Fu/Dup Visible Layers",
        "*",
        [(PF_TOGGLE, "merge", "Merge Duplicated Layers?", True)],      
        [],
        dup_visible_layers)
main ()