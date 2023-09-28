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


def palette_offset (amount, forward):
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
    if not forward:
        amount = num_colors - amount

    tmp_entry_array = []
    for i in xrange (num_colors):
        tmp_entry_array.append  ((pdb.gimp_palette_entry_get_name (palette, i),
                                  pdb.gimp_palette_entry_get_color (palette, i))
                                )
    for i in xrange (num_colors):
        target_index = i + amount
        if target_index >= num_colors:
            target_index -= num_colors
        elif target_index < 0:
            target_index += num_colors
        pdb.gimp_palette_entry_set_name (palette, target_index, tmp_entry_array[i][0])
        pdb.gimp_palette_entry_set_color (palette, target_index, tmp_entry_array[i][1])
    return palette

register(
        "Pallette_Offset",
        "Offsets a given palette, ",
        "palette_offset ( palette, amount_to_offset) -> modified_palette",
        "Joao S. O. Bueno Calligaris",
        "(c) Joao S. O. Bueno Calligaris",
        "2004",
        "<Palettes>/Offset",
        "*",
        [
         #(PF_PALETTE, "palette", "Name of Pallette to offset", ""),
         (PF_INT, "amount", "Amount of colors to offset", ""),
         (PF_BOOL, "forward", "Offset the palette forward?", True)
        ],
        [(PF_PALETTE, "new_palette", "Name of offset palette")],
        palette_offset)
main ()