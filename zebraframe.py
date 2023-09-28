#!/usr/bin/env python

from gimpfu import *
from math import floor

Rect = 0
Ellipse = 1
Free = 2

def zebra_select (img, drawable, ammount = 1, percent = 10.0, weaken = False, 
                  fade_inside = 1, shape = Rect):

    pdb.gimp_image_undo_group_start (img)

    is_sel, x1, y1, x2, y2 = pdb.gimp_selection_bounds (img)
    if shape == Free and not is_sel:
        pdb.gimp_selection_all (img)
    
    w = ow = x2 - x1
    h = oh = y2 - y1
    
    h_step = ow * percent / 100.0
    v_step = oh * percent / 100.0
    
    width=pdb.gimp_image_width (img)
    height=pdb.gimp_image_height (img)
    
    if not weaken and shape != Free:
        
        for i in xrange (ammount):
            x2 = x1 + h_step
            y2 = y1 + v_step
    
            w2 = w - 2 * h_step 
            h2 = h - 2 * v_step 
            
            if w2 < 0 or h2 < 0:
                break
            
            if shape == Rect:        
                pdb.gimp_rect_select (img, x1, y1, w, h, CHANNEL_OP_ADD, 0, 0)
                pdb.gimp_rect_select (img, x2, y2, w2, h2, CHANNEL_OP_SUBTRACT,0 , 0)
            elif shape == Ellipse:
                pdb.gimp_ellipse_select (img, x1, y1, w, h, CHANNEL_OP_ADD, 1, 0, 0)
                pdb.gimp_ellipse_select (img, x2, y2, w2, h2, CHANNEL_OP_SUBTRACT, 1, 0, 0)
            
            x1 += h_step * 2
            y1 += v_step * 2
            
            w -= h_step * 4
            h -= v_step * 4
    else:
        pdb.gimp_context_push ()
        selection = pdb.gimp_channel_new (img, img.width, img.height,
                                         "zebra_sel tmp channel", 50,
                                         (128, 128, 128)
                                         )
        pdb.gimp_image_add_channel (img, selection, 0)
        if shape != Free:
            pdb.gimp_selection_none (img)
            
        color = (255,) * 3 #White (only used if shape == Free and !weaken)
    
        pdb.gimp_context_set_foreground ((0,0,0))
        
        pdb.gimp_drawable_fill (selection, FOREGROUND_FILL)
        if ammount == 0:
            return
        
        shrink_step = min (h_step, v_step) / 2.0 
        
        for i in xrange (ammount):
            if shape !=  Free:
                x2 = x1 + h_step
                y2 = y1 + v_step
        
                w2 = w - 2 * h_step
                h2 = h - 2 * v_step
                
                if w2 < 0 or h2 < 0:
                    break
                
                if shape == Rect:                    
                    pdb.gimp_rect_select (img, x1, y1, w, h, CHANNEL_OP_REPLACE, 0, 0)
                    pdb.gimp_rect_select (img, x2, y2, w2, h2, CHANNEL_OP_SUBTRACT, 0, 0)
                elif shape == Ellipse:
                    pdb.gimp_ellipse_select (img, x1, y1, w, h, CHANNEL_OP_REPLACE, 1, 0, 0)
                    pdb.gimp_ellipse_select (img, x2, y2, w2, h2, CHANNEL_OP_SUBTRACT, 1, 0, 0)
            else:
                if i > 0 :
                    pdb.gimp_selection_shrink (img, shrink_step)
                    if not pdb.gimp_selection_bounds (img) [0]:
                        break
            
            if weaken:
                tmp_color = float (i) / ammount
                if fade_inside:
                    tmp_color = 1 - tmp_color
                color = (int (255 * tmp_color), ) * 3
                
            pdb.gimp_context_set_foreground (color)
            pdb.gimp_edit_fill (selection, FOREGROUND_FILL)
            
            if shape == Free:
                pdb.gimp_selection_shrink (img, shrink_step)
                if not pdb.gimp_selection_bounds (img) [0]:
                    break
                pdb.gimp_context_set_foreground ((0,0,0))
                pdb.gimp_edit_fill (selection, FOREGROUND_FILL)
                
                
            else:
                x1 += h_step * 2
                y1 += v_step * 2
                w -= h_step * 4
                h -= v_step * 4
        pdb.gimp_selection_load (selection)
        pdb.gimp_image_remove_channel (img, selection)
            
        pdb.gimp_context_pop ()
            
    pdb.gimp_image_undo_group_end (img)




register(
         "zebra_select",
         "Horizontal Gradient Blurrer",
         "Horizontal Gradient Blurrer - honest",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2003",
         "<Image>/Python-Fu/Alchemy/Zebra Select",
         "*",
         [
                (PF_INT, "ammount", "How many stripes", 1),
                (PF_FLOAT, "percent", "image size percent for each stripe", 10),
                (PF_BOOL,"weaken", "Fade selection?", 0 ),
                (PF_BOOL, "fade_inside", "Fade inner stripes?", 1),
                (PF_RADIO, "shape", "Shape to use:", "Rect", 
                [("Rect", Rect), ("Ellipse", Ellipse), ("Free", Free)])
         ],
         [],
         zebra_select)

main()
