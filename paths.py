#!/usr/bin/python

#Distributed under the GPL. Read the terminal  output of the
#license () function for full legal text.
def license():
	print """
    Python Fu scripts for Path manipulation and export in the GIMP
	PATHS.PY V 1.1 11 May, 2003.
    Copyright (C) 2003  Joao S. O. Bueno

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


def get_path_bounding_box (points):
	maxx=None
	maxy=None
	miny=1e7
	minx=1e7
	for i in xrange(0,len(points)):
		if (i % 3 ==0):
			#if this point is an x coordinate:
			if points[i]<minx:
				minx=points[i]
			if points[i]>maxx:
				maxx=points[i]

		elif i%3 ==1:
			if points[i]<miny:
				miny=points[i]
			if points[i]>maxy:
				maxy=points[i]

	return minx,miny, maxx, maxy

def get_path_center (points):
	"""Returns the geometrical center of the points in the array.
points array is a float array, with each point specified by 3 floats:
x coordinate, y coordiante, and point type: 1 for pont, 2 for control point"""

	minx,miny,maxx, maxy = get_path_bounding_box (points)

	midx=((maxx-minx) /2.0) + minx
	midy=((maxy-miny)/2.0) +miny
	return (midx,midy)


def scale_path(img, drawable, scalex=2, scaley=2):
	"""Scales selected Path, creating a copy of it on given
image"""

	try:
		pathname=pdb.gimp_path_get_current (img)
	except:
		return 0

	path=pdb.gimp_path_get_points (img, pathname)
	path=list(path)

	path[3]=list(path[3])
	numpoints=path[2]

	midx, midy=get_path_center (path[3])
	for i in xrange(0,numpoints):
		if (i % 3 ==0):
			path [3][i]=(path[3][i]-midx) * scalex + midx
		elif i%3 ==1:
			path[3][i]=(path[3][i]-midy) * scaley + midy


	pathname= "Scaled copy of " + pathname

	pdb.gimp_path_set_points (img, pathname, 1,numpoints,tuple( path[3]))



def rotate_path(img, drawable, degrees):
	"""Rotates selected Path clockwise, creating a copy of it on given
image"""
	alpha=-float(degrees)*(pi/180.0)

	try:
		pathname=pdb.gimp_path_get_current (img)
	except:
		return 0

	path=pdb.gimp_path_get_points (img, pathname)
	path=list(path)

	path[3]=list(path[3])
	numpoints=path[2]
	#first, gotta obtain max and min (x), and (y) in order to have a central point
	#around which to rotate the path.

	points=path[3]
	midx, midy=get_path_center(points)
	#and now, for the rotation
	tcos=cos(alpha)
	tsin=sin(alpha)
	for i in xrange(0,numpoints,3):
		px=points[i]-midx
		py=points[i+1]-midy
		tpx=px * tcos + py * tsin
		tpy=py *tcos - px *tsin
		points[i]=int (tpx+midx)
		points[i+1]=int (tpy+midy)

	print "%3.2f, %3.2f" %(midx, midy)
	pathname= "Rotated copy of " + pathname

	pdb.gimp_path_set_points (img, pathname, 1,numpoints,tuple( path[3]))

def to_ps_color (color):
	"""changes a color tuple from (0-255,0-255, 0-255) to normalized
	float values from 0 to 1"""
	out=[]
	for i in color:
		out.append(float(i)/255.0)
	return tuple(out)

def export_path(img, drawable, filename, strike, strike_color, brush_width, fill, fill_color, scale):
	"""Exports selected Path to a portable Postscript file, converting the
	points into curveto postscript parameters."""
	try:
		pathname=pdb.gimp_path_get_current (img)
	except:
		return 0
	fill_color=to_ps_color (fill_color)
	strike_color=to_ps_color (strike_color)
	#gets a tuple with selected path:
	#path[0]<=path type
	#path[1]<=Path closed
	#path[2]<=Number of points
	#path[3]<=point array POINT, CONTROL, CONTROL, ....
	path=pdb.gimp_path_get_points (img, pathname)
	#get rid of spaces, unsuitabe for postscript names:
	pathname2=pathname.replace ("\x20", "_")

	path=list(path)

	path[3]=list(path[3])
	points=path[3]
	numpoints=path[2]

	bb=list (get_path_bounding_box (points))
	bb[0]=int((float(bb[0])-brush_width)*0.9)
	bb[1]=int((float(bb[1])-brush_width)*0.9)
	bb[2]=int((float(bb[2])+brush_width)*1.1)
	bb[3]=int((float(bb[3])+brush_width)*1.1)

	x1,y1,x2,y2=bb
	page_height=y2






	fileout=open (filename, "w")
	fileout.write ("""%%!PS
%%%%Creator: GIMP export Path to PostScript file plugin V 1.0 by Joao S. O. Bueno
%%%%Title: %s
%%%%CreationDate: %s
%%%%DocumentData: Clean7Bit
%%%%Pages: 1
%%%%BoundingBox: %d %d %d %d
%%%%EndComments
%%%%BeginProlog

/%s {
\tnewpath
""" %(filename,strftime ("%a %b %d %H:%M:%S %Y"),x1,y1,x2,y2,pathname2))


	points=path[3]
	num_points=len(points)
	print points
	for i in xrange(0,num_points,9):
		#if it is a point starting a path.
		if i==0 or points[i+2]==3:
			fileout.write ("\t%f %f moveto\n" %(points[i], points[i+1]))
			sp=(points[i],points[i+1])
		#convert the point + control point information into controlpoints to the curveto operator
		cp1 =(points [i+3], points[i+4])
		if i+6<num_points:
			cp2=(points [i+6], points[i+7])
			if i+9<num_points and points[i+11]!=3:
				dp=(points[i+9], points[i+10])
			else:
				#if this is the last point in a closed path:
				dp=sp

		else:
			#if this is the last point in an open path:
			#get out. everythin already drawn;
			break
		fileout.write ("\t%f %f %f %f %f %f curveto \n"
			%(cp1[0],cp1[1],cp2[0],cp2[1],dp[0],dp[1]))





	fileout.write ("""closepath
	} def
gsave
0 %f translate
%f -%f scale
%s
""" %(page_height, scale, scale, pathname2))
	if strike and fill:
		fileout.write ("gsave\n")

	if strike:
		fileout.write ("""
%f setlinewidth
%f %f %f setrgbcolor
stroke
""" %(brush_width/scale, strike_color[0], strike_color[1], strike_color[2]))

	if strike and fill:
		fileout.write ("grestore\n")

	if fill:
		fileout.write ("""
%f %f %f setrgbcolor
eofill
""" %(fill_color[0], fill_color[1], fill_color[2]))

	fileout.write ("grestore\nshowpage\n");
	fileout.close()
	print strike_color
#end export_path (postscript)

def export_path_svg(img, drawable, filename, strike, strike_color,strike_opacity,
       brush_width, fill, fill_color,fill_opacity, unit, scale):
	"""Exports selected Path to a portable Postscript file, converting the
	points into curveto postscript parameters."""
	try:
		pathname=pdb.gimp_path_get_current (img)
	except:
		return 0
	strike_opacity=float(strike_opacity)/100.0
	fill_opacity=float (fill_opacity)/100.0
	unit=unit.replace(" ","")
	if "pt mm in pc px cm".find (unit)==-1:
		print "Invalid CSS Unit for Path export. Assuming points (pt)"
		unit="pt"

	#gets a tuple with selected path:
	#path[0]<=path type
	#path[1]<=Path closed
	#path[2]<=Number of points
	#path[3]<=point array POINT, CONTROL, CONTROL, ....
	path=pdb.gimp_path_get_points (img, pathname)
	#get rid of spaces, undesirable for xml dom  names:
	pathname2=pathname.replace ("\x20", "_").replace ("#","_")

	path=list(path)

	path[3]=list(path[3])
	points=path[3]

	bb=list (get_path_bounding_box (points))
	bb[0]=int(((float(bb[0])-brush_width)*0.9)*scale)
	bb[1]=int(((float(bb[1])-brush_width)*0.9)*scale)
	bb[2]=int(((float(bb[2])+brush_width)*1.1)*scale)
	bb[3]=int(((float(bb[3])+brush_width)*1.1)*scale)

	x1,y1,x2,y2=bb

	fileout=open (filename, "w")
	#svg headers derived from SODPODI 0.31 generated SVG file
	fileout.write ("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<!-- Created with the GIMP - Path to SVG script by Joao S. O. Bueno
Created %s -->
<svg
   id="%s"
   width="%d%s"
   height="%d%s"
   viewBox="0 0 %d %d"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink">

""" %(filename,strftime ("%a %b %d %H:%M:%S %Y"),x2,unit,y2,unit, x2, y2))
	if strike:
		strike="rgb(%d,%d,%d)" %strike_color
	else:
		strile="none"

	if fill:
		fill= "rgb(%d,%d,%d)" %fill_color
	else:
		fill="none"
	style_string="""fill:%s;fill-rule:evenodd;stroke:%s;stroke-opacity:%f;
	stroke-width:%s%s;stroke-linejoin:miter;stroke-linecap:butt;fill-opacity:%f;""" \
	%(fill, strike, strike_opacity, brush_width, unit, fill_opacity)

	points=path[3]
	num_points=len(points)
	this_svg_path=0
	sp=(0,0)
	dp=(0,0)
	#scale_path according to scale factor:
	for i in xrange (0,num_points,3):
		points[i]*=scale
		points[i+1]*=scale
	for i in xrange(0,num_points,9):
		#if it is a point starting a path.
		if i==0 or points[i+2]==3:
			if this_svg_path !=0:
				#if this is not the first closed path in a composed gimp path,
				#close the previous path
				if dp==sp:
					#if the last path was closed:
					fileout.write (" z ")
				fileout.write ("\"\n/>\n")
			fileout.write("""<path \n\tstyle="%s"\n\tid="%s"\n\td=" """
				%(style_string,pathname2+"_%d"%this_svg_path))
			fileout.write ("M %f %f" %(points[i], points[i+1]))
			#record starting point
			sp=(points[i],points[i+1])
			this_svg_path+=1


		#convert the point + control point information into controlpoints to the curveto operator
		cp1 =(points [i+3], points[i+4])
		if i+6<num_points:
			cp2=(points [i+6], points[i+7])
			if i+9<num_points and points[i+11]!=3:
				dp=(points[i+9], points[i+10])
			else:
				#if this is the last point in a closed path:
				dp=sp

		else:
			#if this is the last point in an open path:
			#get out. everythin already drawn;
			break
		fileout.write (" C %f %f %f %f %f %f"
			%(cp1[0],cp1[1],cp2[0],cp2[1],dp[0],dp[1]))



	#after the last path is drawn:
	if dp==sp:
		fileout.write (" z ")
	fileout.write ("\"\n/>\n</svg>\n")


	fileout.close()

#end export_path_svg

register(
        "ScalePath",
        "Scales selected path",
        "Scales selected path",
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2003. GPL applies.",
        "<Image>/Python-Fu/Paths/Scale",
        #"RGB*, GRAY*",
		"*",
        [
                (PF_FLOAT, "Horizontal_Scale", "Amount to scale selected path on horizontal direction", 2),
                (PF_FLOAT, "Vertical_Scale", "Amount to scale selecter path on vertical direction", 2)
        ],
        [],
        scale_path)

register(
        "RotatePath",
        "Rotates selected path",
        "Rotates selected path clockwise",
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2003. GPL applies.",
        "<Image>/Python-Fu/Paths/Rotate",
        #"RGB*, GRAY*",
		"*",
        [
                (PF_FLOAT, "Degrees", "Amount to rotate selected path around it's center, clockwise", 0)
        ],
        [],
        rotate_path)

register(
        "ExportPath",
        "Exports selected path to postscript file",
        """Exports selected path to postscript file, with option of striking
		and/or filling with a solid color. TODO: Export to EPS""",
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2003. GPL applies.",
        "<Image>/Python-Fu/Paths/Export/to Postscript",
        #"RGB*, GRAY*",
		"*",
        [
                (PF_FILE, "File", "File name to export", "gimp_path.ps"),
				(PF_BOOL, "Draw_Contour", "Whether or not to strike the path", 1),
				(PF_COLOUR, "Contour_Color", "Strike Color", (0,0,0)),
				(PF_FLOAT, "Brush_Width" , "brush width in points", 1),
				(PF_BOOL, "Fill_Path", "Whether or not to fill the path", 0),
				(PF_COLOUR, "Fill_Color", "Fill Color", (0,0,0)),
				(PF_FLOAT, "Scale", "Scale in points/pixel", 1)


        ],
        [],
        export_path)
register(
        "ExportPathSVG",
        "Exports selected path to postscript file",
        """Exports selected path to SVG file, with option of striking
		and/or filling with a solid color. """,
        "Joao S. O. Bueno",
        "Joao S. O. Bueno",
        "2003. GPL applies.",
        "<Image>/Python-Fu/Paths/Export/to SVG",
        #"RGB*, GRAY*",
		"*",
        [
                (PF_FILE, "File", "File name to export", "gimp_path.svg"),
				(PF_BOOL, "Draw_Contour", "Whether or not to strike the path", 1),
				(PF_COLOUR, "Contour_Color", "Strike Color", (0,0,0)),
				(PF_SLIDER, "Contour_Opacity", "Contour Opacity", 100,(0,100,1)  ),
				(PF_FLOAT, "Brush_Width" , "brush width in points", 1),
				(PF_BOOL, "Fill_Path", "Whether or not to fill the path", 0),
				(PF_COLOUR, "Fill_Color", "Fill Color", (0,0,0)),
				(PF_SLIDER, "Fill_Opacity", "Fill Opacity",100, (0,100,1)),
				(PF_STRING, "Units", "pt, mm, cm, in, px, pc", "pt" ),
				(PF_FLOAT, "Scale", "Scale in units/pixel", 1)



        ],
        [],
        export_path_svg)

main()
