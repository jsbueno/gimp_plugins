#!/usr/bin/env python
# -*- coding: utf-8 -*-


from gimpfu import *

# (c) 2012 by Joao S. O. Bueno

def update_data(data, colors, bpp):
    colors_used = set()
    for pixel_index in xrange(0, len_data, bpp):
        colors
    
    pass


def force_tile_colors (img, layer, t_width, t_height, palette):
    colors_per_tile = 2
    color_map = pdb.gimp_image_get_colormap(img)[1]
    colors = set()
    for index in xrange(0, color_map, 3):
        colors.add(color_map[index:index+3])
    print colors
    
    for y in xrange(0, layer.width, t_width):
        for x in xrange(0, layer.height, t_height):
            region = layer.get_pixel_rgn(x, y, t_width, t_height)
            data = bytearray(region[:,:])
            update_colors(data, colors, bpp)
            region[:,:] = str(data)
            layer.update()


register(
         "force_tile_colors",
         "Reduces the colors used on each image tile",
         "Recomended for forcing image compliance to 8 bit systems",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2012",
         "Force tile colors...",
         "Indexed*",
         [ 
           (PF_IMAGE, "img", "The image", None),
           (PF_DRAWABLE, "layer", "The layer", None),
           (PF_INT, "t_width", "Tile Width", 8),
           (PF_INT, "t_height", "Tile Height", 8),
           (PF_PALETTE, "palette", "Palette to use", "Paintjet")
         ],
         [],
         force_tile_colors,
         menu="<Image>/Colors/")

main()
