#!/usr/bin/env python

from gimpfu import *

import math

def font_test (img, drw, font):


    #pdb.gimp_image_undo_group_start (img)
    print font
    #pdb.gimp_image_undo_group_end (img)




register(
         "font_test",
         "Triess PF_FONT",
         "test script - do not use",
         "Joao S. O. Bueno Calligaris",
         "(k) All rites reversed - JS",
         "2005",
         "<Image>/Python-Fu/Alchemy/Font Test",
         "*",
         [
                (PF_FONT, "font", "Font","Sans 100")
         ],
         [],
         font_test)

main()
