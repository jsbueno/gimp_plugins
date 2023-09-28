#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import pickle

def new_layer_group (img, layer, name):
    group = []
    for layer in img.layers:
       if pdb.gimp_drawable_get_linked (layer):
            group.append (layer.name)
    if not len (group):
        return ""

    parasite = img.parasite_find ("layer_groups")
    if not parasite:
        layer_groups = {}
    else:
        layer_groups = pickle.loads (parasite.data)
    layer_groups[name] =  group
    parasite = gimp.Parasite ("layer_groups", PARASITE_UNDOABLE |
                    PARASITE_PERSISTENT, pickle.dumps (layer_groups) )
    img.parasite_attach (parasite)
    return name

def restore_layer_group (img, layer, name):
    parasite = img.parasite_find ("layer_groups")
    if not parasite:
        return
    layer_groups = pickle.loads (parasite.data)
    if not name in layer_groups:
        return
    for layer in img.layers:
        layer.linked = layer.name in layer_groups [name]



register   (
             "new_layer_group",
             "create a new layer group for active image, using the linked images for that",
             "",
             "Joao S. O. Bueno Calligaris",
             "GPL 2 or later, Joao S. O. Bueno Calligaris",
              "2006",
              "<Image>/Layer/Groups/New",
              "*",
              [
                (PF_STRING, "name", "Name of layer group", "group")
              ],
              [ (PF_STRING, "new_group", "Name of new group") ],
              new_layer_group
            )
register   (
             "restore_layer_group",
             "restores a layer group for the active image",
             "",
             "Joao S. O. Bueno Calligaris",
             "GPL 2 or later, Joao S. O. Bueno Calligaris",
             "2006",
             "<Image>/Layer/Groups/Restore",
             "*",
             [
               (PF_STRING, "name", "Name of layer group", "group")
             ],
             [ ],
             restore_layer_group
           )

main ()
