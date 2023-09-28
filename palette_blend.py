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


def palette_blend(palette, blend_color, strength):
    strength = strength / 100.0
    #verify if given palette is writable
    try:
        pdb.gimp_palette_entry_set_color (palette, 0,
                                          pdb.gimp_palette_entry_get_color (palette, 0)
                                         )
    except:
        palette = pdb.gimp_palette_duplicate (palette)
    num_colors = pdb.gimp_palette_get_info (palette)
    for i in xrange (num_colors):
        color = pdb.gimp_palette_entry_get_color (palette, i)
        color = list (color)
        for j in xrange(3):
            color[j] = int ((1.0 - strength) * color[j] + strength * blend_color[j])
        pdb.gimp_palette_entry_set_color (palette, i, tuple (color))

    return palette

register(
        "Pallette_Blend",
        "Blend all colros in a palette with a given color",
        "palette_blend ( palette, color, strenght) -> modified_palette",
        "Joao S. O. Bueno Calligaris",
        "(C) 2005 - João S. O. Bueno Calligaris - Licensed under GPL",
        "2004",
        "<Toolbox>/Xtns/Python-Fu/Palettes/Blend",
        "*",
        [
         (PF_PALETTE, "palette", "Name of Pallette to rotate", ""),
         (PF_COLOR, "color", "Color with which to blend", (255,255,255) ),
         (PF_SLIDER, "strength", "Blend Strength", 50, (0,100,1))
        ],
        [(PF_PALETTE, "new_palette", "Name of rotated palette")],
        palette_blend)
main ()