#!/usr/bin/python

#Distributed under the GPL. Read the terminal  output of the
#license () function for full legal text.


from gimpfu import *


def transfer_selection(img, drw, dest_image, copy_visible):
    is_sel, x, y , widh, height = pdb.gimp_selection_bounds (img)
    if not is_sel:
        #terminate if there is no selection.
        return
    if copy_visible:
        pdb.gimp_edit_copy_visible (img)
    else:
        pdb.gimp_edit_copy (drw)

    float_sel = pdb.gimp_edit_paste (dest_image.layers[0], False)
    float_sel.set_offsets (x,y)
    pdb.gimp_floating_sel_to_layer (float_sel)


register(
        "transfer_selection",
        "Tranfers selections content to other image",
        """Transfers selection content, like copy and paste, but preserves the original
           coordinates of the selection.
        """,
        "Joao S. O. Bueno Calligaris",
        "Joao S. O. Bueno Calligaris",
        "2005. Public Domain",
        "<Image>/Python-Fu/Transfer Selection",
        "*",
        [
          (PF_IMAGE, "destination_image", "Image",  None),
         (PF_BOOL, "copy_visible", "Copy Visible?", False)
        ] ,
        [],
        transfer_selection
        )

main()
