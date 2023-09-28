#!/usr/bin/python
# -*- coding: utf-8 -*-
#    This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from gimpfu import *
import random
from math import pi



def read_color_array(palette):
        pdb.gimp_progress_init ("Reading Palette", -1)
        num_colors = pdb.gimp_palette_get_info (palette)
        color_array = []
        for i in xrange (num_colors):
            color_array.append  (pdb.gimp_palette_entry_get_color (palette, i))
            if not i % 32:
                pdb.gimp_progress_update (float (i) / num_colors)
        return color_array

def gradient_from_palette (palette,  blending, coloring):
    gradient_name = pdb.gimp_gradient_new (palette)
    last_segment = 0

    colors = read_color_array (palette)
    number_of_segments = len(colors)
    if blending == None:
        number_of_segments += 1

    pdb.gimp_progress_init("Creating new gradient", -1)
    if len (colors) < 1:
        return
    #A new gradient has one new segemtn from white to black
    #for someunknown force of the universe. the call to "gimp...replicate"
    #only accepts up to 20 copies.
    for i in xrange (number_of_segments - 2):
        pdb.gimp_gradient_segment_range_replicate (gradient_name,
                                                    i, -1, 2)
    pdb.gimp_progress_update (0.3)


    pdb.gimp_gradient_segment_range_redistribute_handles (gradient_name, 0, -1)
    if blending != None:
        pdb.gimp_gradient_segment_range_set_blending_function (gradient_name, 0, -1, blending)
        #If the two ends of a segment are on the same color, if the coloring type
        #is any o f the HSV, the segemnt is the whole rainbow
        pdb.gimp_gradient_segment_range_set_coloring_type (gradient_name, 0, -1, coloring)
    else:
        pdb.gimp_gradient_segment_range_set_blending_function (gradient_name, 0, -1,
                                                               GRADIENT_SEGMENT_LINEAR)
        pdb.gimp_gradient_segment_range_set_coloring_type (gradient_name, 0, -1,
                                                           GRADIENT_SEGMENT_RGB)

    if number_of_segments == 1:
        pdb.gimp_gradient_segment_set_right_color (gradient_name, 0, colors[0], 100)
        pdb.gimp_gradient_segment_set_left_color (gradient_name, 0, colors[0], 100)
        return

    for i in xrange (number_of_segments - 1):
        pdb.gimp_gradient_segment_set_left_color (gradient_name, i, colors[i], 100)
        if blending != None:
            pdb.gimp_gradient_segment_set_right_color (gradient_name, i, colors[i + 1], 100)
        else:
            pdb.gimp_gradient_segment_set_right_color (gradient_name, i, colors[i], 100)
        if not i % 10:
            pdb.gimp_progress_update (0.3 + 0.7 * float(i) / len(colors))
    #TODO: try to check for redundant segments.

def palette_from_gradient (gradient, number, segment_colors):
    palette_name = pdb.gimp_palette_new (gradient)
    if not segment_colors:
        colors = pdb.gimp_gradient_get_uniform_samples (gradient, number, False)[1]
        for i in xrange (number):
            pdb.gimp_palette_add_entry (palette_name, "#%d" %i,
                                          (int (colors[i * 4] * 255),
                                           int (colors[i * 4 + 1] * 255),
                                           int (colors[i * 4 + 2] * 255)
                                          )
                                        )
    else:
        #pick colors
        available_colors = number
        colors = []
        mean_step = 1.0 / number
        #GIMP gradient PDB functions lack a way to know the number of
        #segements in a given gradient.
        segments = []
        i = 0
        while True:
            colors_taken = 0
            try:
                left = pdb.gimp_gradient_segment_get_left_pos (gradient, i)

            except:
                break
            segments.append ({"left" : left})
            segments[i]["right"] = pdb.gimp_gradient_segment_get_right_pos (gradient, i)
            segments[i]["l_color"] = pdb.gimp_gradient_segment_get_left_color (gradient, i)[0]
            segments[i]["r_color"] = pdb.gimp_gradient_segment_get_right_color (gradient, i)[0]

            width = segments[i]["right"] - segments[i]["left"]
            segments[i]["width"] = width
            colors_taken  = int (number *  width)
            if colors_taken < 2:
                colors_taken = 2
            segments[i]["colors_taken"] = colors_taken
            available_colors -= colors_taken
            print colors_taken
            i += 1


        for i in xrange(len(segments)):
            segment = segments[i]
            if segment["colors_taken"] > 2 and available_colors < 0:
                available_colors += segment["colors_taken"] - 2
                segment["colors_taken"] = 2
            if available_colors > 0:
                segment["colors_taken"] += 1
                available_colors -= 1
            if i or segment["l_color"] != segments[i-1]["r_color"]:
                segment["colors_taken"] -= 1
                colors.append (segment["l_color"])
            sample_positions = [segment["left"]]
            count = 1
            for j in xrange(segment["colors_taken"] ):
                sample_positions.append (segment["left"] +
                                         count * segment["width"] / segment["colors_taken"])
                count += 1

            middle_colors = pdb.gimp_gradient_get_custom_samples (gradient,
                                                                        len (sample_positions),
                                                                        sample_positions,
                                                                        False)[1]

            for j in xrange (4, len(middle_colors) - 4, 4):
                colors.append ((int (middle_colors[j] * 255),
                                int (middle_colors[j + 1] * 255),
                                int (middle_colors[j + 2] * 255)
                              ))

            colors.append (segment["r_color"])

        for i in xrange (len (colors)):
            pdb.gimp_palette_add_entry (palette_name, "#%d" %i, colors[i])

register(
        "gradient_from_palette",
        "Creates a new gradient from a given palette",
        "gradient_from_palette (palette, blending, coloring) -> None",
        "Joao S. O. Bueno Calligaris",
        "(c) GPL V2.0 or later - J.S.",
        "2004",
        "<Toolbox>/Xtns/Python-Fu/Palettes/Map Palette to Gradient",
        "*",
        [
          (PF_PALETTE, "palette", "Palette to use",""),
          (PF_RADIO, "blending", "Blending function for segments", GRADIENT_SEGMENT_LINEAR,
                   ( ("Linear", GRADIENT_SEGMENT_LINEAR),
                     ("Curved", GRADIENT_SEGMENT_CURVED),
                     ("Sine", GRADIENT_SEGMENT_SINE),
                     ("Spheric Increasing", GRADIENT_SEGMENT_SPHERE_INCREASING),
                     ("Spheric Decreasing", GRADIENT_SEGMENT_SPHERE_DECREASING),
                     ("None", None)
                   )
          ),
          (PF_RADIO, "coloring", "Coloring type for segments", GRADIENT_SEGMENT_RGB,
                   ( ("RGB", GRADIENT_SEGMENT_RGB),
                     ("HSV CW", GRADIENT_SEGMENT_HSV_CW),
                     ("HSV CCW", GRADIENT_SEGMENT_HSV_CCW),
                   ),
           )
        ],
        [],
        gradient_from_palette)
register(
        "palette_from_gradient",
        "Creates a new palette from a given gradient",
        "palette_from_gradient (gradient, number, segment_colors) -> None",
        "Joao S. O. Bueno Calligaris",
        "(c) GPL V2.0 or later - J.S.",
        "2004",
        "<Toolbox>/Xtns/Python-Fu/Palettes/Map Gradient to Palette",
        "",
        [
          (PF_GRADIENT, "gradient", "Gradient to use",""),
          (PF_INT, "number", "Number of colors", 256),
          (PF_TOGGLE, "segment_colors", "Pick exact colors at segment edges?", False)

        ],
        [],
        palette_from_gradient)
main ()