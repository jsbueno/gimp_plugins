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






def flip_about_path(img, drw):
    """Arbitraly flips a selection, usindg the two first nodes of the current path
       as the axis.
       
       EEK. my arbitrary flip code inside the GIMP is buggy.
    """
    #no need for undo grouos, since a single opertaion is performed on the image.
    
    path_id = pdb.gimp_image_get_active_vectors (img)
    if not path_id or path_id == -1:
        print "Image need an active vector for flip about path to work"
        return 0

    pathname = pdb.gimp_vectors_get_name (path_id)


    path=pdb.gimp_path_get_points (img, pathname)
    path=list(path)

    path_points = list(path[3])
    numpoints=path[2]
    if path[2] < 12:
        return 0

    x0 = path_points[0]
    y0 = path_points[1]
    
    x1 = path_points[9]
    y1 = path_points[10]

    pdb.gimp_drawable_transform_flip (drw,
                                      x0, y0,
                                      x1, y1,
                                      TRANSFORM_FORWARD,
                                      INTERPOLATION_CUBIC,
                                      True,
                                      3,
                                      False)


register(
        "flip_about_path",
        "Arbitrarily flips selection",
        """Flip selection using the two first nodes of current path as the flip axis.
        """,
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2004. GPL applies.",
        "<Image>/Python-Fu/Flip About Path",
        "*",
        [],
        [],
        flip_about_path)

main()
