#!/usr/bin/python


from gimpfu import *
import os


def clear_subtitles(folder, sc1, dc1, sc2, dc2):
    for file in os.listdir (folder):
        if file[-4:].lower() != ".png":
            continue
        img = pdb.gimp_file_load (file, file)
        print file
        img.disable_undo ()
        pdb.gimp_by_color_select (img.layers[0], sc1, 0,
                                  CHANNEL_OP_REPLACE, False,
                                  False, 0, False)
        pdb.gimp_context_set_foreground (dc1)
        pdb.gimp_edit_fill (img.layers[0], FOREGROUND_FILL)

        pdb.gimp_by_color_select (img.layers[0], sc2, 0,
                                  CHANNEL_OP_REPLACE, False,
                                  False, 0, False)
        pdb.gimp_context_set_foreground (dc2)
        pdb.gimp_edit_fill (img.layers[0], FOREGROUND_FILL)
        #doesn't work:
        #pdb.plug_in_color_map (img, img.layers[0], sc1, sc2, dc1, dc2, 0)

        pdb.gimp_file_save (img, img.layers[0], os.path.join (folder, file), file)



register(
        "clear_subtitles",
        "replace two given colors in a sequence of png files in a directory",
        """Changes an Image size to the Selection boundary size
        """,
        "Joao S. O. Bueno Calligaris",
        "Joao S. O. Bueno Calligaris",
        "2006. GPL applies.",
        "<Toolbox>/Xtns/Python-Fu/Clear Subtitles",
        "*",
        [
          (PF_STRING, "folder", "file folder", ""),
          (PF_COLOR, "src_color_1", "src_color_1", (0,127,0)),
          (PF_COLOR, "dest_color_1", "dest_color_1", (0,0,0)),
          (PF_COLOR, "src_color_2", "src_color_2", (127,127,0)),
          (PF_COLOR, "dest_color_1", "dest_color_2", (255,255,0)),
        ],
        [],
        clear_subtitles)

main()
