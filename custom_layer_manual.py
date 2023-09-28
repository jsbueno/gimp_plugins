#!/usr/bin/python
# -*- coding: utf-8 -*-


#To chnage what the plugin does, change the "result = "line, in the inner loop

from gimpfu import *
try:
    import Numarray
except:
    import Numeric as Numarray
    
def min_2 (i, j):
    if i < j:
        return i
    return j
def max_2 (i, j):
    if i > j:
        return i
    return j
def clamp (component, min_, max_):
    if component < min_:
        return min_
    elif component > max_:
        return max_
    return component
    
def clamp_0_255 (component):
    if component < 0:
        return 0
    elif component > 255:
        return 255
    return component
    
def result (p1, p2):
    result = px_1[i,j,k] - px_2 [i,j,k]
    if result < -threshold:
        result = -threshold
    elif result > threshold:
        result = threshold
    result = px_1[i,j,k] + result
    if result > 255:
        result = 255
    elif result < 0:
        result = 0
    dest_pixels[i,j,k] = result
    return result
def custom_layer_op (img, drw, layer_1, layer_2, create_layer, dest_layer, threshold):
    global trheshold
    pdb.gimp_image_undo_group_start(img)
    
    has_alpha = layer_2.has_alpha  
    selection, sx, sy, ex, ey = pdb.gimp_selection_bounds (img)
    if not selection:
        sx = sy = 0
        ex = min (layer_1.width, layer_2.width)
        ey = min (layer_1.height, layer_2.height)
    if create_layer:        
        dest_layer = pdb.gimp_layer_new_from_drawable (layer_2, img)
        img.add_layer (dest_layer)
        dest_layer.set_offsets (layer_2.offsets[0],  layer_2.offsets[1])
        if not has_alpha:
            dest_layer.add_alpha()
            
    width = ex - sx
    height = ey - sy
    
    pixel_region_1 = layer_1.get_pixel_rgn (sx, sy, width, height)
    array_1 = Numarray.array (pixel_region_1[:,:], Numarray.UInt8)
    px_1 = Numarray.reshape (array_1, (width, height, 3 + layer_1.has_alpha))
    
    dest_pixel_region = dest_layer.get_pixel_rgn (sx, sy, width, height)
    dest_array = Numarray.array (dest_pixel_region[:,:], Numarray.UInt8)
    dest_pixels = Numarray.reshape (dest_array, (width, height, 4))
    
    if create_layer:
        array_2 = dest_array
        px_2 = dest_pixels
    else:
        pixel_region_2 = layer_2.get_pixel_rgn (sx, sy, width, height)
        array_2 = Numarray.array (pixel_region_2[:,:], Numarray.UInt8)
        px_2 = Numarray.reshape (array_2, (width, height, 3 + has_alpha))
        
    pdb.gimp_progress_init ("Calculating...", -1)
    for j in xrange (height):
        for i in xrange (width):
            for k in xrange (3):
                dest_pixels[i,j,k] = px_1[i, j, k] ^ px_2 [i, j, k]
                """if not k:
                    result = px_1[i,j,k] - px_2[i,j,2] / 2
                    if px_2[i,j,k] % 2:
                        result = 255 - result
                elif k == 1:
                    result = px_2[i,j,k] + px_2[i,j,k] / 2
                elif k == 2:
                    result = px_1[i,j,0]
                
                if result > 255:
                    result = 255
                elif result < 0:
                    result = 0
                dest_pixels[i,j,k] = result
                
            if has_alpha:
                dest_pixels [i,j,3] = px_2 [i,j,3]
            else:
                dest_pixels [i,j,3] = 255
                """
        if not j % 10:
            pdb.gimp_progress_update (float(j) / height)
 
    #Dest_pixels is just a 'view' of dest_array - so its contents got changed above
    dest_pixel_region[:,:] =  dest_array.tostring()
    dest_layer.update (sx, sy, ex, ey)
    
    pdb.gimp_image_undo_group_end (img)
    pdb.gimp_displays_flush ()
    
register(
        "custom_layer_op",
        "Calculates a third layer based on two source layers",
        "custom_layer_op(img, layer_1, layer_2, create_layer, dest_layer, threshold) -> None",
        "Joao S. O. Bueno Calligaris",
        "(C) Joao S. O. Bueno Calligaris - available exclusively under the GPL. source-code reuse restrictions apply.",
        "2004",
        "<Image>/Python-Fu/Custom Layer Op",
        "RGB*",
        [(PF_LAYER, "layer_1", "Base layer", None),
         (PF_LAYER, "layer_2", "Second Layer", None),
         (PF_TOGGLE, "create_layer", "Create new layer?", True),
         (PF_LAYER, "dest_layer", "Target Layer", None),
         (PF_INT, "threshold", "Threshold value",20)
         
        ],     
        [],
        custom_layer_op)
main ()