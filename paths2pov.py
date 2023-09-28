#!/usr/bin/python
# -*- coding: utf-8 -*-
#Distributed under the GPL. Read the terminal  output of the
#license () function for full legal text.
def license():
    print """
    Python Fu scripts for Path manipulation and export in the GIMP
    PATHS.PY V 1.2 17 Apr, 2005.
    Copyright (C) 2003, 2004, 2005 Joao S. O. Bueno Calligaris

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from gimpfu import *
from math import *
from time import strftime
from os import spawnvp, P_WAIT, system




def to_pov_color (color):
    """changes a color tuple from (0-255,0-255, 0-255) to normalized
    float values from 0 to 1 in povray SDL vector sintax"""
    #to do: check if color length != 3, to work with non rgb images.
    out=[]
    for i in color:
        out.append(float(i)/255.0)
    return " rgb <%f,%f,%f> "  %tuple(out[:3])






def export_path_sphere_union (img, drawable, filename,color, radius, runpov, sphere_sweep, sample, command_line, sphere_def):
    """Exports selected Path to a POVray Sphere Union object. May render file into image."""
    
    try:
        pathname=pdb.gimp_path_get_current (img)
    except:
        #no selected path.
        return 0
    color=to_pov_color (color)

    bgcolor=to_pov_color (pdb.gimp_palette_get_background ())

    path_all_points=pdb.gimp_path_get_points (img, pathname)[3]
    path_changing_points=[(path_all_points[0],path_all_points[1])]
    for i in xrange (0,len(path_all_points),3):
        if path_all_points[i+2] ==3:
            #if this is  a point that starts a discontinuous portion of the path
            path_changing_points.append((path_all_points[i],path_all_points[i+1]))




    width=pdb.gimp_image_width (img)
    height=pdb.gimp_image_height (img)

    ratio=float(height)/float(width)
    povscale=1.0/ height


    spheresweeps= ""

    if 1:
        #there is no way to tell the path lenght with
        #gimp_path_get_point_at_dist,
        #so, the way out of the loop is the excetion when we search beyond
        #the path's end
        where=0.0
        count=0
        count_this=0
        ox=-1
        oy=-1
        sphere_sweeps_tmp=[]
        ograd=None
        o_ograd=None
        changed=0
        while (1):

            point=pdb.gimp_path_get_point_at_dist (img, where)
            if point == (0, 0, 0.0):
                #Starting GIMP 2.2, this is returned when the end of a path is reached.
                #in earlier versins of this function, an excepetion was generated
                #( hence this block is inside a "try except")
                break

            #this path_get_point_at_dist function does spill out
            #somne "false positives" when in transition from one
            #path segment to the other.
            #so, lets add a  work around here

            #The distance returned from the PDB is not accurate.
            #so we pick 2*sample as a threshold value./
            if ox!=-1 and (abs(point[0]-ox)>(sample*2) or
            abs(point[1]-oy)>(sample*2)):

                # next curve in the path.

                far=1
                while (far):

                    for i in path_changing_points:
                        if abs(point[0]-i[0])<=sample and \
                        abs(point[1]-i[1])<=sample:
                            far=0
                    if far:
                        where+=1
                        point=pdb.gimp_path_get_point_at_dist (img, where)


            if not sphere_sweep:
                d = {}
                d["x"] = point[0]
                d["y"] = point[1]
                d["radius"] = radius
                spheresweeps+=("\t" + sphere_def + "\n") % d
            else:
                if ox!=-1:
                    if ox!=-1 and (abs(point[0]-ox)>(sample*2) or
                    abs(point[1]-oy)>(sample*2)):

                        # next curve in the path. need to switch sweeps.
                        o_ograd=None
                        ograd=None
                        for i in sphere_sweeps_tmp:
                            spheresweeps+=i
                        changed=1
                        spheresweeps+="\t\t tolerance 0.001 \n\t\t}\n"
                        spheresweeps=spheresweeps % count_this
                        count_this=0
                    else:
                        changed=0
                if ox==-1 or changed:
                    sphere_sweeps_tmp=[]
                    spheresweeps += """
     sphere_sweep
         {linear_spline
          %d,
          """
                #if the last two points  on a straight line, just drop the last one.
                if point[2]==o_ograd and point[2]==ograd:
                    sphere_sweeps_tmp.pop()
                    count_this -=1


                sphere_sweeps_tmp.append ("\n\t\t <%f, %f, 0>, %f"
                 %(point[0],height - point[1], radius))
                count_this+=1

            ox=point[0]
            oy=point[1]
            o_ograd=ograd
            ograd=point[2]
            where+=sample
            count+=1

    if sphere_sweep:
        for i in sphere_sweeps_tmp:
            spheresweeps+=i
        spheresweeps+="\t\t tolerance 0.001 \n\t\t}\n"
        #print spheresweeps
        spheresweeps=spheresweeps % count_this

    if filename is None:
        filename = "/tmp/paths2pov.pov"
    fileout=open (filename, "w")


    fileout.write ("""
/*POVRay 3.5 file
/
/ Generated by Path to Sphere Union filter, in GIMP.
/ Path to Sphere Union by Joao S. O. Bueno
/ Using GIMP PYTHON
/ Filename: %s
/ Creation time: %s
*/

camera {
    orthographic
    up <0, 1, 0>
    right <%f, 0, 0>
    location <%f, 0.5, -30>
    look_at <%f, .5, 0>
  }


#background {%s}

#declare Swtexture=
texture
    {pigment
        {color %s}
     finish
         {specular .9
         ambient .4
        }
    }

union
    {
     %s
     texture { Swtexture}
     scale %f
    }

light_source
    {<-1,2,-3>
     color rgb <1,1,1>
    }

""" %(filename,strftime ("%a %b %d %H:%M:%S %Y"),
 1/ratio, (1/ratio)/2, (1/ratio)/2, bgcolor, color, spheresweeps, povscale) )
    fileout.close()

    if runpov:
        pngfilename=filename[0:-4]
        command_dict={"input_file":filename, "output_file":pngfilename,
        "width": width, "height": height}
        print command_line % command_dict
        system (command_line % command_dict)
        #pov=spawnvp (P_WAIT,"povray",(command_line %command_dict).split())
        print pngfilename
        povimage=pdb.file_png_load(pngfilename + ".png", pngfilename.rsplit("/",1)[:-1] )
        the_layer=pdb.gimp_image_get_active_layer(povimage)
        pdb.gimp_edit_copy(the_layer)
        the_old_layer=pdb.gimp_image_get_active_layer(img)
        the_new_layer=pdb.gimp_edit_paste(the_old_layer,0)
        pdb.gimp_floating_sel_to_layer(the_new_layer)
        the_new_layer.name="POVRay Rendered Layer"
        pdb.gimp_image_delete (povimage)
        pdb.gimp_displays_flush()






register(
        "ExportPathSphereUnion",
        "Creates a Sphere Union as a POVRay(tm) object",
        """Exports selected path to Povray Sphere Union (faster than sphere sweep) object. May optionally
    render path into Image layer.""",
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2003. GPL applies.",
        "<Image>/Python-Fu/Paths/Povray Sphere Union",
        "*",
        [
                (PF_FILE, "File", "File name to export", "gimp_path.pov"),
                (PF_COLOUR, "color", "color", (0,255,0)),
                (PF_FLOAT, "Sphere_radius" , "sweep radius in pixels", 10),
                (PF_BOOL, "Run_pov", "Run Povray", 1),
                (PF_BOOL, "sphere_sweep", "Generate Sphere Sweep", 0),
                (PF_FLOAT, "sample","Sample distance(px)",20),
                (PF_STRING, "command_line", "POVRay command line", "povray +i%(input_file)s +o%(output_file)s.png +w%(width)d +h%(height)d +a0.5 +D -P +L/usr/local/lib/povray-3.5/include/ +Fn  +UA"),
                (PF_TEXT, "sphere_def", "Povray sphere definition", "sphere {<%(x)f,%(y)f,0>,%(radius)f}")

        ],
        [],
        export_path_sphere_union)

main()
