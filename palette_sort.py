#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

#conversion code straight from
# http://www.easyrgb.com/math.php?MATH=M21#text21

#as soom as GIM:PFU allows for PDB registering without adding
#functions to a menu, register these two.
from gimpfu import *

def rgb2hsv (R, G = 0,B = 0):
    if isinstance (R, tuple):
        G = R[1]
        B = R[2]
        R = R[0]

    if not (isinstance (R, float) or isinstance (G, float) or isinstance (B, float)):
        var_R = (R / 255.0 )
        var_G = (G / 255.0 )
        var_B = (B / 255.0 )
    else:
        var_R = R
        var_G = G
        var_B = B

    var_Min = min(var_R, var_G, var_B )   #Min. value of RGB
    var_Max = max(var_R, var_G, var_B )   #Max. value of RGB
    del_Max = var_Max - var_Min            #Delta RGB value

    V = var_Max

    if del_Max == 0:                     #This is a gray, no chroma...
        H = 0                            #HSV results = From 0 to 1
        S = 0
    else:                                #Chromatic data...
        S = del_Max / var_Max

        del_R = ( ( ( var_Max - var_R ) / 6.0 ) + ( del_Max / 2.0 ) ) / del_Max
        del_G = ( ( ( var_Max - var_G ) / 6.0 ) + ( del_Max / 2.0 ) ) / del_Max
        del_B = ( ( ( var_Max - var_B ) / 6.0 ) + ( del_Max / 2.0 ) ) / del_Max

        if  var_R == var_Max:
             H = del_B - del_G
        elif var_G == var_Max:
            H = (1 / 3.0 ) + del_R - del_B
        elif var_B == var_Max:
            H = (2 / 3.0 ) + del_G - del_R

        if  H < 0  : H += 1
        if  H > 1  : H -= 1
    return (H,S,V)


def hsv2rgb (H, S = 0, V = 0):
    if isinstance (H, tuple):
        S = H[1]
        V = H[2]
        H = H[0]

    if S == 0:                       #HSV values = From 0 to 1
        R = V * 255                  #RGB results = From 0 to 255
        G = V * 255
        B = V * 255
    else:
        var_h = H * 6
        var_i = int (var_h)             #Or ... var_i = floor( var_h )
        var_1 = V * ( 1 - S )
        var_2 = V * ( 1 - S * ( var_h - var_i ) )
        var_3 = V * ( 1 - S * ( 1 - ( var_h - var_i ) ) )

        if var_i == 0:
            var_r = V; var_g = var_3; var_b = var_1
        elif  var_i == 1:
            var_r = var_2; var_g = V; var_b = var_1
        elif  var_i == 2:
            var_r = var_1; var_g = V; var_b = var_3
        elif var_i == 3:
            var_r = var_1; var_g = var_2; var_b = V
        elif var_i == 4:
            var_r = var_3; var_g = var_1; var_b = V
        else:
            var_r = V; var_g = var_1; var_b = var_2

    R = int (var_r * 255)                  #RGB results = From 0 to 255
    G = int (var_g * 255)
    B = int (var_b * 255)
    return (R,G,B)

def palette_sort (model, channel, ascending):
    #FIXME: before GIMP 2.4, the palette will come up as first argument from
    #the palette context menu
    palette = pdb.gimp_context_get_palette ()

    #If palette is read only, work on a copy:
    try:
        pdb.gimp_palette_entry_set_color (palette, 0,
                                          pdb.gimp_palette_entry_get_color (palette, 0)
                                         )
    except:
        palette = pdb.gimp_palette_duplicate (palette)
    num_colors = pdb.gimp_palette_get_info (palette)
    entry_list = []
    for i in xrange (num_colors):
        entry =  (pdb.gimp_palette_entry_get_name (palette, i),
                  pdb.gimp_palette_entry_get_color (palette, i)
                 )
        index = entry[1][channel]
        if model == "HSV":
            index = rgb2hsv (entry[1])[channel]
        else:
            index = entry[1][channel]
        entry_list.append ((index, entry))
    entry_list.sort()
    if not ascending:
        entry_list.reverse()
    for i in xrange(num_colors):
        pdb.gimp_palette_entry_set_name (palette, i, entry_list[i][1][0])
        pdb.gimp_palette_entry_set_color (palette, i, entry_list[i][1][1])

    return palette


register(
    "palette_Sort",
    "Sort a palette by either one of the RGB or one of the HSV components ",
    """
       You can sort a palette by either of its color components in either RGB or HSV color models. Beware that if the palette is not write only, it is overwritten, and there is no undo operation for this. If the palette is read only, a new copy is created.
    """,
    "Joao S. O. Bueno Calligaris",
    "(C) João S. O. Bueno Calligaris",
    "2004",
    "<Palettes>/Sort",
    "",
    [
        #(PF_PALETTE, "palette", "Name of palette to Sort", ""),
        #change in python fu for something nicer:
        #(PF_RADIO, "model", "Color model to sort in  ", "RGB",
        #            (("RGB", "RGB"), ("HSV", "HSV"))),
        (PF_RADIO, "model", "Color model to sort in  ", "RGB",
                    ("RGB", "HSV")),


        (PF_RADIO, "channel", "Channel to sort", 0,
                   (("Red/Hue", 0), ("Green/Sat.", 1), ("Blue/Val.", 2))),
        (PF_BOOL, "ascending", "Sort in ascending order", 1)
    ],
    [(PF_PALETTE, "new_palette", "Name of sorted palette")],
    palette_sort)
main ()
