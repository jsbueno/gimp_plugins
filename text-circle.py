#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# text-circle.py -- a script for The GIMP
# Author: Joao S. O. Bueno, based on script-fu by Shuji Narazaki <narazaki@gimp.org>
# Time-stamp: <1998/11/25 13:26:51 narazaki@gimp.org>
# Version 0.5
# Thanks (from original script-fu)
#   Jim Seymour (jseymour@jimsun.LinxNet.com)
#   Sven Neumann <sven@gimp.org>

from gimpfu import *
import math


def text_circle (img, drw, text, radius, start_angle, fill_angle,  font) :
    #pdb.gimp_image_undo_group_start (img)
    try:
        font_size = int (font.split(" ")[-1])
        font_name = font [:- len (font_size)]
        font_size = int (font_size)
    except:
        font_size = 18
        font_name = "Bitstream Vera Sans"
    text = unicode (text)
    
    sel, x1,y1, x2, y2 = pdb.gimp_selection_bounds (img)
    if not sel:
        x1, y1 = drw.offsets
        x2 = x1 + drw.width
        y2 = y2 + drw.height
    else:
        old_sel = pdb.gimp_selection_save (img)
        pdb.gimp_selection_none (img)

    visibility = hide_all_layers (img)
    cx = int ((x1 + x2) / 2)
    cy = int ((y1 + y2 ) / 2)
    
    angle = start_angle
    step = fill_angle / len (text)

    for character in text:
        #print "param: %d, %d, char=\"%s\", %d, %s" %(cx,cy, character.encode ("utf-8"), font_size, font_name)
        if character == u" ":        
            angle += fill_angle / len (text)
            continue 
        
        character_layer = pdb.gimp_text_fontname (img, None, cx, cy, character.encode("utf-8"), 0, 1, font_size, POINTS, font_name)
        
        if (fill_angle < 0):
            pdb.gimp_flip ( character_layer, 0)
            pdb.gimp_flip ( character_layer, 1)
        pdb.gimp_drawable_offset (character_layer, 0, OFFSET_TRANSPARENT, - character_layer.width /2, - radius)
        pdb.gimp_layer_resize (character_layer, character_layer.width, radius * 2, 0 , 0)
        pdb.gimp_rotate (character_layer, 1, angle /180.0 * math.pi)
         
        if not sel:
            drw.visible = 1
            pdb.gimp_image_merge_visible_layers (img, CLIP_TO_IMAGE)
        else:
            pdb.gimp_selection_load (img, old_sel)  
            pdb.gimp_edit_copy (character_layer)
            floating = pdb.gimp_edit_paste (drw,1)
            pdb.gimp_floating_sel_anchor (floating)
            pdb.gimp_selection_none
            pdb.gimp_image_remove_layer (img, character_layer)
        angle += fill_angle / len (text)

        
    if sel:
        pdb.gimp_selection_load (img, old_sel)
        pdb.gimp_channel_delete (old_sel)
    else:
        pdb.gimp_selection_none (img)
    
    restore_layer_visibility (img, visibility)
    pdb.gimp_displays_flush()
    #pdb.gimp_image_undo_group_end (img)
      
def hide_all_layers (img):
    visibility = []
    for layer in img.layers:
        visibility.append (layer.visible)
        layer.visible = 0
    return visibility
    
def restore_layer_visibility (img, visibility):
    i = 0
    for layer in img.layers:
        layer.visible = visibility[i]
        i += 1       

register (
  "text_circle",
  "Circular Text renders text around a circle",
  """This will render text around a circle, clockwise, or counter-clockwise.
  The previous script, in scirpt-fu, could not handle utf-8 strings
  """,
  "Joao S. O. Bueno",
  "Joao S. O. Bueno",
  "2004",
  "<Image>/Python-Fu/Text Circle",
  "*",
  [
     ( PF_STRING    ,"Text", "Text to render", "The GNU Image Manipulation Program Version 2.2 "),
     ( PF_ADJUSTMENT, "Radius", "Circle Radius", 256,  (80,8000,1) ),
     ( PF_ADJUSTMENT, "Start_Angle", "Starting Angle", 0,  (-360,360,1) ),
     ( PF_ADJUSTMENT, "Fill_Angle", "Fill Angle", 360, (-360, 360, 1)),
     ( PF_FONT       , "Font", "Font", "Bitstream Vera Sans 18")
  ],
  [],
  text_circle
  )
  
    
main ()