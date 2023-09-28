#!/usr/bin/env python

from gimpfu import *

# (c) 2007 by Joao S. O. Bueno Calligaris 
# V 1.1

# License: GPLv2 or later

def copypaste (img, drw):
    """
    Performs a copy on the active layer, an paste on all linked layers preserving original offset and mask.
    """
    img.undo_group_start ()
    x, y = tuple (pdb.gimp_selection_bounds (img)[1:3])
    selection = pdb.gimp_selection_save (img)
    #edit_copy returns false if nothing was copied.
    if pdb.gimp_edit_copy (drw):
        if hasattr (drw, "mask") and drw.mask:
            mask_data = pdb.gimp_edit_named_copy (drw.mask, "%s-mask-copy" % drw.name)
        else:
            mask_data = None
        
        # find target layers:
        for layer in img.layers:
            if layer.linked and layer != drw:
                if mask_data:
                    if not layer.mask:
                        layer.add_mask (
                            layer.create_mask (ADD_WHITE_MASK))
                    floating = pdb.gimp_edit_named_paste (layer.mask, mask_data, False)
                    floating.translate (x - floating.offsets[0], y - floating.offsets[1])
                    pdb.gimp_floating_sel_anchor (floating)
                floating = pdb.gimp_edit_paste (layer, False)
                floating.translate (x - floating.offsets[0], y - floating.offsets[1])
                pdb.gimp_floating_sel_anchor (floating)
                
    pdb.gimp_selection_load (selection)
    pdb.gimp_image_remove_channel (img, selection)
    if isinstance (drw, gimp.Layer):
        pdb.gimp_image_set_active_layer (img, drw)
    elif  drw.is_layer_mask:
        layer = pdb.gimp_layer_from_mask (drw)
        pdb.gimp_image_set_active_layer (img, layer)
        layer.edit_mask = True
    else:
        pdb.gimp_image_set_active_channel (img, drw)
    img.undo_group_end ()
    gimp.displays_flush ()

register(
         "copy_paste",
         "Copies form active layer, pastes on linked layers, preserves mask",
         copypaste.__doc__,
         "Joao S. O. Bueno",
         "(c) GPLv2 or later",
         "2007",
         "<Image>/Edit/Copy Paste with Mask",
         "*",
         [],
         [],
         copypaste)

main()
