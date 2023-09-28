#!/usr/bin/env python
# coding: utf-8

# Author: João Sebastião de Oliveira Bueno
# Copyright: João S. O. Bueno (2009), licensed under the GPL v 3.0

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function

VERSION = 1.0
from gimpfu import *

import os


def phrase_brush(font_name, font_size, text):
    BRUSH_DIR = pdb.gimp_gimprc_query("brush-path-writable")
    pdb.gimp_context_push()
    pdb.gimp_context_set_default_colors()
    
    padding = font_size // 4
    img = gimp.Image(font_size + padding, font_size + padding, GRAY)
    img.undo_freeze()
    
    text = text.decode("utf-8")
    for letter in reversed(text):
        layer = img.new_layer(fill_mode=BACKGROUND_FILL)
        text_floating_sel = pdb.gimp_text_fontname(img, layer, 
                                                   padding //2, padding // 2,
                                                   letter.encode("utf-8"), 0 ,
                                                   True, font_size, PIXELS, 
                                                   font_name)
        if text_floating_sel: #whitespace don't genrate a floating sel.
            pdb.gimp_edit_bucket_fill(text_floating_sel,
                                  FG_BUCKET_FILL,
                                  NORMAL_MODE, 100, 1.0,
                                  False,0 ,0)
            pdb.gimp_floating_sel_anchor(text_floating_sel)

    file_name = (text.lower().replace(u" ", u"_") + u".gih").encode("utf-8")
    file_path = os.path.join(BRUSH_DIR, file_name)
    print (file_name, file_path)
    
    pdb.file_gih_save(img, img.layers[0], 
                      file_path, file_path, 
                      100, #spacing
                      text, #description,
                      img.width, img.height,
                      1, 1,
                      1, #dimension
                      [len(text)], #rank - number of cells 
                      1, #dimensio again - actually size for teh array of the selection mode
                      ["incremental"])
                      
                      
    pdb.gimp_brushes_refresh()
    pdb.gimp_image_delete(img)
    pdb.gimp_context_pop()
    #img.undo_thaw()
    #pdb.gimp_display_new(img)
    

register(
         "phrase_brush",
         "Creates  a new brush with letters forming a phrase",
         "Creates  a new brush with letters forming a phrase",
         "Joao S. O. Bueno",
         "Copyright Joao S.O. Bueno 2009. GPL v3.0",
         "2009",
         "New _Brush with Phrase...",
         "",
         [
                (PF_FONT, "font", "Font","Sans"),
                (PF_INT, "size", "Pixel Size", 50),
                (PF_STRING, "text", "text", "The GNU Image Manipulation Program")
         ],
         [],
         phrase_brush,
         menu="<Image>/File/Create")

main()
