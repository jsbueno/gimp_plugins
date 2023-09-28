#!/usr/bin/env python
# -*- Coding: utf-8 -*-

#Distributed under the GPL. Read the terminal  output of the
#license () function for full legal text.

from gimpfu import *
from math import sin, cos, pi, sqrt, tan
import random

DOTS_ONLY, DRAW_LINES, FILL_TRIANGLES = 0, 1, 2

def triangular_grid(img, drw, size=30, angle_d=0,
                    connect=DRAW_LINES, alternate_fill=False, distort_selection=False, gradient_highlight=False,
                    palette="Default", gradient="Default", gradient_opacity=25):
    """
    """
    
    fill = connect == FILL_TRIANGLES
    angle = angle_d / 180.0 * pi
    m = max(drw.width, drw.height)
    width = m * sqrt(1 +  tan(angle))
    height = m * sqrt(1 +  tan(angle))
    if width > 3 * drw.width:
        width = 3 * drw.width
    if height > 3 * drw.height:
        height = 3 * drw.height
          
    img.undo_group_start()
        
    selection_exists, lx1, ly1, lx2, ly2 = pdb.gimp_selection_bounds(img)
    
    even = True
    
    y = 0.0
    gimp.progress_init("Drawing grid")
    
    def f(x, y):
        return ( (drw.width / 2.0 +  
                  cos(angle) * (x - width / 2.0) -
                  sin(angle) * (y - height / 2.0)), 
    
                (drw.height / 2.0 - 
                  sin(angle) * (x - width / 2.0) - 
                  cos(angle) * (y - height / 2.0))
               )
    if fill:
        num_colors = pdb.gimp_palette_get_info(palette)
        def_color = pdb.gimp_context_get_foreground()
        if selection_exists:
             original_selection = pdb.gimp_selection_save(img)
            
        
        #vectors = pdb.gimp_vectors_new(img, "triangle_grid_tmp")
        #pdb.gimp_image_add_vectors(img, vectors, -1)
        
    vstep =  size * cos(30 / 180.0 * pi)
    pdb.gimp_context_set_gradient(gradient)
    while y < height:           
        if even:
            x = - size 
        else:
            x = - size * 0.5  # sin(30 / 180.0 * pi)
            
        while x < width:
            x1, y1 = f(x, y)
            x2, y2 = f(x + size, y)
            x0, y0 = f(x + size / 2.0, y + vstep)
            if not (x1 < lx1 - size  or
                    x1 > lx2 + size  or
                    y1 < ly1 -  size or
                    y1 > ly2 + size ):
                
                if connect == DOTS_ONLY:
                        pdb.gimp_paintbrush_default(drw, 2, (x1,y1))
                elif connect == DRAW_LINES:
                    pdb.gimp_paintbrush_default(drw, 8, (x0, y0, x1, y1, x2, y2, x0, y0))
                    
                elif fill:
                    for i in (0, 1):
                        if alternate_fill and i:
                            break
                        if i:
                            x2, y2 = f(x + size / 2.0, y + vstep)
                            x0, y0 = f (x - size / 2.0, y + vstep) 
                        vectors = pdb.gimp_vectors_new(img, "triangle_grid_tmp")
                        pdb.gimp_image_add_vectors(img, vectors, -1)
                        #dragonscales: 
                        #stroke = pdb.gimp_vectors_bezier_stroke_new_ellipse(vectors, x0, y0, size, size, 0)
                        
                        stroke = pdb.gimp_vectors_bezier_stroke_new_moveto(vectors, x0, y0)
                        pdb.gimp_vectors_bezier_stroke_lineto(vectors, stroke, x1,y1)
                        pdb.gimp_vectors_bezier_stroke_lineto(vectors, stroke, x2,y2)
                        pdb.gimp_vectors_stroke_close(vectors, stroke)
                        
                        pdb.gimp_vectors_to_selection(vectors, CHANNEL_OP_REPLACE, True, False, 0, 0)
                        if not pdb.gimp_selection_bounds(img)[0]:
                                continue
                        if selection_exists:
                            pdb.gimp_selection_combine(original_selection, CHANNEL_OP_INTERSECT)
                            if not pdb.gimp_selection_bounds(img)[0]:
                                continue
                            if distort_selection:
                                pdb.gimp_vectors_to_selection(vectors, CHANNEL_OP_REPLACE, True, False, 0, 0)
                                            
                        pdb.gimp_image_remove_vectors(img, vectors)
                        
                        
                        color = pdb.gimp_palette_entry_get_color(palette, random.randrange(num_colors))
                        x4, y4 = (x0 + x1 + x2) / 3.0, (y0 + y1 + y2) / 3.0 
                        pdb.gimp_context_set_foreground(color)
                        pdb.gimp_edit_bucket_fill_full(drw, FG_BUCKET_FILL, NORMAL_MODE,
                                                    100, 15, False, True, 
                                                    SELECT_CRITERION_COMPOSITE, x4, y4)
                        if gradient_highlight:
                            pdb.gimp_edit_blend (drw, CUSTOM_MODE, MULTIPLY_MODE, 
                                             GRADIENT_LINEAR, gradient_opacity,
                                             0,  REPEAT_NONE, False, False, 0, 0,
                                             False, x0, y0, x1, y1)
                                             
                                             
                        if 0:
                            x5 = (x4 - drw.height / 2.0) / drw.width * 6.0
                            y5 = (y4 - drw.height / 2.0) / drw.width * 6.0
                            pdb.plug_in_lighting (img, drw, None, None, False, False, 0,
                                                  0, (255,255,255),
                                                  -x5, -y5, 1,
                                                  0, 0, 0,
                                                  0.3, 0.5, 0.5, 0.2, 0,
                                                  False, False, False)
                        
                                                  
                                                  
                                                  
                    pdb.gimp_context_set_foreground(def_color)
            
                                 
            x += size
        even = not even
        y += vstep
        gimp.progress_update(y / height)
        
    if selection_exists and fill:
        selection = pdb.gimp_selection_load(original_selection)
        pdb.gimp_image_remove_channel(img, original_selection)
    else:
        pdb.gimp_selection_none(img)
    
    img.undo_group_end()

register(
        "triangular_grid",
        "Draws a triangular grid",
        """Flip selection using the two first nodes of current path as the flip axis.
        """,
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2007. GPL applies.",
        "<Image>/Filters/Render/Triangular Grid",
        "*",
        [(PF_INT,   "size", "Grid Size (pixels)",30),
         (PF_SPINNER, "angle", "Grid Angle", 0.0, (-60, 60, 0.1)),
         
         (PF_RADIO, "connect", "Draw grid lines", DRAW_LINES,
          [ ("Dots only", DOTS_ONLY),("Draw lines", DRAW_LINES), ("Fill", FILL_TRIANGLES)] 
         ),
         (PF_BOOL, "alternate_fill", "Alternate Filling", False),
         (PF_BOOL, "distort_selection", "Distort Selection", False),
         (PF_BOOL, "gradient_highlight", "Use Gradient Highlight", False),
         (PF_PALETTE, "palette", "Fill Palette", "Default"),
         (PF_GRADIENT, "gradient", "Hightlight Gradient", "Default"),
         (PF_SPINNER, "gradient_opacity", "Highlight Opacity", 20, (0, 100,1)),
        ],
        [],
        triangular_grid)

main()
