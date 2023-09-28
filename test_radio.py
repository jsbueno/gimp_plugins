#!/usr/bin/python
# -*- coding: utf-8 -*-

from gimpfu import *

CROP_NOTHING = 0
CROP_IMAGE = 1
CROP_LAYER = 2

def radio_test (img, drw, radio):
    print radio

register(
        "radio_test",
        "does nothign  - test only",
        "Does nothing",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2006",
        "<Image>/Python-Fu/Radio Test",
        "*",
        [(PF_RADIO, "radio", "Choose mode :",
         CROP_LAYER,
          (("Leave as it is", 0.5 ), ("Crop Image", CROP_IMAGE), ("Crop Layer", CROP_LAYER) ),
        )
        ],      
        [],
        radio_test)
main ()