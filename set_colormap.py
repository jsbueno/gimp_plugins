#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *
import random
from math import pi

def make_new_drw (img, x1, y1, x2, y2):
    #type_ = img.layers[0].type_with_alpha
    type_ = RGBA_IMAGE
    new_drw = pdb.gimp_layer_new (img, x2 - x1, y2 - y1, type_, "squarificate_tmp", 100, NORMAL_MODE)
    pdb.gimp_image_add_layer (img, new_drw, -1)
    pdb.gimp_layer_set_offsets (new_drw, x1, y1)
    return new_drw

def read_color_array(palette):
        #pdb.gimp_progress_init ("Reading Palette", -1)
        num_colors = pdb.gimp_palette_get_info (palette)
        color_array = []
        for i in xrange (num_colors):
            color_array.append  (pdb.gimp_palette_entry_get_color (palette, i))
            if not i % 32:
                pass
                #pdb.gimp_progress_update (float (i) / num_colors)
        return color_array
        
def set_colormap (img,drw, palette):
    pdb.gimp_image_undo_group_start(img)
    #pdb.gimp_progress_init("Setting Color Map", -1)
    if (
        img.base_type == INDEXED
       ):
        color_array = read_color_array (palette)
        raw_color_bytes = []
        for i in xrange (len(color_array)):
            for j in (0,1,2):
                raw_color_bytes.append (color_array[i][j])
        pdb.gimp_image_set_cmap (img, len(raw_color_bytes), raw_color_bytes)        
    else:
        
        
        selection, x1, y1, x2, y2 = pdb.gimp_selection_bounds (img)
        
        if not selection:
            x1 = y1 = 0
            x2 = img.width
            y2 = img.height
        
        work_img = pdb.gimp_image_new (x2 - x1, y2 - y1, 0)
        ox1 = x1
        oy1 = y1
        x1 = y1 = 0
        x2 = x2 - ox1
        y2 = y2 - oy1
    
        pdb.gimp_image_undo_freeze (work_img)
        work_drw = make_new_drw (work_img, x1, y1, x2, y2)
        pdb.gimp_edit_copy (drw)
        floating_sel = pdb.gimp_edit_paste (work_drw,  0)
        pdb.gimp_floating_sel_anchor (floating_sel)
        
        if work_img.base_type != GRAY:
            pdb.gimp_image_convert_grayscale (work_img)
            pdb.gimp_levels_auto (work_drw)
        pdb.gimp_image_convert_rgb (work_img)
            
        complete = 0.0
        
        color_array = read_color_array (palette)
        num_colors = len(color_array)
        
        if num_colors != 256:
            colors_per_entry = 256.0/ num_colors
            tmp_color_array = []
            j = counter = 0
            #pdb.gimp_progress_init ("Smurfing Out Color Numbers", -1)
            for i in xrange (256):
                tmp_color_array.append (color_array[j])
                counter += 1
                if counter >= colors_per_entry:
                    #compensate somewhat for palettes with more than 256 colors.
                    #it will still be buggy.
                    j += int (counter / colors_per_entry)
                    counter = 0
                if not i % 32:
                    pass
                    #pdb.gimp_progress_update (i / 256.0)
            color_array = tmp_color_array
        
            
        #pdb.gimp_progress_init ("Preparing Curve Arrays", -1)
        red= [0] * 256
        green = [0] * 256
        blue = [0] * 256
        alpha = [0] * 256
        for i in xrange (256):
            red[i], green[i], blue[i], alpha[i] = color_array [i]
            if not i % 32:
                pass
                #pdb.gimp_progress_update (i / 256.0)
        #pdb.gimp_progress_init ("Colorifying", -1)
        pdb.gimp_curves_explicit (work_drw, HISTOGRAM_RED, 256, red)
        #pdb.gimp_progress_update (1 / 3.0)
        pdb.gimp_curves_explicit (work_drw, HISTOGRAM_GREEN, 256, green)
        #pdb.gimp_progress_update (2 / 3.0)
        pdb.gimp_curves_explicit (work_drw, HISTOGRAM_BLUE, 256, blue)
        # check if working drw has alpha channel, if so why not?
        #pdb.gimp_curves_explicit (work_drw, HISTOGRAM_ALPHA, 256, alpha)
        #pdb.gimp_progress_update (1.0)
        #if work_img.base_type == INDEXED:
        #    pdb.gimp_image_convert_grayscale (img)
        if work_img.base_type == GRAY:
            pdb.gimp_image_convert_indexed (img, FSLOWBLEED_DITTER, 
                                            CUSTOM_PALETTE, 0, 1, 0, palette)
            pdb.gimp_image_convert_indexed (work_img, NO_DITTER, 
                                            CUSTOM_PALETTE, 0, 1, 0, palette)
                                            
        try:
            pdb.gimp_image_undo_thaw (work_img)
            pdb.gimp_edit_copy (work_img.layers[0])
            
            floating_sel = pdb.gimp_edit_paste (drw,  1)
            pdb.gimp_floating_sel_anchor (floating_sel)
            pdb.gimp_image_delete (work_img)
        
            pdb.gimp_displays_flush ()
        except Exception, error:
            print error
    pdb.gimp_image_undo_group_end (img)

    
register(
        "set_colormap",
        "Set a palette as colormap for a drawable",
        "set_colormap (img, drw, pallete) -> None",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2004",
        "<Image>/Python-Fu/Set_color_map",
        "*",
        [(PF_PALETTE, "palette", "palette to use",""),
        ],     
        [],
        set_colormap)
main ()