#!/usr/bin/python
#-*- coding: utf-8 -*-
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
#Version 0.2 alpha

from gimpfu import *
import gtk
import pickle
import random

def count (text, str_):
    c = 0
    i = text.find (str_)
    while i != -1:
        c += 1
        text = text [i + len (str_):]
        i = text.find (str_)
    return c

def combine_layer_list (img, layer_list):
    visible_dict = {}
    for layer in img.layers:
        visible_dict[layer.name] = layer.visible
        if layer in layer_list:
            layer.visible = True
        else:
            layer.visible = False
    merged_layer = pdb.gimp_image_merge_visible_layers (img, EXPAND_AS_NECESSARY)
    for layer in img.layers:
        layer.visible = visible_dict[layer.name]
    return merged_layer

class RichText (object):
    def __init__ (self, img, drw, font, font_size, color):
        self.img = img
        self.drw = drw
        self.font =  font
        self.size = font_size
        self.color = color
        self.create_window ()
        self.layer = None
        self.apply_now = False
        self.our_layer = None
        self.justify = gtk.JUSTIFY_LEFT
        
    def get_text (self):
        text = []
        i0 = self.tb.get_start_iter()
        begin = True
        chars = []
        old_dict_tag = {}
        while True:
            if begin:
                tags = i0.get_tags ()
            if begin or i0.get_toggled_tags (True) or i0.get_toggled_tags (False) or (chars and chars [-1] == "\n") or i0.is_end():
                begin = False
                if chars:
                    dict_tag = {}
                    if tags:
                        for tag in tags:
                            if tag.get_property("foreground-set"):
                                dict_tag["color"] = self._gdk_to_gimp (
                                tag.get_property("foreground-gdk"))
                            if tag.get_property("family-set"):
                                dict_tag["font"] = tag.get_property("font")
                                ratio = tag.get_data("ratio")
                                if ratio is not None:
                                    dict_tag["ratio"] = float(tag.get_data("ratio"))
                                print dict_tag["ratio"]

                    textstr = "".join (chars)
                    if  (text and text[-1][0] and text[-1][0][-1] != "\n" and
                        old_dict_tag == dict_tag):
                        text[-1] = (text[-1][0] + textstr, text[-1][1])

                    else:
                        text.append ((textstr, dict_tag))
                    old_dict_tag = dict_tag
                    chars = []
                tags = i0.get_tags ()
            chars.append (i0.get_char ())
            if i0.is_end ():
                break
            i0.forward_char ()
        return text

    def set_text (self, data):
        text_tuples = data [0]
        self.justify = data [1]
        self.width_adj.set_value (data[2])

        self.apply_now = False
        i0 = self.tb.get_start_iter ()
        for textstr, tags in text_tuples:
            off_1 = i0.get_offset()
            self.tb.insert (i0, textstr)
            if tags:
                tags = tags.copy ()
                if tags.has_key("color"):
                    tags["foreground-gdk"] = self._gimp_to_gdk (tags["color"])
                    del tags["color"]
                if tags.has_key ("ratio"):
                    ratio = str(tags["ratio"])
                    del tags["ratio"]
                else:
                    ratio = None
                tag = self.tb.create_tag (None, **tags)
                if ratio is not None:
                    tag.set_data ("ratio", ratio)
                i1 = self.tb.get_iter_at_offset (off_1)
                self.tb.apply_tag (tag, i1, i0)
        self._change_justify ()

    def do_it (self, *a):
        layers = []
        text_tuples = self.get_text ()
        #points to pixels:
        #print text_tuples

        at_line = 0
        x = 0
        new_line = False
        line_heights = []
        line_height = 0
        this_line_height = 0
        start_x = int (self.img.height // 2)
        start_y = int (self.img.height // 2)

        print text_tuples
        
        for text, dict_tag in text_tuples :

            if not dict_tag.has_key("font"):
                font = self.get_font()
                size = self.get_font_size ()
            else:
                font = dict_tag["font"].rsplit(" ",1)[0]
                size = int(dict_tag["font"].rsplit(" ",1)[1])
            line_height = max (line_height, 1.0 / 72 * self.img.resolution[1] * size)
            if text[-1] == "\n":
                line_heights.append (line_height)
                print text, line_height
                line_height = 0
        if text[-1] != "\n":
            line_heights.append (line_height)

        for text, dict_tag in text_tuples :
            if new_line:
                last_line_height = this_line_height
                this_line_height = 0
                at_line += 1
                x = 0
            if text[-1] == "\n":
                new_line = True
                text = text [:-1]
            else:
                new_line = False

            if not dict_tag.has_key("color"):
                pdb.gimp_context_set_foreground (self.color)
            else:
                pdb.gimp_context_set_foreground (dict_tag["color"])
            if not dict_tag.has_key("font"):
                font = self.font
                size = self.size
            else:
                font = dict_tag["font"].rsplit(" ",1)[0]
                size = int(dict_tag["font"].rsplit(" ",1)[1])
            x_pixel_size = 1.0 / 72 * self.img.resolution[0] * size
            y_pixel_size = 1.0 / 72 * self.img.resolution[1] * size

            #for centered text: (buggy)    
            #x = int (self.img.width // 2 - x_pixel_size * len (text) // 2)
            y = start_y + sum(line_heights[0:at_line])
            #for vertical-alignment at the text base:
            y += line_heights[at_line] - (1.0 / 72 * self.img.resolution[1] * size)
            #Work Around: gimp-text-fontname is ignoring
            #pixels/points font size unit parameter
            # (25/06/2006)

            max_width = self.width_adj.get_value ()
            ok = False
            text_pieces = text.split()
            while not ok:
                if not self.justify == gtk.JUSTIFY_FILL:
                    layer =   pdb.gimp_text_fontname (self.img, None,
                        x, y,
                        text, 0, True,
                        #size, POINTS,
                        size / 72.0 * self.img.resolution[0],
                        PIXELS,
                        font )
                        if x + layer.width < max_width or not " " in text:
                            layers.append (layer)
                            x += layer.width
                            break
                text_pieces = text.split()
                pdb.gimp_image_remove_layer(self.img, layer)
                layer_lines = []
                layers_in_this_line = []
                this_line_height = 0
                block_height = 0

                tmp =  pdb.gimp_text_get_extents_fontname (
                    " ",
                    size / 72.0 * self.img.resolution[0],
                    PIXELS,
                    font)
                space_width = tmp[0]
                if self.justify == gtk.JUSTIFY_FILL:
                    space_width /= 2.0
                    
                for text_piece in text_pieces:

                    layer =  pdb.gimp_text_fontname (self.img, None,
                        x, y,
                        text_piece, 0, True,
                        #size, POINTS,
                        size / 72.0 * self.img.resolution[0],
                        PIXELS,
                        font)
                        if x + layer.width <= max_width:
                            layers_in_this_line.append (layer)
                            x += layer.width + space_width
                            this_line_height = max (this_line_height, layer.height)
                        else:
                            block_height += this_line_height
                            layer_lines.append (layers_in_this_line)
                            layers_in_this_line = 0
                            
                            


        new_layer = combine_layer_list (self.img, layers)
        if not self.our_layer is None:
            offsets = self.our_layer.offsets
            try:
                pdb.gimp_image_remove_layer(self.img, self.our_layer)
            except RunTimeError:
                pass
        else:
            offsets = (start_x, start_y)
        self.our_layer = new_layer
        # "0" is added to the justify value because gEnums are not pickable
        
        self.our_layer.attach_new_parasite ("pyrichtext", True,
                                            pickle.dumps(
                                                (text_tuples, self.justify + 0,
                                                 self.width_adj.get_value())
                                            , 0))
        self.our_layer.set_offsets (*offsets)

        pdb.gimp_displays_flush()
        
    def _selection_iters (self):
        sel = self.tb.get_selection_bounds ()
        if sel:
            i1, i2 = sel
        else:
            i1 = i2 = self.tb.get_iter_at_mark (self.tb.get_insert())
            
        return i1, i2
        
    def color_changed (self, *par):
        if not self.tb.get_selection_bounds ():
            self.set_at_next_stroke = True
            return
        colortag = self.tb.create_tag (None, foreground_gdk = self.color_button.get_color())
        i1, i2 = self._selection_iters()
        self.tb.apply_tag (colortag, i1, i2)

    def font_changed (self, *par):
        if not self.tb.get_selection_bounds ():
            self.set_at_next_stroke = True
            return
        fonttag = self.tb.create_tag (None, font = self.font_button.get_font_name ())
        fonttag.set_data ("ratio", str (self.ratio_adj.get_value ()))
        i1, i2 = self._selection_iters()
        self.tb.apply_tag (fonttag, i1, i2)

    def create_justify_buttons (self):
        h1 = gtk.HBox()
        self.just_buttons = {}

        for justify, image in zip (
            (gtk.JUSTIFY_LEFT, gtk.JUSTIFY_CENTER, gtk.JUSTIFY_FILL, gtk.JUSTIFY_RIGHT),
            (gtk.STOCK_JUSTIFY_LEFT, gtk.STOCK_JUSTIFY_CENTER, gtk.STOCK_JUSTIFY_FILL, gtk.STOCK_JUSTIFY_RIGHT)
            ):
                
            self.just_buttons[justify] = b = gtk.Button()
            i = gtk.image_new_from_stock (image, gtk.ICON_SIZE_LARGE_TOOLBAR)
            i.show ()
            b.add (i)
            h1.pack_start (b, FALSE, FALSE, 2)
            b.show ()
            b.connect ("clicked", self.justify_button, justify)

        h1.show()

        return h1

    def create_window(self):
        self.w =gtk.Window ()
        self.w.show ()
        h = gtk.HBox ()
        self.color_button = gtk.ColorButton ()
        self.color_button.show ()

        self.color_button.set_color (self._gimp_to_gdk (self.color))
        h.pack_start (self.color_button,False, False, 6)
        self.color_button.connect ("color-set", self.color_changed)
        
        self.font_button = gtk.FontButton ()
        h.pack_start (self.font_button, False, False, 6)
        self.font_button.show ()
        self.font_button.set_font_name ("%s %s" % (self.font, self.size))
        self.font_button.connect ("font-set", self.font_changed)

        h2 = gtk.HBox ()
        l = gtk.Label ("Ratio:")
        l.show ()
        h2.pack_start (l, False, False, 2)
        self.ratio_adj = gtk.Adjustment (1.0, 0.1, 10, 0.1)
        sb = gtk.SpinButton (self.ratio_adj)
        sb.set_digits (1)
        sb.show ()
        h2.pack_start (sb, False, False, 2)
        h2.show ()
        h.pack_start (h2, False, False, 6)


        h1 = self.create_justify_buttons ()
        h1.set_border_width (1)
        h.pack_start (h1, False, False, 6)

        h2 = gtk.HBox ()
        l = gtk.Label ("Width:")
        l.show ()
        h2.pack_start (l, False, False, 2)
        self.width_adj = gtk.Adjustment (400, 1, 3000, 10)
        sb = gtk.SpinButton (self.width_adj)
        sb.show ()
        h2.pack_start (sb, False, False, 2)
        h2.show ()

        h.pack_start (h2, False, False, 6)
        h.show ()

        self.t = gtk.TextView ()
        self.tb = gtk.TextBuffer ()
        self.t.set_buffer (self.tb)
        self.t.show ()
        self.t.set_wrap_mode (gtk.WRAP_WORD)
        
        self.tb.connect ("insert-text", self.inserting_text)
        self.tb.connect ("changed", self.apply_tags)
        
        self.b = gtk.Button (label="Ok")
        self.b.connect ('clicked', self.do_it)
        self.b.show ()
        
        v = gtk.VBox()
        v.pack_start (h, False, False, 6)
        v.pack_start(self.t, True, True, 6)
        v.pack_end (self.b, False, False, 6)
        self.w.add(v)

        v.show ()
        
    def justify_button (self, widget, justification):
        self.justify = justification

        self._change_justify()

    def _change_justify (self):
        i0 = self.tb.get_start_iter()
        i1 = self.tb.get_end_iter()
        tag = self.tb.create_tag (None, justification = self.justify)
        self.tb.apply_tag (tag, i0, i1)
        for j in self.just_buttons:
            if j != self.justify:
                self.just_buttons[j].set_relief (gtk.RELIEF_NORMAL)
            else:
                self.just_buttons[j].set_relief (gtk.RELIEF_NONE)

        
    def inserting_text (self, tb, i1, text, length):
        tags = i1.get_tags()
        for tag in tags:
            if (tag.get_property("foreground-gdk") == self.color_button.get_color()
                and
                tag.get_property("font") == self.font_button.get_font_name()):
                return
        self.apn_where = i1.get_offset()
        self.apn_length = length
        self.apply_now = True
    def apply_tags (self, *a):
        if not self.apply_now:
            return
        tag = self.tb.create_tag (None, font = self.font_button.get_font_name (),
                                  foreground_gdk = self.color_button.get_color ())
        tag.set_data ("ratio", str (self.ratio_adj.get_value ()))
                                  
        i1 = self.tb.get_iter_at_offset (self.apn_where)
        i2 = i1.copy()
        i2.forward_chars (self.apn_length)
        self.tb.apply_tag (tag, i1, i2)
        self.apply_now = False
        
    def _gimp_to_gdk (self, color):
        return gtk.gdk.Color (
                *[comp + (comp << 8) for comp in color[0:3]])
    def _gdk_to_gimp (self, color):
        return  (color.red  >> 8, color.green >> 8, color.blue >> 8)
    def get_color (self):
        return self._gdk_to_gimp (self.color_button.get_color())
    def get_font (self):
        font = self.font_button.get_font_name ()
        return font.rsplit (" ", 1)[0]
    def get_font_size (self):
        font = self.font_button.get_font_name ()
        return int (font.rsplit (" ", 1)[1])
    def set_font_name (self, new_name):
        old_name, size  = self.font_button.get_font_name ().rsplit (" ", 1)
        self.font_button.set_font_name ("%s %s" % (new_name, size))
    def set_font_size (self, new_size):
        name, old_size  = self.font_button.get_font_name ().rsplit (" ", 1)
        self.font_button.set_font_name ("%s %s" % (name, new_size))


def richtext(img, drw):
    """
    """
    gtk.rc_parse(gimp.gtkrc())
    #tehre is no way to rretireve gimp context font size, fort the time being
    # 2006-10-13
    w = RichText (img, drw,
                  pdb.gimp_context_get_font(), 12,
                  pdb.gimp_context_get_foreground())
    if "pyrichtext" in drw.parasite_list():
        text_tuple = pickle.loads(drw.parasite_find ("pyrichtext").data)
        w.our_layer = drw
        w.set_text (text_tuple)

    gtk.main ()

register(
        "richtext",
        "Hacks around some richtext edition for gimp 2.2",
        """Heh! That is it! Version 02 alpha
        """,
        "Joao S. O. Bueno Calligaris",
        "Joao S. O. Bueno Calligaris",
        "2006. GPL applies.",
        "<Image>/Filters/Render/Rich Text...",
        "*",
        [],
        [],
        richtext)

main()
