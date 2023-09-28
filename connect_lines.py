#!/usr/bin/env python

from gimpfu import *

import math

def connect_lines (img, drw, line_count, reverse1, reverse2):

    try:
        vectors = pdb.gimp_image_get_active_vectors(img)
        strokes = pdb.gimp_vectors_get_strokes(vectors)
        #teh above call returns a 2 tuple - the first item is the lenght of the second,
        #which is a tuple with the stroke IDa  
        if strokes[0] < 2:
            return 
        stroke1, stroke2 = strokes[1]
    except Exception:
        #no selected path.
        return 
    len1 = pdb.gimp_vectors_stroke_get_length(vectors, stroke1, 100.0)
    step1 = len1 / line_count
    len2 = pdb.gimp_vectors_stroke_get_length(vectors, stroke2, 100.0)
    step2 = len2 / line_count

    dist1 = dist2 = 0.0

    img.undo_group_start()
    gimp.progress_init()
    for i in xrange(line_count):
        if reverse1:
            real_dist1 = len1 - dist1
        else:
            real_dist1 = dist1
        if reverse2:
            real_dist2 = len2 - dist2
        else:
            real_dist2 = dist2

        point1 = pdb.gimp_vectors_stroke_get_point_at_dist(vectors, stroke1, real_dist1, 100.0)
        point2 = pdb.gimp_vectors_stroke_get_point_at_dist(vectors, stroke2, real_dist2, 100.0)

        if not point1[-1] or not point2[-1]:
            continue
        pdb.gimp_paintbrush_default(drw, 4, (point1[0], point1[1], point2[0], point2[1]))

        dist1 += step1
        dist2 += step2
        if not i % 10:
            gimp.progress_update(i / float(line_count))

    img.undo_group_end()
    gimp.displays_flush()




register(
         "conect_lines",
         "Connect lines accross two vector components",
         "Connect points at regular intervals between the first two components in a vectors object",
         "Joao S. O. Bueno",
         "GPLv3",
         "2008",
         "<Image>/Python-Fu/Alchemy/Connect Lines",
         "*",
         [
                (PF_INT, "line_count", "How many lines to draw", 20),
                (PF_BOOL, "reverse1", "reverse connecting points in first stroke", False),
                (PF_BOOL, "reverse2", "reverse connecting points in second stroke", False),

                
         ],
         [],
         connect_lines
        )

main()
