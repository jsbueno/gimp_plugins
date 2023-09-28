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


def palette_merge(palette_1, palette_2):

    #While there is no PF_PALLETE, we rather verify if the suplied names do exist:
    palette_list = pdb.gimp_palettes_get_list("")[1]
    if (palette_1 not in palette_list or
        palette_2 not in palette_list):
        raise "You should type existing palette names"
    new_palette = pdb.gimp_palette_duplicate (palette_1)
    new_palette = pdb.gimp_palette_rename (new_palette, "Merged %s and %s"
                                           % (palette_1, palette_2) )
    num_new_colors = pdb.gimp_palette_get_info (palette_2)
    for i in xrange (num_new_colors):
        entry_name = pdb.gimp_palette_entry_get_name (palette_2, i)
        entry_color = pdb.gimp_palette_entry_get_color (palette_2, i)
        new_entry = pdb.gimp_palette_add_entry (new_palette, entry_name, entry_color)
    return new_palette

register(
        "Pallette_Merge",
        "Merge two given palettes",
        "palette_merge (palette_1, palette_2) -> new_palette",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2004",
        "<Toolbox>/Xtns/Python-Fu/Palettes/Merge",
        "*",
        [
         (PF_PALETTE, "palette_1", "Name of first Pallette to merge", ""),
         (PF_PALETTE, "palette_2", "Name of second Pallette to merge", "")
        ],
        [(PF_PALETTE, "new_palette", "Name of merged palette")],
        palette_merge)
main ()