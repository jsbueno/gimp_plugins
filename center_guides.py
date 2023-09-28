#!/usr/bin/python

#use Gimp qw( :auto );
#use Gimp::Fu;
# I don't know what this "auto:" means,
#but we normally just import gimpfu in python scripts/

from gimpfu import *

#register        "center_guide",
# the register call in python must come after the function definition 
#itself. Ok - this is  thasy perl way, in which the function was
#defined inside the funcion call for register. Python is  a clean
#language - the only way of doing this is with short functions
#that can be written as lambdas.

#        sub {
#                my ($img, $layer, $center) = @_;
def center_guide (img, layer, center):
     #beware of indentation from this point on

     #$w = $img->width();
     #$h = $img->height();
     #$hc = int($h/2 + 0.5);
     #$vc = int($w/2 + 0.5);

     w = img.width
     h = img.height
     hc = int (h / 2.0 + 0.5)
     vc = int (w / 2.0 + 0.5)

     #if ($center == 1) {
     #      $hc = int(($h / 2.6179) + 0.5);
     #    };
     if center == 1:
          hc = int (h / 2.6179 + 0.5)

     #          $bit_bucket = $img->add_hguide($hc);
     #          $bit_bucket = $img->add_vguide($vc);
     #          gimp_drawable_update($layer, 0, 0, $w, $h);
     img.add_hguide (hc)
     img.add_vguide (vc)
     gimp.displays_flush()	

     #   };

register   ("center_guide",
            "Creates h- & v-guides at the center of the image.",
            "Physical center = width/2 and height/2; Optical center = the Golden Mean.",
             "Claes G Lindblad <claesg\@algonet.se>",
             "Claes G Lindblad, pythonified by Joao S. O. Bueno Calligaris",
              "990323",
              "<Image>/Image/Guides/Center Guides",
              "*",
              [
                [PF_RADIO,
                        "center",
                        "center",
                         0,
                         (("Physical", 0), ("Optical", 1))
                ]
                      
              ],
              [],
              center_guide
              )  
                

#exit main;
main ()
