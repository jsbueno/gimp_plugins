#!/usr/bin/env python

from gimpfu import *
import gtk
from gobject import timeout_add

# (c) 2008 by Joao S. O. Bueno Calligaris

class LinesWindow(gtk.Window):
    def __init__ (self, img, drw, *args):
        self.img = img
        self.drw = drw
        self.vectors = None
        self.w, self.h = 0, 0
        self.button = gtk.Button("Close Auto Liner")
        r =  gtk.Window.__init__(self, *args)
        self.add(self.button)
        self.button.show()
        self.show()
        timeout_add(50, self.update, self)
        self.button.connect("clicked", self.quit)
        return r

    def update(self, *args):
        vectors = pdb.gimp_image_get_active_vectors(self.img)
        if vectors != self.vectors:
            try:
                origin = vectors.strokes[0].points[0][2:4]
            except IndexError:
                timeout_add(50, self.update, self)
                return
            self.vectors = vectors
            self.origin = origin
            
            self.point_list = set()
        new_points = set()
        x = None
        for stroke in self.vectors.strokes:
            for i, coord in enumerate(stroke.points[0]):
                # x coords of nodes (not handlers):
                if  i % 6 == 2:
                    x = coord
                # y coords of nodes (not handlers):
                elif i % 6 == 3:
                    new_points.add((x, coord))
        new_points.difference_update(self.point_list)
        for point in new_points:
            if point == self.origin:
                continue
            pdb.gimp_paintbrush_default (self.drw,
                                         4, (self.origin[0], self.origin[1], point[0], point[1])
                                        )
        if new_points:
            gimp.displays_flush()
        self.point_list.update(new_points)

        timeout_add(50, self.update, self)
    def quit(self, *args):
        gtk.main_quit()



def connect_vector_nodes (img, drw):


        
    # TODO: add "get_Active_vectors" to gimp.Image objects
    r = LinesWindow(img, drw)
    gtk.main()

register(
         "connect_vector_nodes",
         "Connects each node of a path with the original node in \"real time\"",
         "Keeps an open window, and draws straight lines using current paintbrush settings to the frist node of a vector",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2008",
         "<Image>/Python-Fu/Live connect vector nodes",
         "*",
         [],
         [],
         connect_vector_nodes)

main()
