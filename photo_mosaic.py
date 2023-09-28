#/usr/bin/env python
# coding: utf-8

# Copyright Joao S. O. Bueno 2009
# GPL v3.0
#
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


from __future__ import division
from gimpfu import *
import random, math

VERSION = 1.0


# CLARYFIYING: the words "tile" and "shadow" here have nothing to
# do with the internal GIMP objects -
# they just refer to artistic artifacts created in the image


def get_tiles(drw, width_slices, height_slices, tile_spacing, uneven_spacing):
    tile_width = drw.width / width_slices
    tile_height = drw.height / height_slices
    x_total_offset = (width_slices - 1) * tile_spacing
    y_total_offset = (height_slices - 1) * tile_spacing
    
    for y in xrange(height_slices):
        for x in xrange(width_slices):
            orig_off_x = drw.offsets[0] + x * tile_width
            orig_off_y = drw.offsets[1] + y * tile_height
            sel = pdb.gimp_rect_select(
                 drw.image,
                 orig_off_x,
                 orig_off_y,
                 tile_width,
                 tile_height,
                 CHANNEL_OP_REPLACE,
                 False, 0
                )
            new_layer = clone_selection(drw)
            pdb.gimp_selection_none(drw.image)
            if tile_spacing:
                if width_slices > 1:
                    x_adjust = (x_total_offset / (width_slices - 1)) * x - x_total_offset / 2
                    if uneven_spacing:
                        x_adjust += random.uniform(-tile_spacing, tile_spacing) / 2
                else:
                    x_adjust = 0
                if height_slices > 1:
                    y_adjust = (y_total_offset / (height_slices - 1)) * y - y_total_offset / 2
                    if uneven_spacing:
                        y_adjust += random.uniform(-tile_spacing, tile_spacing) / 2
                else:
                    y_adjust = 0
                new_layer.set_offsets(int(orig_off_x + x_adjust), int(orig_off_y + y_adjust))
            yield new_layer


def select_layer_boundaries(drw):
    return pdb.gimp_rect_select(
         drw.image,
         drw.offsets[0],
         drw.offsets[1],
         drw.width,
         drw.height,
         CHANNEL_OP_REPLACE,
         False, 0
       )

def add_frame(drw, width, noise):
    #select tile
    sel = select_layer_boundaries(drw)
    #shrink selection
    pdb.gimp_selection_shrink(drw.image, width)
    # invert seletion
    pdb.gimp_selection_invert(drw.image)
    # disttress selection
    if noise:
        pdb.script_fu_distress_selection(
             drw.image,
             drw,
             127,
             int(width / 3),
             int (width / 3),
             2,
             True, True)
    # fill with bg
    pdb.gimp_edit_fill(drw, BACKGROUND_FILL)
    pdb.gimp_selection_none(drw.image)

def tile_rotate(drw, angle):
    pdb.gimp_selection_none(drw.image)
    pdb.gimp_drawable_transform_rotate_default(
         drw,
         angle,
         True,
         0, 0,
         True,
         TRANSFORM_RESIZE_ADJUST
        )

def consolidate_layers(img, layer_list):
    visible_state = {}
    for layer in img.layers:
        visible_state[layer.tattoo] = layer.visible
        layer.visible = layer in layer_list
    new_layer = pdb.gimp_image_merge_visible_layers(img, EXPAND_AS_NECESSARY)
    for layer in img.layers:
        layer.visible = visible_state.get(layer.tattoo, True)
    return new_layer

def tile_bend(drw, bending):
    drw = pdb.plug_in_curve_bend(
         drw.image ,drw, 0.0, #rotation
         True,   #smoothing
         True,   #antialias
         False,  #work-on-copy
         0,      # curve-type: smooth
         3, [0, .5, 1], 
         3, [.5, bending, .5],
         3, [0, .5, 1], 
         3, [.5, bending, .5], 
         0, [],
         0, []
        )
    return drw

def clone_layer(drw):
    pdb.gimp_selection_all(drw.image)
    return clone_selection(drw)

def clone_selection(drw):
    pdb.gimp_edit_copy(drw)
    fl = pdb.gimp_edit_paste(drw, True)
    pdb.gimp_floating_sel_to_layer(fl)
    return fl
    

def photo_mosaic (img, drw,
    width_slices = 4,
    height_slices = 4,
    border_width = 10, 
    border_noise = False,
    tile_spacing = 10,
    uneven_spacing = False,
    maximum_angle = 5.0,
    bending_factor = 0.1,
    drop_shadow = 5):

    img.undo_group_start()
    tiles = []
    tile_drop_shadows = []

    for tile in get_tiles(drw, width_slices, height_slices, tile_spacing, uneven_spacing):
        add_frame(tile, border_width, border_noise)
        if bending_factor and drop_shadow:
            shadow_source = clone_layer(tile)
        else:
            shadow_source = tile
        if maximum_angle:
            angle = random.uniform(-maximum_angle, maximum_angle) / 180.0 * math.pi / 2
            if shadow_source is not tile:
                tile_rotate(shadow_source, angle)
        if bending_factor:
            bending = random.uniform(0, bending_factor) - bending_factor / 2.0 + 0.5
            tile = tile_bend(tile, bending)
            
        tiles.append(tile)
        tile_rotate(tile, angle)
        if drop_shadow:
            #if bending_factor < 0:
                #TODO: if ending happens, weid piece of shadow shows up
                # on the wrong side- have to clip that off.
            #script_fu_drop_shadow does not return newly created layer :-/
            all_layers = img.layers[:]
            pdb.script_fu_drop_shadow(
                 img, shadow_source,
                 drop_shadow, drop_shadow,
                 drop_shadow * 1.5,
                 (0,0,0),
                 80,
                 False
                )
            tile_shadow = [layer for layer in img.layers if layer not in all_layers][0]
            tile_drop_shadows.append(tile_shadow)
            if bending_factor and bending < 0.5:
                pdb.gimp_selection_layer_alpha(shadow_source)
                pdb.gimp_selection_invert(img)
                pdb.gimp_edit_clear(tile_shadow)
                pdb.gimp_selection_none(img)

        if bending_factor and drop_shadow:
            pdb.gimp_image_remove_layer(img, shadow_source)

    tiles = consolidate_layers(img, tiles)
    tiles.name = "Photo Mosaic"
    if drop_shadow:
        shadows = consolidate_layers(img, tile_drop_shadows)
        shadows.name = "Photo Mosaic Drop Shadows"
        while img.layers.index(tiles) > img.layers.index(shadows):
            pdb.gimp_image_lower_layer(img, shadows)

    drw.visible = False
    img.undo_group_end()
    gimp.displays_flush()
    
register(
         "photo_mosaic",
         "Slice a layer in several tiles, add a frame, bending, spacing and shadow to each one.",
         "Slice a layer in several tiles, add a frame, bending, spacing and shadow to each one.",
         "Joao S. O. Bueno",
         "GPL V3.0 or later",
         "2009",
         "Photo _Mosaic...",
         "*",
         [(PF_IMAGE, "Image", "Image", None),
          (PF_DRAWABLE, "Drawable", "Drawable", None),
          (PF_INT, "width_slices", "How many slices across the layer", 4),
          (PF_INT, "height_slices", "How many slices on the height of the layer", 4),
          (PF_INT, "border_width", "Add background color frame to each tile. 0 for no border", 5),
          (PF_BOOL, "border_noise", "Make uneven edges for the  frame", False),
          (PF_INT, "tile_spacing", "How far apart to space tiles", 10),
          (PF_BOOL, "uneven_spacing", "Randomize tile spacing", False),
          (PF_FLOAT, "maximum_angle", "Maximum rotation angle for each tile. 0 for no rotation", 5.0),
          (PF_FLOAT, "bending_factor", "How much to bend each photo, (0 <= b <= 1.0), 0.2)", 0.1),
          (PF_INT, "drop_shadow", "Drop shadow distance to tiles. Use 0 for no shadow", 5)
         ],
         [],
         photo_mosaic,
         menu = "<Image>/Filters/Artistic/"
        )

main()
