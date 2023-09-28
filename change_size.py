#!/usr/bin/python

#Distributed under the GPL. Read the terminal  output of the
#license () function for full legal text.
def license():
    print """
    Python Fu scripts for Path manipulation and export in the GIMP
    PATHS.PY V 1.1 11 May, 2003.
    Copyright (C) 2003  Joao S. O. Bueno

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from gimpfu import *

def change_size(img, drw):
    """Chnages a image size to teh (rectangular) selection boundary size, either by cropping, or by scaling up.
    """
    #no need for undo grouos, since a single opertaion is performed on the image.

    exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds (img)

    ix1, iy1, ix2, iy2 = (0,0, drw.width, drw.height)
    if not exists:
        return
    pdb.gimp_image_undo_group_start (img)

    pdb.gimp_selection_none (img)
    if (x1 < ix1 or y1 < iy1 or
        x2 > ix2 or y2 > iy2):
        ratio = float (ix2 - ix1) / (iy2 - iy1)
        if ratio > 1:
            scale_ratio = float (x2 - x1) / (ix2 - ix1)
        else:
            scale_ratio = float (y2 - y1) / (iy2 - iy1)
        pdb.gimp_image_scale (img, ix2 * scale_ratio, iy2 * scale_ratio)
    pdb.gimp_image_crop (img, x2 - x1, y2 - y1, x1, y1)
    pdb.gimp_image_undo_group_end (img)
    gimp.displays_flush ()


register(
        "change_size",
        "Changes an Image size to the Selection boundary size",
        """Changes an Image size to the Selection boundary size
        """,
        "Joao S. O. Bueno Calligaris",
        "Joao S. O. Bueno Calligaris",
        "2006. GPL applies.",
        "<Image>/Image/Change Size",
        "*",
        [],
        [],
        change_size)

main()
