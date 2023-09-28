#!/usr/bin/env python

from gimpfu import *

import math

def cross_stroke (img, drw, length, step, number_spikes,
                  star = False,
                  fade = False,
                  gradient = False):

    try:
        pathname=pdb.gimp_path_get_current (img)
    except:
        #no selected path.
        return 0
    pdb.gimp_image_undo_group_start (img)
    if number_spikes == 0:
            number_spikes = 1
    dist = 0
    x = y = 1
    if not star:
        j = 0
    while x !=0 and y !=0:
        #while undocumented, gimp_path_get_point_at_dist return (0,0) as coord when
        #the path is over (gmp 2.2 - in gimp 1.2 it would just generate an exception)
        x,y, slope = pdb.gimp_path_get_point_at_dist (img, dist)
        if y == 0 and x == 0:
            break
        if slope == 0:
            slope += 1e-4

        angle = math.atan (slope) - math.pi / 2

        def stroke ():
            x1 = x + length * math.cos (angle)
            y1 = y + length * math.sin (angle)
            pdb.gimp_paintbrush (drw, fade * length, 4,
                                (x,y, x1,y1), True,
                                 gradient * length)

        if star:
            for i in xrange (number_spikes):
                stroke ()
                angle += 2 * math.pi / number_spikes
        else:
            angle += j * 2 * math.pi / number_spikes
            stroke ()
            j += 1
        dist += step

    pdb.gimp_image_undo_group_end (img)




register(
         "cross_stroke",
         "Crossed Path Stroker",
         "Strokes paths in perpendicular and other newish ways",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2005",
         "<Image>/Python-Fu/Alchemy/Cross Stroke",
         "*",
         [
                (PF_INT, "length", "Stroke length", 100),
                (PF_INT, "step", "How many pixels between strokes", 30),
                (PF_INT, "number_spikes", "How many spikes", 2),
                (PF_BOOL,"star", "All strokes from a single point?", True),
                (PF_BOOL, "fade", "Fade strokes?", True),
                (PF_BOOL, "gradient", "Use gradient colors?", False)
         ],
         [],
         cross_stroke)

main()
