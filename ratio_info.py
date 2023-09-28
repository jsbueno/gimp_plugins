#!/usr/bin/env python

from gimpfu import *
import gtk
from gobject import timeout_add

# (c) 2004 by Joao S. O. Bueno Calligaris

class RatioWindow(gtk.Window):
    def __init__ (self, img, *args):
        self.img = img
        self.w, self.h = 0, 0
        self.label = gtk.Label()
        r =  gtk.Window.__init__(self, *args)
        self.add(self.label)
        self.label.show()
        self.show()
        timeout_add(200, self.update, self)    
        return r

    def update(self, *args):
        exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds(self.img)
        w = x2 - x1 
        h = y2 -y1
        timeout_add(200, self.update, self)
        if (w, h) == (self.w, self.h) or not h:
            return
        self.w, self. h = w, h
        text = "%d : %d  -  %f" % (w, h , w / float(h))
        self.label.set_text(text)



def ratio_info (img, drw):
    r = RatioWindow(img)
    gtk.main()

register(
         "ratio_info",
         "Shows current selection aspect ratio",
         "Pops up a window with he current selection aspect ratio",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2007",
         "<Image>/Select/Ratio Window",
         "*",
         [],
         [],
         ratio_info)

main()
