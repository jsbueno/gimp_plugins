#!/usr/bin/env python

from gimpfu import *
from math import floor

def de_alpha_one_layer (img,layer, color, uniform_sizes):
    global layers_list

    visibility = layer.visible
    layer.visible = 1
    if not pdb.gimp_drawable_has_alpha (layer):
        return
    type_ = pdb.gimp_drawable_type (layer)
    if uniform_sizes:
        width = img.width
        height = img.height
        offx, offy = (0,0)
        merge_mode = CLIP_TO_IMAGE
    else:
        width = layer.width
        height = layer.height
        offx, offy = layer.offsets
        merge_mode = EXPAND_AS_NECESSARY

    new_layer = pdb.gimp_layer_new (img, width, height,
                        layer.type,
                        "de_alpha_temp",100, NORMAL_MODE)
    #position = len (layers_list) - layers_list.index (layer)
    position = layers_list.index (layer)
    pdb.gimp_image_add_layer (img, new_layer, position)

    pdb.gimp_image_lower_layer (img, new_layer)
    new_layer.set_offsets (offx, offy)

    pdb.gimp_drawable_fill (new_layer, FOREGROUND_FILL)

    new_layer.visible = 1
    combined_layer = pdb.gimp_image_merge_visible_layers (img, merge_mode)

    combined_layer.visible = visibility


def de_alpha (img, drawable, de_alpha_all_layers, color, uniform_sizes):
    global layers_list
    img.undo_freeze()
    visible_states = []
    #img.layers will change during interations so:
    layers_list = img.layers
    current_fg = gimp.get_foreground()
    gimp.set_foreground (color)
    for layer in layers_list:
        visible_states.append (layer.visible)
        layer.visible=0
    if not de_alpha_all_layers:
        de_alpha_one_layer (img, drawable, uniform_sizes)
    else:
        for layer in layers_list:
            visible_states.append (layer.visible)
            layer.visible=0
        for layer in layers_list:
            de_alpha_one_layer (img,layer, color, uniform_sizes)
        for i in range (len(layers_list)):
            img.layers[i].visible = visible_states[i]
    gimp.set_foreground (current_fg)
    img.undo_thaw()
    pdb.gimp_displays_flush ()







register(
         "de_alpha",
         "Alpha Remover for All Layers",
         "Remove Alpha channel from all layers - use for creating animations or brushes.",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2003",
         "<Image>/Python-Fu/de-alpha",
         "*",
         [
                (PF_BOOL, "de_alpha_all_layers", "Whether to work on current layer or all layers", 1),
                (PF_COLOR, "color", "Color to apply to background", (255,255,255)),
                (PF_BOOL, "uniform_sizes", "Make layer sizes equal Image size", 0)

         ],
         [],
         de_alpha)

main()
