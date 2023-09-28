#!/usr/bin/python

from gimpfu import *


def test_colors(img, drw):
    gimp.set_foreground((255,0,0))
    pdb.gimp_drawable_fill(drw, FOREGROUND_FILL)
  


register(
        "test_colors",
        "test working of color parameters",
        "",
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2008. GPL applies.",
        "<Image>/Python-Fu/Test color handling",
        "",
        [],
        [],
        test_colors)

main()
