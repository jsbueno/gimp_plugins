#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gimpfu import *
from math import sqrt
import os.path


def color_correct (img, drw, contrast_enhance, reduce_red):
    pdb.gimp_image_undo_group_start (img)
    pdb.plug_in_c_astretch (img, drw)
    #enhance contrast
    pdb.gimp_brightness_contrast (drw, 0, contrast_enhance)
    #reduce red:
    pdb.gimp_hue_saturation (drw, RED_HUES, 0, 0,
                                -100 + reduce_red)
    if reduce_red < 80:
        #as we don't have an  "overlap" option when using hue_saturation via pdb
        pdb.gimp_hue_saturation (drw, YELLOW_HUES, 0, 0,
                                -50 + reduce_red // 2)
    pdb.gimp_image_undo_group_end (img)

def crop_at_guides (img, drw):
    x1, y1, x2, y2 = get_guides_square_coord (img)
    pdb.gimp_image_crop (img, x2 - x1, y2 - y1, x1, y1)

def get_path_length (img, pathname):
    """
    Returns the length between the first two nodes of a given path
    """
    path=pdb.gimp_path_get_points (img, pathname)
    path=list(path)

    path_points = list(path[3])
    numpoints=path[2]
    if path[2] < 12:
        raise "Invalid Path"

    x0 = path_points[0]
    y0 = path_points[1]

    x1 = path_points[9]
    y1 = path_points[10]

    l = sqrt ((x1 - x0) ** 2 + (y1 -y0) ** 2)
    print l
    return l

def get_guides_square_coord (img):
    """
    Gets the coordinates of the rectangle bound by the first two horizontal and first two
    vertical guides on an image. If tehre are no, or missing guides, the image's
    boundaries are returned.
    """
    horiz = []
    vert = []
    guide_id = pdb.gimp_image_find_next_guide (img, 0)
    while guide_id:
        orientation =  pdb.gimp_image_get_guide_orientation (img, guide_id)
        if orientation == ORIENTATION_HORIZONTAL:
            horiz.append (pdb.gimp_image_get_guide_position (img, guide_id))
        elif orientation == ORIENTATION_VERTICAL:
            vert.append (pdb.gimp_image_get_guide_position (img, guide_id))
        guide_id = pdb.gimp_image_find_next_guide (img, guide_id)
    if len (horiz) == 0:
        horiz.append (0)
    if len (horiz) == 1:
        horiz.append (img.width)
    if len (vert) == 0:
        vert.append (0)
    if len (vert) == 1:
        vert.append (img.height)
    horiz.sort ()
    vert.sort ()
    return horiz[0], vert[0], horiz[1], vert[1]


def get_layer_by_name (img, name):
    for layer in img.layers:
        if layer.name == name:
            return layer
    #If there is no layer named "USER", create a new one, behind the top layer:
    layer = pdb.gimp_layer_new (img, img.width,
                                img.height, img.base_type | 1,
                                name, 100,
                                NORMAL_MODE)

    pdb.gimp_image_add_layer (img, layer, 1)
    pdb.gimp_drawable_fill (layer, TRANSPARENT_FILL)
    return layer

def place_layer_above (img, layer, name):
    """place given layer just above layer with name "name"
    """
    if layer != img.layers[0]:
        pdb.gimp_image_raise_layer_to_top (img, layer)
    for search_layer in img.layers [1:]:
        if search_layer.name == name:
            break
        pdb.gimp_image_lower_layer (img, layer)

def celebrity_paste (img, drw, target_image, scale_down, target_folder):
    """
    Usage: have a person body/torso selected in both source and target images.
    A copy of target image is made, person is cut from source image, color histogram auto
    -corrected, and pasted on new image, scaled to roughly the same size. The original
    selected torso on this image is pasted as a new layer above the person who was
    copied from the source image. Optionally, everything is scaled down.

    After the plug-in is run, some steps can of it can be un-done, so one
    can have control of all steps.

    """
    apply_color_correct = False
    reduce_red = 100
    paste = True
    crop = False
    if paste:
        n_img = pdb.gimp_image_duplicate (target_image)
        disp = pdb.gimp_display_new (n_img)

        cel_drw = n_img.layers [0]
        cel_left = cel_drw.offsets[0]
        cel_height = cel_drw.height
        cel_width = cel_drw.width
        #print cel_left, cel_height, cel_width

        #autocrop not working asit should
        #that is why I had to anotate the cel. , width, offset, above
        #pdb.plug_in_autocrop_layer (n_img, cel_drw)

        pdb.gimp_image_undo_group_start (n_img)

        old_user_layer = get_layer_by_name (n_img, "USER")

        pdb.gimp_edit_copy (drw)
        floating = pdb.gimp_edit_paste (old_user_layer, False)
        user_height = floating.height
        user_width = floating.width
        #print "user:", user_height, user_width
        user_layer = floating
        pdb.gimp_floating_sel_to_layer (floating)

        place_layer_above (n_img, user_layer, "USER")

        pdb.gimp_image_remove_layer (n_img, old_user_layer)
        user_layer.name = "USER"

        #pdb.gimp_floating_sel_anchor (floating)

        #pdb.plug_in_autocrop_layer (n_img, user_layer)
        pdb.gimp_image_undo_group_end (n_img)

        #now, guess some scaling.
        #The scale function takes the final coordinates
        #of the work layer. So we also try to guess  a nice place to
        #leave our pasted image
        try:
            user_path = pdb.gimp_path_get_current (img)
            cel_path = pdb.gimp_path_get_current (n_img)
            factor = get_path_length (n_img, cel_path) / get_path_length (img, user_path)
        #if there is no path set:
        except RuntimeError:
            print "No paths detected: using default scale"
            factor = float (cel_width) / user_width


        #estimate where in the image we have space:
        x1, y1, x2, y2 = get_guides_square_coord (n_img)

        if cel_left - x1 > x2 - (x1 + cel_width):
            #paste at left of the celebrity
            left =  cel_left - 0.9 * user_width * factor
            left = max (x1, left)
        else:
            left = cel_left + cel_width - 0.1 * user_width * factor
            if left + user_width * factor > x2:
                left = x2 - user_width * factor
        right = left + user_width * factor
        botton = n_img.height
        top = botton - user_height * factor
        #print factor

        pdb.gimp_drawable_transform_scale (user_layer,
                                           left, top, right, botton,
                                           TRANSFORM_FORWARD,
                                           INTERPOLATION_CUBIC,
                                           True, 3, False)
        user_layer.set_offsets (int (left), int(top))
        if crop:
            if scale_down:
                #scaling down must be done prior to cropping due
                # to undo workflow issues:
                ratio = float (y2 - y1) / (x2 - x1)
                guides_ratio =  n_img.width / float (x2 - x1)

                pdb.gimp_image_scale (n_img, guides_ratio * img.width,
                                      guides_ratio * img.width * ratio)

                x1, y1, x2, y2 = get_guides_square_coord (n_img)
            if apply_color_correct:
               color_correct (n_img, user_layer, 12, reduce_red)
               apply_color_correct = False

            pdb.gimp_image_crop (n_img, x2 - x1, y2 - y1, x1, y1)
        elif scale_down:
            ratio = float (n_img.height) / n_img.width
            pdb.gimp_image_scale (n_img, img.width, img.width * ratio)
        #sets filename on the new image equal filename on the old image:
        old_filename = pdb.gimp_image_get_filename (img)
        filename = os.path.join (target_folder, os.path.basename (old_filename))

        pdb.gimp_image_set_filename (n_img, filename)
        #backup old image:
        if old_filename == filename:
            backup_name = filename.split (".")
            backup_name.insert (-1, "orig")
            backup_name = ".".join (backup_name)
            pdb.gimp_image_set_filename (img, backup_name)
            try:
                #copy file
                open (backup_name, "wb").write (open (filename, "rb").read())
            except:
                print "It was not possible to make a backup copy of the original image"

    else:
        pdb.gimp_image_undo_group_start (img)
        pdb.gimp_edit_copy (drw)
        floating = pdb.gimp_edit_paste (img.active_drawable, False)
        user_layer = pdb.gimp_layer_new (img, img.width,
                                      img.height, floating.type,
                                      "work layer", 100,
                                      NORMAL_MODE)
        pdb.gimp_image_add_layer (img, user_layer, 0)
        pdb.gimp_floating_sel_attach (floating, user_layer)
        pdb.gimp_floating_sel_anchor (floating)
        pdb.gimp_image_undo_group_end (img)
        n_img = img

    if apply_color_correct:
        color_correct (n_img, user_layer, 12, reduce_red)

    gimp.displays_flush ()

register   ("celebrity_paste",
            "Copies selected person to target image, attempting to make it fit there.",
            celebrity_paste.__doc__,
            "João S. O. Bueno Calligaris",
            """Konrads & Aleks, paste apropriate (c) info here. If possible, I'd like this to remain free software, but the GIMP license does not make it mandatory""",
             "2006-03-09",
             # In gimp 2.4 python plug-ins will no longer be segregated
             # to "python-fu". So I am coping with that here
             "<Image>/Filters/Work/Paste...",
             "*",
             [
                (PF_IMAGE, "target_image", "Target Image", None),
                (PF_BOOL, "scale_down", "Scale Result to Source Image Size", False),
                (PF_STRING, "target_folder", "Target folder where to save the edited image", "")
             ],
             [],
             celebrity_paste
            )

register   ("color_correct",
            "Applies standard color correction to photos from cheap cameras.",
            "",
            "João S. O. Bueno Calligaris",
            """Konrads & Aleks, paste apropriate (c) info here. If possible, I'd like this to remain free software, but the GIMP license does not make it mandatory""",
             "2006-03-13",
             # In gimp 2.4 python plug-ins will no longer be segregated
             # to "python-fu". So I am coping with that here
             "<Image>/Filters/Work/Colour Correct...",
             "*",
             [
                (PF_SPINNER, "contrast_enhance",
                  "Contrast Enhancement", 12, (1, 50, 1)),
                (PF_SPINNER, "reduce_red",
                  "Percent of Red to leave on the image", 90, (1, 100, 1))
             ],
             [],
             color_correct
            )

register   ("crop_at_guides",
            "Crop image to area delimited to the four guides.",
            "",
            "João S. O. Bueno Calligaris",
            """Konrads & Aleks, paste apropriate (c) info here. If possible, I'd like this to remain free software, but the GIMP license does not make it mandatory""",
             "2006-03-13",

             "<Image>/Filters/Work/Crop At Guides",
             "*",
             [],
             [],
             crop_at_guides
            )


main ()
