#!/usr/bin/env python

from gimpfu import *
from os import sep
from math import ceil
import re
from os import listdir


def contact (cols, rows, width, height, spacing, keep_ratio, auto_rotate, reg_exps, images, directory):
    """Creates  new width x height gimp image(s), and import several other
     disk images into it, like a "contact" copy of negatives 
    """

    #arrays to hold all image filenames and whether each should be manually rotated.
    image_names = []
    image_rotate = []
    
    #indexes used to sync manual rotation option with image file names.
    i = 0
    last_block_i = -1
    #cut filenames list on commas
    images_ = images.split (",")
    #if there is no comma, cuts on spaces.
    if len (images_) == 1:
        images_ = images.split ()
    
    #retrieve all file names in target directory     
    if reg_exps:
        all_files = listdir (directory)
    #parse all inpout names and synch the informationa about rotation
    for name in images_:
        name_ = name.strip()
        image_rotate.append (0)
        #if input is a single digit, treat as a manual rotation operator, rather than image file name
        if name_.isdigit() and len (name_) == 1:
            if last_block_i == -1:
                image_rotate [i - 1] = int(name_)
            else:
                for j in range (last_blocl_i, i):
                    image_rotate [i - 1] = int(name_)
        else:
            #just appends the filename to our list
            if not reg_exps:
                last_block_i = -1
                image_names.append (name_ )
                image_rotate.append (0)
                i += 1
            #if the input name is a regexp, eun the regexp against all filenames in target directory,
            #appending the matches
            else:
                exp = re.compile (name_)
                last_block_i = i
                for filename in all_files:
                    if re.match (exp, filename):
                        image_names.append (filename)
                        image_rotate.append (1)
                        i += 1
    #based on input parameters, calculate the pixel size for each image we are tiling.
    layer_width = float (width - spacing) / cols  - spacing
    layer_height = float (height - spacing) / rows - spacing 
    layer_ratio = layer_width / layer_height                    

    #creates an array taht will hold references to the new images created as output of the porgram
    #FIXME: it is actually unused after creation. And MAY BE related to the bug of dying python-fu        
    imgs = []
    #resets counter for all images that will be read from the disk
    image_counter = 0
    #loops over each space existing in all output images that will get created
    for img_n in xrange (int (ceil (float (len (image_names)) / (cols * rows)))):
        #exits if we got all our image list done.
        if image_counter >= len (image_names):
            break
        
        #creates new image in the GIMP
        imgs.append (pdb.gimp_image_new (width, height, RGB))
        img = imgs[img_n]
        
        #creates background layer in our image.
        background = pdb.gimp_layer_new (img, width, height, RGB, "background", 100, NORMAL_MODE)
        img.add_layer (background, 0)
        background.fill (BACKGROUND_FILL)
        #vector to hold the layers with our thumbnails on the current image
        layers = []
        #index of thumbnails on the current image
        i = 0
        #loops over rows and cols on target image
        for x in xrange (cols):
            for y in xrange (rows):
                #if we get past our filenames list, exit
                if image_counter >= len (image_names):
                    break
                #open next file in the gimp, on a new (undisplayed) image
                #if open fails, skip this image and continues execution
                try:
                    thumb_img = pdb.gimp_file_load (directory + sep + image_names [image_counter],
                                                    image_names [image_counter]
                                                   )
                except:
                    print "contact.py - Image %s failed to load" %image_names [image_counter]
                    image_counter += 1
                    continue
                #if new image has more than a layer, flatten it.
                if len (thumb_img.layers) > 1:
                    thumb_img.flatten ()
                #if this image is set for manual rotation, do it.
                if image_rotate[image_counter]:
                    pass
                #this was not working fine.
                    #pdb.gimp_image_rotate (thumb_img, image_rotate [image_counter] - 1)
                if keep_ratio:
                    #is aspect ratio of target thumbnail is smaller than from original image
                    w = thumb_img.width
                    h = thumb_img.height
                    thumb_ratio = float (w) / h
                  
                    if (auto_rotate and not image_rotate[image_counter] 
                       and ((thumb_ratio - 1) * (layer_ratio - 1)) < 0.0 ):
                        pdb.gimp_image_rotate (thumb_img, ROTATE_270)
                        w = thumb_img.width
                        h = thumb_img.height
                        thumb_ratio = float (w) / h
                    
                    if layer_ratio <= thumb_ratio:
                        thumb_img.scale (int (layer_width),
                                        int (thumb_img.height / (float (thumb_img.width) / layer_width)))
                    else:
                        thumb_img.scale ( int (thumb_img.width / (float (thumb_img.height) / layer_height)),
                                         int (layer_height))
                       
                    #calculate factors to center image in it's tile space.        
                    x_correction = (layer_width - thumb_img.width ) /2.0
                    y_correction = (layer_height - thumb_img.height ) /2.0
                else:
                    #ifnot keeping aspect ratio, just scale to tile size
                    thumb_img.scale (layer_width, layer_height)
                    x_correction = 0
                    y_correction = 0
                #copy the image read from disk to our current output image.
                drw = pdb.gimp_layer_new_from_drawable (thumb_img.layers[0], img)
                layers.append (drw)
                img.add_layer (drw, -1)
                i += 1     
                drw.set_offsets (x_correction + spacing + x * (layer_width + spacing),
                                 y_correction + spacing + y * (layer_height + spacing))
                pdb.gimp_drawable_set_name (drw, image_names [image_counter])
                pdb.gimp_image_delete (thumb_img)
                image_counter += 1
        #display this output image, and starts next one.        
        pdb.gimp_display_new (img)
    pdb.gimp_displays_flush()




register(
         "contact",
         "Contact Filter",
         "Tile up N images on disk on a large one",
         "Joao S. O. Bueno",
         "(k) All rites reversed - JS",
         "2004",
         "<Toolbox>/Xtns/Python-Fu/contact",
         "",
         [
                (PF_INT, "cols", "How many cols of images", 2),
                (PF_INT, "rows", "How many rows of images", 2),
                (PF_INT, "width", "Image Width",1754),
                (PF_INT, "height", "Image Height",1240),
                (PF_INT,  "spacing", "Spacing between images", 80),
                (PF_TOGGLE, "keep_ratio", "Keep aspect ratio", 1),
                (PF_TOGGLE, "auto_rotate", "Auto rotate Images", 1),
                (PF_TOGGLE, "regexps", "Filenames are regexps", 0),
                (PF_STRING, "images", "List of images separated by spaces.\n Put a \"1\" on the list to rotate previous image", ""),
                (PF_DIRNAME, "directory", "Directory were to pick image files from", ".")
         ],
         [],
         contact)

main()
