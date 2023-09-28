#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *
import math


        
        
def shape_warp(img, destination_drw, source_drw, source_shape, destination_shape, offset_angle = 0):
    pdb.gimp_image_undo_group_start(img)
    
    old_color = pdb.gimp_context_get_foreground ()
    old_selection = pdb.gimp_selection_save (img)
     
    pdb.gimp_context_set_foreground ((0,0,0))
    pdb.gimp_selection_none (img)
    
    source_offsets, source_shape = prepare_shape (source_shape)
    destination_offsets, destination_shape = prepare_shape (destination_shape)
    
    intermediate_drw = pdb.gimp_layer_new (img, source_shape.width * 2, 
                                           source_shape.height * 2,
                                           destination_drw.type_with_alpha, 
                                           "shape_warp_tmp_1",
                                           0,
                                           NORMAL_MODE
                                          )
    pdb.gimp_image_add_layer (img, intermediate_drw, 0)
    pdb.gimp_drawable_fill (intermediate_drw, FOREGROUND_FILL)
    warp_to_rect (source_drw, source_shape, source_offsets, intermediate_drw)
    
    
    pdb.gimp_drawable_transform_scale (intermediate_drw, 0, 0,
                                       destination_shape.width * 2,
                                       destination_shape.height * 2,
                                       TRANSFORM_FORWARD, 
                                       INTERPOLATION_CUBIC,
                                       True,
                                       3,
                                       False
                                      )

                                                                                
    warp_from_rect (intermediate_drw, destination_shape, destination_offsets, destination_drw, offset_angle)
    destination_drw.update(0, 0, destination_drw.width, destination_drw.height)
    
    pdb.gimp_selection_load (old_selection)
    pdb.gimp_image_remove_channel (img, old_selection)
    #paste results
    
    pdb.gimp_image_remove_layer (img, intermediate_drw)
    pdb.gimp_context_set_foreground (old_color)
    pdb.gimp_image_delete (source_shape.image)
    pdb.gimp_image_delete (destination_shape.image)
    pdb.gimp_image_undo_group_end (img)
    pdb.gimp_displays_flush ()

def prepare_shape (drw):
    """Paste drawable as new gray image, and autocrop"""
    pdb.gimp_edit_copy (drw)
    new_image = pdb.gimp_image_new (drw.width, drw.height, GRAY)
    pdb.gimp_image_undo_disable (new_image)
    new_layer = pdb.gimp_layer_new (new_image, drw.width, drw.height,
                                    GRAY_IMAGE, "source_shape",100,
                                    NORMAL_MODE
                                   )
    pdb.gimp_image_add_layer (new_image, new_layer, 0)
    floating_sel = pdb.gimp_edit_paste (new_layer, False) 
    pdb.gimp_floating_sel_anchor (floating_sel)
    pdb.plug_in_autocrop_layer (new_image, new_layer)
    
    print new_layer.offsets
    
    return offsets, new_layer

def warp_to_rect (source_drw, shape, offsets, destination_drw):
    
    
    x = offsets[0]
    y = offsets[1]
    w = shape.width
    h = shape.height
    
    cx = (x + w) / 2.0
    cy = (y + h) / 2.0
    
    dw = destination_drw.width
    dh = destination_drw.height
    dest_cx = dw / 2.0
    dest_cy = dh / 2.0
    
    radius_cache = "\x00" * w * h
    
    source_pr = source_drw.get_pixel_rgn (x, y, w, h)
    shape_pr = shape.get_pixel_rgn (x, y, w, h)
    destination_pr = destination_drw.get_pixel_rgn (0, 0, dw, dh)
    for j in xrange (dh):
        for i in xrange (dw):
            a, r = get_polar (i + 0.5, j + 0.5, dest_cx, dest_cy)
            R = max_radius (cx, cy, a)
            normal_r = r / 
            #enters the normalized distances to the shape center in each pixel of the cache
            #for this given angle. Skips pixels 
            fill_radius_cache (radius_cache, w, h, a)
    

def warp_from_rect (source_drw, shape, offsets, destination_drw, offset_angle):
    pdb.gimp_drawable_fill (destination_drw, FOREGROUND_FILL)
    
def get_polar (x, y, cx, cy):
    dx = x -cx
    dy = y - cy
    r = math.hypot (dx, dy)
    a = math.atan2 (dx, dy)
    return a, r
def max_radius (cx, cy, a):
    """Returns the maximum distance of a line  with an angle a from the center cx, cy
     possible inside a rectangle
     """
    
    v =  cx * math.tan (a)
    if not abs(v)> cy:
        R = math.hypot (v,cx) 
    else:
        a -= math.pi / 2.0
        v = cy * math.tan(a)
        R = math.hypot (v, cy)
    return R
    
        
    
register(
        "shape_warp",
        "Warps image in a shape into other shape",
        "shape_warp (img, dest_drw, source_drw, source_shape, destination_shape) -> None",
        "Joao S. O. Bueno Calligaris",
        "(C) Joao S. O. Bueno Calligaris - available exclusively under the GPL. source-code reuse restrictions apply.",
        "2004",
        "<Image>/Python-Fu/Shape Warp",
        "*",
        [(PF_DRAWABLE, "source", "source_layer", None),
         (PF_DRAWABLE, "source_shape", "Source shape", None),
         (PF_DRAWABLE, "dest_shape", "Destination Shape",None),
         (PF_SLIDER, "offset_angle", "Offset Angle", 0, (-360,360, 1)),
         
        ],     
        [],
        shape_warp)
main ()