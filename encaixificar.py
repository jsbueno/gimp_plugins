#!/usr/bin/env python

from gimpfu import *

def encaixificar (img, drawable,max_x, max_y, color):
    if max_x <= 0 or max_y <= 0 :
      return
    pdb.gimp_image_undo_group_start(img)
    if img.width > max_x or img.height > max_y:
        print "la vou eu"
        if img.width / max_x > img.height / max_y:
            ratio = float (max_x) / img.width
        else:
            ratio = float (max_y) / img.height

        img.scale ( (img.width * ratio),  (img.height * ratio))
        pdb.gimp_displays_flush()
    try:
      pdb.gimp_layer_add_alpha (drawable)
    except:
      pass
    img.resize (max_x, max_y,0,0)
    #pposition the layer on the bottom-right corner of the resized image:
    pdb.gimp_layer_set_offsets (drawable, 0, max_y - img.height)

    if drawable.is_gray:
      mode = GRAYA_IMAGE
    elif drawable.is_indexed:
      mode = INDEXEDA_IMAGE
    else:
      mode = RGBA_IMAGE
    new_drw = pdb.gimp_layer_new (img, max_x, max_y, mode,
                                  "background", 100, NORMAL_MODE)
    pdb.gimp_image_add_layer (img, new_drw, len (img.layers))
    old_fg = gimp.get_foreground ()
    gimp.set_foreground (color)
    pdb.gimp_drawable_fill (new_drw, FOREGROUND_FILL)
    gimp.set_foreground (old_fg)


    pdb.gimp_image_undo_group_end(img)
    pdb.gimp_displays_flush ()


register(
         "encaixificar",
         "Prepare for web - specific site",
         "recuces an  image to the larger that will fit in given size, fixes the aspect ratio and adds a white background layer",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2004",
         "<Image>/Python-Fu/encaixificar",
         "*",
         [
            (PF_INT, "Maximum_X", "Maximum horz. image size", 400),
            (PF_INT, "Maximum_y", "Maximum vert. image size", 400),
            (PF_COLOR, "color", "Color to apply to background", (255,255,255))
         ],
         [],
         encaixificar)

main()
