#!/usr/bin/python
#-*- coding: utf-8 -*-
#script by Joao S. O. Bueno Calligaris (c) 2004
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import struct, zlib


from sys import argv, exit
import os
from copy import copy


def png_index_alpha (file_in, palette, file_out):


    file = open (file_in, "r")


    data = file.read()
    init = data.find ("tRNS")
    pre_gap = -1
    pos_gap = 8
    data_out_pad = ""
    if init != -1:
        transp_len = ord (data[init - 1])
        if transp_len == 0:
            if data[init  -2] == 1:
                transp_len = 256
            else:
                print ("Could not determine transparent chunk size on original file")
                exit()
    else:
        init = data.find ("IDAT")
        init -= 4
        pre_gap = 0
        pos_gap = 0
        transp_len = 0
        data_out_pad += "\x00\x00"
    data_out = data [0: init - pre_gap] + data_out_pad

    transp_chunk = "tRNS" + palette
    crc = zlib.crc32 (transp_chunk)
    s_crc = struct.pack (">i", crc )
    transp_chunk += s_crc
    if len(palette) == 256:
        data_out += "\x01\x00"
    else:
        data_out += "\x00" + chr (len(palette))
    data_out += transp_chunk
    data_out += data [init + transp_len + pos_gap:]
    file_out = open (file_out, "w")
    file_out.write (data_out)
    file_out.close()

def save_png_indexed_alpha (image, drw, name, number, limit):
    if limit < 3:
        raise ("Use normal save as PNG on indexed image instead")
    img = duplicate_flatten (image)
    indexed_img = img.duplicate ()
    #zero out transp information,avoiding that convertion to indexed
    #mode spoils RGB information, by mixng white with translucent colors.
    pdb.gimp_curves_explicit ( indexed_img.layers[0], HISTOGRAM_ALPHA, 256, (255,) * 256)
    pdb.gimp_image_convert_indexed (indexed_img,
                                    NO_DITHER,
                                    MAKE_PALETTE,
                                    number, False, False, "")
    #actually, we do not even want alpha information on the indexed image:
    try:
        indexed_img.flatten()
    except:
        pass

    #Now we sample the image, checking for each pixel it's initial alpha value.
    #results are stored in a data structure wich contains the indexed as an index,
    #for each indexed color, a list with tuples - in each tuple, the
    #first number is the alpha value, teh second, the number of pixels using
    #that alpha value, the third, a list of tuples containing every pixel
    #with that value

    #This may become BIG and __SLOW__
    width = img.width
    height = img.height
    index_pr = indexed_img.layers[0].get_pixel_rgn (0 , 0, width, height)
    rgb_pr = img.layers[0].get_pixel_rgn (0 , 0, width, height)

    full_data = [None] * 256

    pdb.gimp_progress_init("Counting Alpha Levels", -1)
    total_colors = 0
    full_transp = None

    for j in xrange (height):
        for i in xrange (width):
            this_index = ord(index_pr [i,j][0])
            this_alpha = ord(rgb_pr [i,j][3])
            if this_alpha == 0:
                #Join all fully transparent pixels into a single entry.
                if full_transp == None:
                    full_transp = this_index
                else:
                    this_index = full_transp
            if not full_data [this_index]:
                full_data[this_index] = {}
            if not full_data[this_index].has_key (this_alpha):
                #full_data[this_index][this_alpha] = [0,[(i, j)]]
                full_data[this_index][this_alpha] = [None,None]]
                total_colors += 1
            #else:
                #full_data[this_index][this_alpha][0] += 1
                #full_data[this_index][this_alpha][1].append ((i,j))
        if not j % 10:
            pdb.gimp_progress_update (float (j) / height)
            print j

        if total_colors >= 256:
            total_colors_retry = 0
            for index in xrange (len (full_data)):
                if not full_data[index]:
                    continue
                if len(full_data[index]) <= limit:
                    total_colors_retry += len(full_data[index])
                else:
                    full_data[index] = compact_alpha_levels (full_data[index], limit)
                    total_colors_retry += len(full_data[index])
            if total_colors_retry >=256:

                pdb.file_png_save2 (1, indexed_img, indexed_img.layers[0],
                                         name, name, False, 9, False, True, False,
                                         True, True, True, False)


                raise "Total number of colors exceeded 256.File saved with no transp.. Try with less colors or alpha levels."

    num_indexes, original_colormap = pdb.gimp_image_get_colormap (indexed_img)
    #and convert it into a usefull object - a list of one tuple for each color:
    colormap = pack_colormap (original_colormap)
    final_transp_levels = [None] * 256
    for index in xrange(num_indexes):
        count = 0
        if full_data[index] == None:
            break
        for transp_level in full_data[index].keys():
            color_entry = full_data[index][transp_level]
            if count == 0:
                color_entry[0] = index
                final_transp_levels[index] = transp_level
                count += 1
            else:
                colormap.append (copy (colormap[index]))
                color_entry[0] = len(colormap) - 1
                final_transp_levels [len (colormap) - 1] = transp_level
    new_colormap = unpack_colormap(colormap)
    pdb.gimp_image_set_colormap (indexed_img, len (new_colormap), new_colormap)
    pdb.gimp_progress_init("Remapping image", -1)
    progress_step = 1.0 / num_indexes
    progress = 0
    #my God..this will take ___long___


    for color in full_data:
        if  color == None:
            break
        for color_entry in color:
            color_str = chr(color[color_entry][0])
            for pixel in color[color_entry][1]:
                index_pr[pixel] = color_str
        progress += progress_step
        pdb.gimp_progress_update (progress)


    #save tmp file with no transp. information:
    temp_name = pdb.gimp_temp_name ("png")

    pdb.file_png_save2 (indexed_img, indexed_img.layers[0],
                        temp_name, temp_name, False, 9, False, True, False,
                        True, True, True, False)

    str_transp_levels = ""
    for transp_level in final_transp_levels:
        if transp_level == None:
            break
        else:
            str_transp_levels += chr (transp_level)

    png_index_alpha (temp_name, str_transp_levels, name)
    os.unlink (temp_name)
    #and 3 hours later....
    pdb.gimp_image_delete (img)
    pdb.gimp_image_delete (indexed_img)

def pack_colormap (colormap):
    packed = []
    for i in xrange (0, len (colormap), 3):
        packed.append ((colormap[i], colormap[i + 1], colormap [i + 2]))
    return packed

def unpack_colormap (colormap):
    unpacked = []
    for entry in colormap:
        for i in xrange (len (entry)):
            unpacked.append (entry[i])
    return tuple (unpacked)


def compact_alpha_levels (data, limit):
    """Receives a dict with a list in each entry with the pixels in that list,
       and returns a colapsed dict, so that there are at most 'limit' entries,
       with DATA colapsed to nearest entries
    """
    #This will be dull for start. There are other things to implement right now.

    survivors = []

    #preserve full transpt, and full opaque entries:
    if data.has_key(0):
        survivors.append (0)
    if data.has_key(255):
        survivors.append (255)
    threshold = 1
    would_survive = len (data)
    transp_levels = data.keys()
    transp_levels.sort()

    while would_survive > limit or threshold <127:
        if threshold == 1:
            threshold = 2
        else:
            #this is arbitrary, and generates seq. 2, 3, 4, 6, 9, 13, 19, 28, 42, 63, 94;
            threshold = int (threshold * 1.5)
        current_level = 0
        would_survive = 0
        for transp_level in transp_levels:
            if transp_level in survivors:
                continue
            if transp_level - current_level >= threshold:
                current_level = transp_level
                would_survive += 1
    mapping = {}
    for transp_level in transp_levels:
        if transp_level in survivors:
            continue
        if abs (transp_level - survivors[-1]) >= threshold:
            survivors.append (transp_level)
        else:
            mapping[transp_level] = len (survivors) - 1
    survivors.sort ()
    for transp_level in transp_levels:
        if transp_level in survivors:
            continue

        m = mapping [transp_level]
        if ( m  < len (survivors) - 1 and
            abs (transp_level - survivors [m]) >
            abs (transp_level - survivors [m + 1])):
            m += 1
        for pixel in data[transp_level][1]:
            #data[survivors[m]][0] += 1
            data[survivors[m]][1].append (pixel)
        del data[transp_level]
    return data

def duplicate_flatten (img):
    """ Duplicate and flatten an image taking into account the visible components"""
    new_image = img.duplicate()

    count =0
    for layer in img.layers:
        if layer.visible:
            count += 1
    if count > 1:
        pdb.gimp_image_merge_visible_layers(new_image, CLIP_TO_IMAGE)
    pdb.gimp_layer_resize_to_image_size (new_image.layers[0])
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
    return new_image

def stand_alone ():
    if len (argv)<3:
        print "\n\nUse png_indexed_alpha file_input file_map file_out"

        print "\nwhere file_input is an indexed png file, file_map is a text file"
        print "with a number from 0 to 255 for line. This number is the transparency"
        print "level (255 == opaque) for each color in the png colormap. "
        print "unlisted colors -> opaque\n\n"
        print "Or save this program to a GIMP plug-ins directory and use it as a GIMP plug-in"
        exit ()

    #Assemble a string with the transparncy entries for each color index
    file_palette = open (argv[2], "r")
    palette_r = file_palette.readlines()
    palette = ""
    for i in palette_r:
        i = i.strip()
        if not i:
            continue
        if i[0] == "#":
            continue
        if len (i.split()) == 2:
            i = int (i.split()[1])
        elif len (i.split("=")) == 2:
            i = int (i.split("=")[1])
        else:
            i = int(i)
        palette += chr(i)

    png_index_alpha (argv[1], palette, argv[3])
try:
    from gimpfu import *
except:
    if __name__=='__main__':
        stand_alone()
    exit ()

register(
    "save_png_indexed_alpha",
    "Saves an RGBA image as an indexed PNG preserving some of the trasnparency information - V. 0.8",
    "save_png_indexed_alpha  (img, drw, name, number, limit) -> None",
    "Joao S. O. Bueno Calligaris",
    "(c) This program is distributed under the terms of the GPL version 2 or later",
    "2004",
    "<Image>/Python-Fu/Save Indexed PNG with Alpha",
    "RGBA",
    [
        (PF_FILE, "name", "Name of file to save to", os.getcwd() +
            os.path.sep + "indexed.png"),
        (PF_INT, "number", "Number of unique colors", 64),
        (PF_INT, "limit", "Limit alpha levels per color to", 8)

    ],
    [],
    save_png_indexed_alpha)
main ()
