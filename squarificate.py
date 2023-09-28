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



def squareficate(img, original_drw, number, mean_size, standard_deviation, tileable, clip, rotate, use_palette):
    global g_rotate
    g_rotate = rotate
    pdb.gimp_image_undo_group_start(img)

    number = int (number)

    #pdb.gimp_progress_init("Squareficating", -1)
    selection, x1, y1, x2, y2 = pdb.gimp_selection_bounds (img)

    if not selection:
        x1 = y1 = 0
        x2 = img.width
        y2 = img.height

    if use_palette:
        original_color = pdb.gimp_context_get_foreground ()
        palette = pdb.gimp_context_get_palette()
        num_colors =  pdb.gimp_palette_get_info (palette)
    if clip:
        mode = CLIP_TO_BOTTOM_LAYER
    else:
        mode = EXPAND_AS_NECESSARY


    work_img = pdb.gimp_image_new (x2 - x1, y2 - y1, 0)
    ox1 = x1
    oy1 = y1
    x1 = y1 = 0
    x2 = x2 - ox1
    y2 = y2 - oy1

    pdb.gimp_image_undo_freeze (work_img)

    complete = 0.0
    if tileable:
        work_drw = make_new_drw (work_img, x1, y1, x2, y2)
        pdb.gimp_drawable_set_name (work_drw, "Squares")
        pdb.gimp_drawable_fill (work_drw, TRANSPARENT_FILL)

    else :
        new_drw = make_new_drw (work_img, x1, y1, x2, y2)
        pdb.gimp_drawable_fill (new_drw, TRANSPARENT_FILL)
        pdb.gimp_drawable_set_name (new_drw, "Squares")
        work_drw = new_drw
    i = 0
    #and a second counter to avoids an infinite loop
    total_i = 0
    while i < number:
        i += 1
        total_i += 1
        if 1:
            side = random.gauss (mean_size, standard_deviation / 2)
            if (side < 1): side = 1
            width = height = side
            if tileable:
                x = random.randrange (x1, x2)
                y = random.randrange (y1, y2)
            else:
                x = random.randrange (int (x1 - side), x2)
                y = random.randrange (int (y1 - side), y2)
            cx = x + width / 2
            cy = y + width / 2
            #do not place squares centered out of the selection shape even
            #when clip is turned of.
            if not clip and not pdb.gimp_selection_value (img, ox1 + cx, oy1 + cy):
                i -= 1

                if total_i > 20 * number:
                    break
                continue
            if  tileable:
                new_drw = make_new_drw (work_img, x1, y1, x2, y2)
                pdb.gimp_drawable_fill (new_drw, TRANSPARENT_FILL)
            square_drw = make_new_drw (work_img, x, y, x + width, y + height)
            if use_palette:
                pdb.gimp_context_set_foreground (
                    pdb.gimp_palette_entry_get_color (palette,
                        random.randrange (0, num_colors)) )
            pdb.gimp_drawable_fill (square_drw, FOREGROUND_FILL)
            if rotate:
                #currently rotate just works around the image (0,0)

                square_drw.set_offsets ( - square_drw.width/2, -square_drw.height/2)
                pdb.gimp_rotate (square_drw, 1, random.uniform (0, pi/2))
                square_drw.set_offsets (x, y)
                width = square_drw.width
                height = square_drw.height
            off_x = off_y = 0
            if tileable:
                if x < x1:
                    off_x = x - x1
                if x + width >= x2:
                    #no bug here. If the square is larger than the boundaries,
                    # we have to go somewere.
                    off_x = - ((x + width) - x2 )
                if y < y1:
                    off_y = y - y1
                if y + height >= y2:
                    off_y = - ( (y + width) - y2)
                square_drw.set_offsets (x + off_x, y + off_y)

            #merge square to new_drw
            new_drw = pdb.gimp_image_merge_down (work_img, square_drw, mode)
            if tileable:
                pdb.gimp_drawable_offset (new_drw, 1, OFFSET_TRANSPARENT, -off_x, -off_y)
                #merge to work_drw
                pdb.gimp_image_merge_down (work_img, new_drw, mode)
            complete = 0.9 * (float(i)/number)
            #pdb.gimp_progress_update (complete)
        #except Exception, error:
        #    print error
    if use_palette:
        pdb.gimp_context_set_foreground (original_color)
    try:
        pdb.gimp_image_undo_thaw (work_img)
        pdb.gimp_edit_copy (work_img.layers[0])

        #"clip"mode to tell if paste behind selection or in front of it
        floating_sel = pdb.gimp_edit_paste (original_drw,  clip)
        #pdb.gimp_layer_translate (floating_sel, ox1, oy1)
        pdb.gimp_floating_sel_anchor (floating_sel)
        pdb.gimp_image_delete (work_img)


        pdb.gimp_displays_flush ()
        #pdb.gimp_progress_update (1)
    except Exception, error:
        print error
    pdb.gimp_image_undo_group_end (img)


register(
        "squarificate",
        "Add randomsized squares as noise on the image",
        "squarificate (img, drw, number, mean_size, standard_deviation, tileable, clip,  rotate, use_palette) -> None",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2004",
        "<Image>/Python-Fu/Squareficate",
        "*",
        [(PF_SPINNER, "number", "number_of_squares", 50, (1,500,1)),
         (PF_SLIDER, "mean_size", "Medium size of the squares", 20, (1,300,1)),
         (PF_SLIDER, "standard_deviation", "Variation in the square size", 15, (0,300,1)),
         (PF_TOGGLE, "tileable", "Whether to make tileable", 0),
         (PF_TOGGLE, "clip", "Clip squares to Selection ", 1),
         (PF_TOGGLE, "rotate", "Whether to rotate squares", 0),
         (PF_TOGGLE, "use_palette", "Use colors from active palette", 0)
        ],
        [],
        squareficate)
main ()
