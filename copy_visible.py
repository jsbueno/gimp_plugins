#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *

def pyco_visible(img, drw):
    new_image = img.duplicate()
    try:
        new_image.flatten()
    except:
        pass
    layer = new_image.layers[0]
    if not layer.is_indexed:
        values = (0, ) * 256
        for i in  xrange (6):
            if ( 
                    (i == ALPHA_CHANNEL and not layer.has_alpha) or
                    (i <= BLUE_CHANNEL and layer.is_grey ) or
                    (layer.is_gray and (i != GRAY_CHANNEL and i != ALPHA_CHANNEL)) or
                    (i == INDEXED_CHANNEL or (i == GRAY_CHANNEL and not layer.is_gray))
               ):
                continue
            if not new_image.get_component_visible (i):
                #if compoonent is not visble, zero it out using the curves tool
                component = i + 1 #convert constants from GIMP_*_CHANNEL to GIMP_HISTOGRAM_*
                if i == ALPHA_CHANNEL:
                    component = HISTOGRAM_ALPHA
                if i == GRAY_CHANNEL:
                    component = HISTOGRAM_VALUE
                pdb.gimp_curves_explicit ( new_image.layers[0],component, 256, values)
                                         
    pdb.gimp_edit_copy (new_image.layers[0])
    pdb.gimp_image_delete (new_image)
    
    
register(
        "pyco_visible",
        "Copy Image as it is Visible, preserving componet visibility ",
        "pyco_visible (img, drw) -> None",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2004",
        "<Image>/Python-Fu/Py-Copy-Visible",
        "*",
        [],      
        [],
        pyco_visible)
main ()