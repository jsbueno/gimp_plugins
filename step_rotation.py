#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gimpfu import *
from math import pi

def remove_layer_alpha (img, layer):
    visibility = layer.visible
    layer.visible = 1
    if not pdb.gimp_drawable_has_alpha (layer):
        return
    width = layer.width
    height = layer.height
    offx, offy = layer.offsets

    new_layer = pdb.gimp_layer_new (img, width, height,
                        layer.type,
                        "de_alpha_temp",100, NORMAL_MODE)
    position = img.layers.index (layer)
    pdb.gimp_image_add_layer (img, new_layer, position)

    pdb.gimp_image_lower_layer (img, new_layer)
    new_layer.set_offsets (offx, offy)
    pdb.gimp_drawable_fill (new_layer, BACKGROUND_FILL)
    new_layer.visible = 1
    combined_layer = pdb.gimp_image_merge_down (img, layer, CLIP_TO_IMAGE)
    combined_layer.visible = visibility
    return combined_layer

def step_rotation (img, drw, layers, angle_span, remove_alpha):
    global layers_list
    pdb.gimp_image_undo_group_start(img)

    if layers <= 1:
        return
    angle_step = float (angle_span) / ( layers -1)
    angle = 0
    old_drw = drw
    for i in xrange (1, layers):
        new_drw = drw.copy ()
        img.add_layer (new_drw, img.layers.index (old_drw) )
        angle += angle_step
        pdb.gimp_drawable_transform_rotate_default (new_drw,
                                               angle * pi / 180,
                                               True,
                                               0,0,
                                               True,
                                               False)
        if (remove_alpha):
            new_drw = remove_layer_alpha (img, new_drw)
        new_drw.name = drw.name + " %4.1f°" % angle
        old_drw = new_drw

    pdb.gimp_image_undo_group_end (img)
    pdb.gimp_displays_flush ()







register(
         "step_rotation",
         "Duplicate a layer and rotate each copy by a varying ammount",
         "",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2003",
         "<Image>/Python-Fu/Step Rotation",
         "*",
         [
                (PF_INT, "layers", "Number of Copies", 10),
                (PF_FLOAT, "angle_span", "Total angle span of rotation", 360),
                (PF_BOOL, "romove_alpha", "Replace edge transp with background colors", False)
         ],
         [],
         step_rotation)

main()
