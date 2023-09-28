#!/usr/bin/env python

from gimpfu import *
import gtk
from gobject import timeout_add

# (c) 2008 by Joao S. O. Bueno

class ResourceWindow(gtk.Window):
    def __init__ (self,  *args):
        self.w, self.h = 0, 0
        self.layout  = gtk.Layout()
        self.layout.show()
        self.add(self.layout)
        self.label = gtk.Label()
        r =  gtk.Window.__init__(self, *args)
        self.layout.put(self.label, 30, 30)
        self.label.show()
        self.show()
        timeout_add(200, self.update, self)    
        return r

    def update(self, *args):
        
        w = 100
        h = 100
        timeout_add(200, self.update, self)
        if (w, h) == (self.w, self.h) or not h:
            return
        self.w, self. h = w, h
        text = "%d : %d  -  %f" % (w, h , w / float(h))
        self.label.set_text(text)



def tag_manager():
    r = ResourceWindow()
    gtk.main()

register(
         "tag_manager",
         "Opens a dialog for tagged resource management in GIMP",
         "Opens a dialog for tagged resource management in GIMP",
         "Joao S. O. Bueno",
         "GPLv3",
         "2008",
         "<Toolbox>/Xtns/Tagged resource manager",
         "*",
         [],
         [],
         tag_manager)

main()
