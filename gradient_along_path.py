#!/usr/bin/env python

from gimpfu import *

def gradient_along_path(img, drw, width, gradient, revert):
    
    width = width / 2.8
    img.undo_group_start()
    
    #gimp.context_push()
    
    strike_layer = pdb.gimp_layer_new(img, img.width, img.height, RGB_IMAGE, "gradient strike", 100, NORMAL_MODE)
    img.add_layer(strike_layer)
    pdb.gimp_layer_add_alpha(strike_layer)
    strike_layer.fill(WHITE_FILL)
    
    #setup brush for striking
    
    brush = pdb.gimp_brush_new("gradient_stroker")
    pdb.gimp_brush_set_shape(brush, BRUSH_GENERATED_CIRCLE)
    pdb.gimp_brush_set_hardness(brush, 1)
    pdb.gimp_brush_set_radius(brush, width / 2.0)
    pdb.gimp_brush_set_spacing(brush, 1.0)
    pdb.gimp_brush_set_spikes(brush, 2)
    pdb.gimp_brush_set_aspect_ratio(brush, 1.0)
    pdb.gimp_brush_set_angle(brush, 0)
    
    pdb.gimp_context_set_brush(brush)
    
    current_color = pdb.gimp_context_get_foreground()
    pdb.gimp_context_set_foreground((0,0,0))
    
    pdb.gimp_edit_stroke_vectors(strike_layer, pdb.gimp_image_get_active_vectors(img))
    
    pdb.plug_in_gauss_iir2(img, strike_layer, width, width)
    
    old_sel = pdb.gimp_selection_save(img)
    
    pdb.gimp_by_color_select(strike_layer, (255,255,255),
                             0, CHANNEL_OP_REPLACE,
                             True, False, 0, False)
    pdb.gimp_edit_cut(strike_layer)
    #new step needed in gimp 2.5
    
    pdb.gimp_selection_none(img)
    gimp.context_set_gradient(gradient)
    if revert:
        pdb.gimp_invert(strike_layer)
    
    #certain gradients depend on context color
    pdb.gimp_context_set_foreground(current_color)
    
    #weird bug in 2.5 devel cycle: gradmap won't work if the is a selection.
    
    pdb.plug_in_gradmap(img, strike_layer)

    
    #
    visible_layers = [layer.name for layer in img.layers if layer.visible and layer != strike_layer]
    for layer in img.layers:
        layer.visible = False
    strike_layer.visible = True
    drw.visible = True
    
    pdb.gimp_image_merge_visible_layers(img, CLIP_TO_BOTTOM_LAYER)
        
    for layer in img.layers:
        if layer.name in visible_layers:
            layer.visible = True
    
    #clean up
    pdb.gimp_selection_load(old_sel)
    pdb.gimp_brush_delete(brush)
    pdb.gimp_image_remove_channel(img, old_sel)
    
    #gimp.context_pop()
    
    img.undo_group_end()
    gimp.displays_flush()



register(
         "gradient_along_path",
         "Strike a path using an orthogonal gradient",
         "Strike a path using an orthogonal gradient, implements  BUG #55018",
         "Joao S. O. Bueno",
         "Joao S. O. Bueno  - GPL v2 or Later",
         "2007",
         "<Image>/Python-Fu/Gradient Along Path",
         "*",
         [
                (PF_INT, "Width", "Width of the stroke", 10),
                (PF_GRADIENT, "Gradient", "Gradient to use", "FG to BG (RGB)"),
                (PF_BOOL, "Revert", "Use inverted gradient", False)
            ],
         [],
         gradient_along_path)

main()
