from gimpfu import *
from random import randrange, choice, uniform

def randrect(img, drw, interactions=50):
    img.undo_group_start()
    old_sel = pdb.gimp_selection_save(img)
    if not drw.width or not drw.height:
        return
    for i in xrange(interactions):
        x1 = randrange(drw.width)
        x2 = randrange(drw.width)
        y1 = randrange(drw.height)
        y2 = randrange(drw.height)
        x = min(x1, x2)
        y = min(y1,y2)
        width = max(x1, x2) - x
        height = max(y1, y2) - y
        
        #pdb.gimp_rect_select(img, x, y, width, height, CHANNEL_OP_REPLACE, False, 0.0)
        pdb.gimp_ellipse_select(img, x, y, width, width, CHANNEL_OP_REPLACE, False, 0,0.0)
        #pdb.gimp_channel_combine_masks(img.selection, old_sel, CHANNEL_OP_INTERSECT, 0, 0)
        if pdb.gimp_selection_bounds(img)[0]:
            pdb.gimp_edit_bucket_fill(drw, FG_BUCKET_FILL, DIFFERENCE_MODE, 100, 100, False, 0, 0)
    pdb.gimp_selection_load(old_sel)
    pdb.gimp_image_remove_channel(img, old_sel)
    img.undo_group_end()
    gimp.displays_flush()

register(
        "rand_rect",
        "Adds random rectangles to the image, filling then with difference mode",
        "Adds random rectangles to the image, filling then with difference mode",
        "Joao S. O. Bueno",
        "GPLv3 - ",
        "2007",
        "<Image>/Python-Fu/Rand Rect",
        "*",
        [
            (PF_INT, "rectangles", "Number of rectangles", 50),
        ],
        [],
        randrect)
main ()