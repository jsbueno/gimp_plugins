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

from math import sqrt


def circle_by_3_points(img, drw):
    """
    Traces a circular selectiona about the first three control nodes of
    the active path.
    """
    #no need for undo grouos, since a single opertaion is performed on the image.
    try:
        pathname=pdb.gimp_path_get_current (img)
    except:
        return 0

    path=pdb.gimp_path_get_points (img, pathname)
    path=list(path)

    path_points = list(path[3])
    numpoints=path[2]
    if path[2] < 20:
        return 0

    x1 = path_points[0]
    y1 = path_points[1]

    x2 = path_points[9]
    y2 = path_points[10]

    x3 = path_points [18]
    y3 = path_points [19]

    #now comes a complicated second degree  3 incognite
    #system I  isolated by hand.
    #Just have in mind that:
    # (x1 - cx) ^ 2  + (y1 - cy) ^ 2 == r ^ 2 , and so on for the other points

    B = x3 ** 2 + y3 ** 2 - x1 ** 2 - y1 ** 2
    C = x2  ** 2 + y2 ** 2 - x1 ** 2 - y1 ** 2
    D = x2 - x1
    E = (y2 - y1) * ( x3 - x1)

    cy = (B * D + C * (x1 - x3)) / (2 * (D * (y3 - y1) - E))
    cx = (C - 2 * cy * (y2 - y1)) / (2 * D)
    r = sqrt ((x1 - cx) ** 2 + (y1 - cy) ** 2)

    x = cx -  r
    y = cy -  r

    pdb.gimp_ellipse_select (img, x, y, 2 * r, 2 * r,
                             CHANNEL_OP_REPLACE,
                             True,
                             False,
                             0
                            )




register(
        "circle_by_3_points",
        "Makes a circular selection usign the first three nodes of the current path.",
        """Makes a circular selection usign the first three nodes of the current path.
        """,
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2004. GPL applies.",
        "<Image>/Python-Fu/Circle by 3 Points",
        "*",
        [],
        [],
        circle_by_3_points)

main()
