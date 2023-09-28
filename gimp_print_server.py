#!/usr/bin/env python
# -*- coding: utf-8 -*-


#Author: João S. O. Bueno
# Copyright (c) João S. O. Bueno  2008, 2009

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




from gimpfu import *
from wsgiref.simple_server import make_server
from urllib import unquote_plus
from string import Template
import cgi
import os, sys
import time
from subprocess import Popen
from ConfigParser import ConfigParser
from sys import stderr

## Configurable parameters:
DATA_DIR=os.environ["TMPDIR"]

TEMPLATE_DIR = os.path.join("%(HOME)s", ".gimp_print_server", "templates")
PHOTOPRINT_CONFIG = os.path.join("%(HOME)s", ".photoprint", "default.preset")

#FIXME: debug output:
OUTPUT_PATH = os.path.join("%(HOME)s", "print_server_output.ps")
PRINTRC_PATH = os.path.join("%(HOME)s", ".gimp-2.6", "printrc")
TEST_IMAGE_PATH = os.path.join("%(HOME)s", "test.png")
THUMBNAIL_WIDTH = 240

THUMB_TEMPLATE = """<a href="/image" target="image"
><img src="/thumbnail" alt="thumbnail" /></a> """

MAIN_TEMPLATE = """<p>Welcome to the Printing web server</p>
%(thumb_template)s
%(message)s
<ul class="menu">
<li><a href="upload"> Upload a new image</a></li>
<li><a href="config"> Setup printing parameters</a></li>
<li><a href="print"> Print image</a></li>
<li><a href="info"> Debug information for development</a></li>
<li><a href="reset"> Reset session</a></li>
</ul>
""" 
#% {"thumb_template": THUMB_TEMPLATE}

UPLOAD_TEMPLATE = """
<form name="image" action="upload" method="post" enctype="multipart/form-data" >
<p>Image File:
<input type="file" name="image" />
<br />
<input type="submit" name="send" value="send" />
</p>
</form>
"""
FORM_TEMPLATE = """
<p>Printing Server</p>
%(thumb_template)s
<p class="message">%(message)s</p>
<form name="parameters" action="%(action)s" method="post" >
%(html_form)s
<input class="submit_button" type="submit" value="Ok" name="ok" />
<input class="reset_button" type="reset" value="Cancel" />
</form>
"""


WIDGET_ENTRY="""<div class="widget"><span>%(label)s</span>: 
<input type="text" name="%(name)s" value="%(value)s" /></div>
"""

# global data srtructure to hold session data
# th e idea is to serve a single client at a time
# so we are keeping this in memory

#should this ever need to scale, it should be easy enough
# to move this to a persistent data-structure

sessions = {}
#FIXME: I am using current_session as a global -- it should rather be
# an "environ" dict member so this can scale without problems
current_session = None

##General utilities: 

class DefDict(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return ""

class MyConfigParser(ConfigParser):
    """
    The config file for PhtoPrint must be kept in order and must have
    no extra whitespace surrounding the "="
    """
    optionxform = str
    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        #photoprint starts with a new line in the config file:
        fp.write("\n")
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                #the line bellow is one of the only changes for this method:
                fp.write("%s=%s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    #the line bellow is one of the only changes for this method:
                    fp.write("%s=%s\n" %
                             (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

class OrderedDict(dict):
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.order = []
    def __setitem__(self, key, value):
        if not key in self:
            self.order.append(key)
        dict.__setitem__(self, key, value)
    def keys(self):
        return self.order
    def items(self):
        return [(key, self[key]) for key in self]
    def __iter__(self):
        return (i for i in self.order)


###
gutemprint_default_parameters = {
    "image": None,
    "drawable": None,
    "output-to": "/tmp/test.ps",
    "driver": "ps2",
    "ppd-file": "",
    "output-type": 1,
    "resolution": "300",
    "media-size": "A4",
    "media-type": "Plain Paper",
    "media-source": "Auto Sheet Feeder",
    "brightness": 1.0,
    "scaling": 100, 
    "orientation": -1,
    "left": -1,
    "top": -1,
    "gamma": 1.0,
    "contrast": 1.0,
    "cyan": 1.0,
    "magenta": 1.0,
    "yellow": 1.0,
    "linear": 0,
    "image-type": 1,
    "saturation": 100, 
    "density": 1.0, 
    "ink-type": "None",
    "dither-algorithm": "None",
    "unit": 0
    }

#TODO: change these entries into tuples,
#describing input type, and parameter validation
editable_controls = [
    "resolution",
    "media-size",
    "media-type",
    "brightness",
    "scaling",
    "gamma",
    "contrast",
    "cyan",
    "magenta", 
    "yellow",
    "linear",
    "saturation",
    "density"
    ]

def load_default_parameters(current_session):
    current_session["print_parameters"] = gutemprint_default_parameters

def gimp_print(new_parameters={}):
    """Performs the actual function call to gutemprint.
    new_parameters should have at least "image" and "drawable" 
    set with valid GIMP objects
    """
    p = gutemprint_default_parameters.copy()
    p.update(new_parameters)
    #as of gutemprint v. 5.2.3.99 this call is borken and can't actually print
    pdb.file_print_gutenprint(
    p["image"],
    p["drawable"],
    p["output-to"],
    p["driver"],
    p["ppd-file"],
    p["output-type"],
    p["resolution"],
    p["media-size"],
    p["media-type"],
    p["media-source"],
    p["brightness"],
    p["scaling"],
    p["orientation"],
    p["left"],
    p["top"],
    p["gamma"],
    p["contrast"],
    p["cyan"],
    p["magenta"],
    p["yellow"],
    p["linear"],
    p["image-type"],
    p["saturation"], 
    p["density"], 
    p["ink-type"],
    p["dither-algorithm"],
    p["unit"]
    )
    
### WEB APP util functions

#def dimension_to_points(x, data):
    #if data.get("unit", "inch") == "mm":
        #value = str(int((float(x) / 25.4) * 72))
    #else:
        #value = str(int(float(x) * 72))
    #return value
#list of options to be rendered as an HTML form for printing images: 
photoprint_options_list = [
    {"type": "number",
     "group": "Image Size",
     "label": "Width",
     "name": "width",
     "validrange": (20, 500),
     "programatic_config": True
    },
    {
     "type": "number",
     "group": "Image Size",
     "label": "Height",
     "arrange": "previous",
     "name": "height",
     "validrange": (20, 500),
     "programatic_config": True
    },
    {
     "type": "radio",
     "group": "Image Size",
     "arrange": "previous",
     "label": "Unit",
     "name": "unit",
     "options": ["mm", "inch"],
     "programatic_config": True
    },

    {"type": "number",
      "group": "Paper Size",
      "label": "Height",
      "help": "paper height:",
      "name": "page_height",
      "validrange": (50, 1000),
      #Function to promote user input from milimiters to points:
      "converter": lambda x: str(int((float(x) / 25.4) * 72)),
      "photoprint_config": ("Print", "CustomHeight")
    },  
    {
     "group": "Margins",
     "type": "number",
     "label": "Left",
     "name": "left_margin",
     "validrange": (0, 200),
     "programatic_config": True,
    },
    {
     "group": "Margins",
     "type": "number",
     "label": "Top",
     "name": "top_margin",
     "validrange": (0, 200),
     "programatic_config": True,
     "arrange": "previous",
   },
   {
     "type": "radio",
     "group": "Rotation",
     "label": "Rotation",
     "name": "rotation",
     "options": ["0 degree", "CW 90 degree", "CCW 90 degree", "180 degree"],
     "values": [0, 90, 270, 180],
     "programatic_config": True,
    },
    {"type": "number",
     "group": "Copies",
     "label": "Number of Copies",
     "name": "copies",
     "validrange": (1, 20),
     "programatic_config": True
    },
    {
     "type": "number",
     "group": "Copies",
     "label": "Hor. Spacing",
     "arrange": "previous",
     "name": "x_spacing",
     "validrange": (0, 500),
     "programatic_config": True
    },
    {
     "type": "number",
     "group": "Copies",
     "label": "Vert. Spacing",
     "arrange": "previous",
     "name": "y_spacing",
     "validrange": (0, 500),
     "programatic_config": True
    },
    {
     "type": "radio",
     "group": "Color Modes",
     "label": "Color Modes",
     "name": "color_modes",
     "options": ["CMYK only", "White then CMYK", "White only", "CMYK and White together"],
     "values": [0, 1, 2, 3],
     "programatic_config": True,
    },
    {
     "type": "number",
     "group": "CMYK Settings",
     "label": "Intensity",
     "name": "cmyk_level",
     "validrange": (0, 1.0),
     "photoprint_config": ("CMYKWW", "CMYKLevel"),
     "default": "1.0",
    },
    {
     "type": "number",
     "group": "CMYK Settings",
     "label": "Gama",
     "arrange": "previous",
     "name": "cmyk_gamma",
     "validrange": (0, 10.0),
     "photoprint_config": ("CMYKWW", "CMYKGamma"),
     "default": "2.0",
    },
    {
     "type": "number",
     "group": "White Settings",
     "label": "Intensity",
     "name": "white_level",
     "validrange": (0, 1.0),
     "programatic_config": True, #no such value in photoprint options. Perhaps 
                                 # there is only one value for both cmyk and white printing
     #"photoprint_config": ("CMYKWW", "CMYKLevel"),                          
     "default": "1.0",
    },
    {
     "type": "number",
     "group": "White Settings",
     "label": "Gama",
     "arrange": "previous",
     "name": "white_gamma",
     "validrange": (0, 10.0),
     "photoprint_config": ("CMYKWW", "WhiteGamma"),
     "default": "2.0",
    },
    {
     "type": "number",
     "group": "White Settings",
     "label": "Brightest",
     "arrange": "previous",
     "name": "white_britghtest",
     "validrange": (0, 1.0),
     "photoprint_config": ("CMYKWW", "CMYKWWMax"),  #Can't know about this one without testing 
     "default": "0.05",
    },
    {
     "type": "number",
     "group": "White Settings",
     "label": "Darkest",
     "arrange": "previous",
     "name": "white_darkest",
     "validrange": (0, 10.0),
     "photoprint_config": ("CMYKWW", "CMYKWWMin"),  #Can't know about this one without testing 
     "default": "1.0",
    },
    {"type": "pannel",
     "group": "Printer Jobs Queue",
     "name": "printer_queue",
     "label": "",
    },
    {"type": "action",
     "group": "Options",
     "help": "Get latest printing jobs queue status from printing system",
     "label": "Refresh Queue",
    },
    {"type": "action",
     "group": "Options",
     "arrange": "previous",
     "help": "Remove all print queue",
     "label": "Clear Queue",
    },
    {"type": "action",
     "group": "Options",
     "arrange": "previous",
     "help": "Perform Nozzle Check Pattern printing",
     "label": "Nozzle Check",
    },
    {"type": "action",
     "group": "Options",
     "arrange": "previous",
     "help": " Perform Nozzle Cleaning action",
     "label": "Cleaning",
    },
    {"type": "action",
     "group": "Options",
     "help": " Cancel printing",
     "label": "Cancel",
    },
    {"type": "action",
     "group": "Options",
     "arrange": "previous",
     "help": "Prints the image",
     "label": "Print",
    },
    {"type": "action",
     "group": "Options",
     "arrange": "previous",
     "help": "Saves printing parameters",
     "label": "Save As Default",
    },
    {"type": "action",
     "group": "Options",
     "arrange": "previous",
     "help": "Loads printing parameters",
     "label": "Load Settings",
    },
]
    # These options make little sense in roll paper -
    # and our intention for now is to use roll paper.
    
    # when implemented, photo position on the page will have to be calculated
    # using the margin values on the photoprint file
"""
    {"type": "select",
      "label": "Orientation",
     "name": "orientation",
     "options": ["Landscape", "Portrait"]
    },
    {"type": "select",
      "label": "Position",
     "name": "horizontal_position",
     "options": ["Left", "Center", "Right"]
    },
    {"type": "select",
      "label": "",
     "arrange": "previous",
     "name": "vertical_position",
     "options": ["Top", "Center", "Bottom"]
    }
    """
    


def options_to_html(options_list):
    html = []
    last_group = ""
    is_first_group = True
    for option in options_list:
        new_group = False
        group = option.get("group", "")
        if group != last_group:
            html.append("""%s<div class="option_group"><h3>%s</h3>"""
                        % ("</div>\n" if not is_first_group else "",
                        option["group"]))
            new_group = True
            last_group = group
            is_first_group = False
        
        if  option["type"] == "action" and option.get("arrange", "") =="previous":
            container_template = "%s"
        else:
            if "help" in option and option["type"] != "action":
                help = """title="%s" """ %option["help"]
            else:
                help = ""
            label = ("%s:" % option["label"]) if option.get("label", False) and (option["type"] not in ("radio", "action")) else ""
            container_template = "<p %s>%s%%s </p>\n" % (help, label)
        if option["type"] in ("select", "radio"):
            if "values" in options[option]:
                values = dict(zip(options[option]["options"], options[option]["values"]))
            else:
                values = options[option]["options"]
            
        if option["type"] == "select" :
            #sample output:
            """
            <p>Print Quality:
            <select name="print_quality">
                <option value="Fast Economy">Fast Economy</option>
                <option value="Standard" />Standard</option>
                <option value="Best" />Best</option
            </select>
            </p>
            """
            select_template = """<select name="%s">\n%s</select>\n"""
            option_template = """    <option value="%s">%s</option>\n"""
            options_html = []
            for value, select_option in zip(values, option["options"]):
                # FIXME: provision for different value and klabel for the options
                options_html.append(option_template % (value, select_option) )
            options_html = "".join (options_html) 
            html_render = select_template % (option["name"], options_html)
        elif option["type"] == "radio" :
            #sample output:
            """
            <div class="radio_group"><p class="radio_title">Print Quality:</p>
                <ul class="radio_options">
                   <li><input name="print_quality" type="radio" value="Fast Economy">Fast Economy</li>
                   <li><input  name="print_quality"  type="radio" value="Standard">Standard</li>
                </ul>
            </div>
            """
            select_template = """<ul class="radio_options">
                    %s
                </ul>
            """
            option_template = """      <li><input type="radio" name="%s" value="%s" %s>%s</li>\n"""
            options_html = []
            for value, select_option in zip(values, option["options"]):
                selected_html = """selected="1" """ if option.get("default", "")==value else ""
                options_html.append(option_template % (option["name"],
                                                       value, selected_html,
                                                       select_option) )
            options_html = "".join(options_html)
            html_render = select_template % (options_html,)
        elif option["type"] == "number":
            """
            <p>Blabla
            <input type="text" name="%s" width=5 />
            </p>
            """
            input_template = """
            <input type="text" name="%s" style="width: %dem;" />
            """
            html_render = input_template % (option["name"], option.get("width", 3) )
        elif option["type"] == "pannel":
            html_render = "Command output. Comming soon"
        elif option["type"] == "action":
            input_template = """
            <input class="submit_button" type="submit" name="command" value="%s"  %s/>
            """
            help = (""" title="%s" """ % option["help"]) if "help" in option else ""
            html_render = input_template % (option["label"], help)
        #EEEEeeek
        if  option["type"] == "action" and option.get("arrange", "") =="previous":
            html[-1] = html[-1].replace ( "</p>", html_render + "</p>")
        else:
            html.append(container_template % html_render)
    return "\n".join(html)


def get_template(template_name, environ):
    #Uses the "HOME" environment variable:
    template_path = os.path.join(TEMPLATE_DIR % environ, template_name)
    return Template(open(template_path).read())
    
def fill_template(template_name, environ, data):
    template = get_template(template_name, environ)
    safe_data = DefDict(data)
    text = template.substitute(safe_data)
    return text

def thumbnail_template(data, current_session):
    if "image" in current_session:
        data["thumb_template"] = THUMB_TEMPLATE
    else:
        data["thumb_template"] = ""

def default_handler_helper(environ, start_response, template="base.html", **data):
    respond_ok(start_response)
    text = fill_template(template, environ, data)
    return [text]


def redirect(environ, start_response, destination="/"):
    start_response("303 redirected", [("Location", destination)])
    return []

## HTTP Handlers
def retrieve_session_image_handler(environ, start_response, fields, *args):
    path = os.path.join(DATA_DIR, fields["image"].filename)
    #FIXME: use unix sockets to feed the mage itno GIMP
    tmp_file = open(path, "wb")
    tmp_file.write(fields["image"].file.read())
    tmp_file.close()
    img = pdb.gimp_file_load(path, path)
    #test_operation for debugging purposes :-p  :
    #pdb.gimp_colorize(img.layers[0], 0, 50, 0)
    image_sufix = "." + fields["image"].filename.rsplit(".",1)[-1]
    #FIXME: one saved image for session at a time, for now!
    out_path = os.path.join(DATA_DIR, str(current_session["id"]) + image_sufix)
    if os.path.exists(out_path):
        os.unlink(out_path)
    reset_session_images(current_session)
    #WARNING: currently not working in GIMP 2.7 master!
    # may have to adapt to the new file export semantics
    #works fine on gimp 2.6:
    pdb.gimp_file_save(img, img.layers[0], out_path, out_path)
    current_session["image_path"] = out_path
    current_session["image"] = img
    #FIXME: for development debugging only.  Redirect to main menu later.
    return redirect(environ, start_response, "/options")
    
def full_image_handler(environ, start_response, *args):
    if "image_path" in environ:
        image_path = environ["image_path"]
    elif "image_path" in current_session:
        image_path = current_session["image_path"]
    else:
        return redirect(environ, start_response, "/")
    file_stat = os.stat(image_path)
    length = str(file_stat.st_size)
    timestamp = file_stat.st_ctime
    http_timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(timestamp))
    print http_timestamp
    sufix = image_path.rsplit(".",1)[-1].lower()
    if sufix in ("jpg", "jpeg", "jpe"):
        image_type = "image/jpeg"
    else:
        image_type = "image/%s" % sufix
    start_response('200 OK', [('Content-Type', image_type), 
                              ('Content-Length', length),
                              ('Cache-Control', 'no-store'),
                              ('Last-Changed', http_timestamp)
                              ])
    return  open(image_path, "rb")
    
def thumbnail_handler(environ, start_response, *args):
    print "thumbnail", current_session
    if not "image" in current_session:
        start_response('404 NOT FOUND', [])
        return ["No image uploaded"]
    if not "thumbnail_path" in current_session:
        thumb_img = current_session["image"].duplicate()
        thumb_img.scale(THUMBNAIL_WIDTH, 
                        int(thumb_img.height / 
                             (thumb_img.width / float(THUMBNAIL_WIDTH))))
        image_sufix = "_thumb." + current_session["image_path"].rsplit(".",1)[-1]
        #FIXME: one saved image for session at a time, for now!
        out_path = os.path.join(DATA_DIR, str(current_session["id"]) + image_sufix)
        if os.path.exists(out_path):
            os.unlink(out_path)
        pdb.gimp_file_save(thumb_img, thumb_img.layers[0], out_path, out_path)
        current_session["thumbnail_path"] = out_path
        pdb.gimp_image_delete(thumb_img)
    environ["image_path"] = current_session["thumbnail_path"]
    return full_image_handler(environ, start_response)
    
def commit_print_handler(environ, start_response, *args):
    image_path = TEST_IMAGE_PATH % environ
    output_path = OUTPUT_PATH % environ
    if not "image_path" in current_session:
        #FIXME: 
        return info_handler(environ, start_response, *args)
    if "copies" in current_session:
        copies = int(current_session["copies"])
    else:
        copies = 1
    files_to_print = copies * [current_session["image_path"]]
    Popen(["photoprint", "-b" ] + files_to_print)
        
    
    #image = pdb.gimp_file_load(image_path, image_path)
    #drawable = image.layers[0]
    #data = {"image": image,
            #"drawable": drawable,
            #"output-to": output_path
           #}
    #gimp_print(data)
    #pdb.gimp_image_delete(image)
    respond_ok(start_response)
    return["<p>Test image printed</p>"]
    

def upload_image_handler(environ, start_response, *args):
    fields = cgi.FieldStorage(fp=environ['wsgi.input'],
        environ=environ,
        keep_blank_values=1)
    if "image" in fields:
        return retrieve_session_image_handler(environ, start_response, fields)
    return default_handler_helper(environ, start_response, body=UPLOAD_TEMPLATE)
    

def root_handler(environ, start_response, *args, **kw):
    d = {}
    #loads the html for displaying the image thumbnail:
    thumbnail_template(d, current_session)
    d["message"] = kw.get("message", "")
    return default_handler_helper(environ, start_response, body=MAIN_TEMPLATE % d)


def config_print_handler(environ, start_response, *args):
    """
    Presents an html form and reads information needed to print:
    
    """
    data = {}
    html_form = []
    fields = cgi.FieldStorage(fp=environ['wsgi.input'],
                environ=environ,
                keep_blank_values=1)
    if "print_parameters" not in current_session:
        load_default_parameters(current_session)
    print_parameters = current_session["print_parameters"]
    #loads the html for displaying the image thumbnail:
    thumbnail_template(data, current_session)
    #if the form has been submitted to us, update our values
    if "ok" in fields:
        for field in editable_controls:
            if field in fields:
                #TODO: call a validator here!
                print_parameters[field] = fields[field].value
        data["message"] = "Parameters updated!"
        #TODO: maybe redirect to print or main here?  
    else:
        data["message"] = ""
    # assemble form:
    for field in editable_controls:
        entry_data = {"label": field,
                      "name": field,
                      "value": print_parameters[field]
                     }
        html_form.append(WIDGET_ENTRY % entry_data)
    data["html_form"] = "\n".join(html_form)
    data["action"] = "config"
    return default_handler_helper(environ, start_response, body=FORM_TEMPLATE % data)
    
def info_handler(environ, start_response, *args):
    respond_ok(start_response)
    return(["<title>Print Server</title>", "<ul> %s </ul>" %   
    "".join (["<li><b>%s</b>: %s</li>"  % item for item in sorted(environ.items())] ) 
    ])
    
def reset_session_handler(environ, start_response, *args):
    reset_session(current_session["id"])
    return redirect(environ, start_response, "/")

def options_form_handler(environ, start_response, message="", *args):
    option_data = {}
    thumbnail_template(option_data, current_session)
    option_data["action"] = "/options_commit"
    option_data["message"] = message if message is not None else ""
    option_data["options_html"] = options_to_html(photoprint_options_list)
    body = fill_template("options.html", environ, option_data)
    html = fill_template("base.html", environ, {"body": body})
    respond_ok(start_response)
    return [html]

def photoprint_options_read(environ):
    config = MyConfigParser({}, OrderedDict)
    config.read([PHOTOPRINT_CONFIG % environ])
    return config

def photoprint_options_commit(environ, config):
    name = PHOTOPRINT_CONFIG % environ
    new_name = name + ".new"
    config_file = open(new_name, "wt")
    config.write(config_file)
    config_file.close()
    os.unlink(name)
    os.rename(new_name, name)

    
def photoprint_options_parse(values, options, config):
    for option in options:
        value = values[option]
        if "photoprint_config" in options[option]:
            session, key = options[option]["photoprint_config"]
            if "converter" in options[option]:
                value = options[option]["converter"](value)
            config.set(session, key, value)

def points_to_milimiters(n):
    return (n / 72.0) *  25.4

def programatic_config(values, options, config):
    if "width" in values:
        width = float(values["width"])
        page_width = int(config.get("Print", "CustomWidth"))
        stderr.write("Page width: %d" % page_width)
        page_width = points_to_milimiters(page_width)
        columns = max(int(page_width / width), 1)
        HGutter = int (page_width % int(width) / float(columns))
        config.set("Layout_NUp", "Columns", str(columns))
        config.set("Layout_NUp", "HGutter", HGutter)

    if "height" in values:
        height = float(values["height"])
        page_height = int(config.get("Print", "CustomHeight"))
        page_height = points_to_milimiters(page_height)
        rows = max(1, int(page_height / height))
        VGutter = int (page_height % int(height) / float(rows))
        config.set("Layout_NUp", "Rows", str(rows))
        config.set("Layout_NUp", "VGutter", VGutter)

    if "copies" in options:
        current_session["copies"] = int(values["copies"])
        
    

def options_form_validate(values, options):
    errors = []
    for option in options:
        type_ = options[option]["type"]
        value = values[option]
        name = options[option]["label"] if options[option]["label"] else options[option]["name"]
        if type_ == "select":
            #if "values" in options[option]:
                #values = dict(zip(options[option]["options"], options[option]["values"]))
            #else:
                #values = options[option]["options"]
            if not value in values:
                errors.append("""Invalid value "%s" for option "%s" """ %
                               (value, name))
        elif type_ == "number":
            try:
                n = float(value)
            except ValueError:
                errors.append("""Option "%s" should be given a numeric value""" % name)
                continue
            if "validrange" in options[option]:
                minv, maxv = options[option]["validrange"]
                if not minv <= n <= maxv:
                    errors.append("""Values for option "%s" should be between %d and %d""" % (name, minv, maxv)) 
    return errors
    
def options_commit_handler(environ, start_response, *args):
    fields = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ,
                                keep_blank_values=1)
    #extract values to change in photoprint config file
    values = {}
    values_options = {}
    for option in photoprint_options_list:
        opt_name = option.get("name", "")
        if opt_name in fields and fields[opt_name].value:
            values[opt_name] = fields[opt_name].value
            values_options[opt_name] = option
    
    #verify values
    errors = options_form_validate(values, values_options)
    if errors:
        error_template = """<p class="error">%s</p>"""
        error_html = "<br />".join(errors)
        return options_form_handler(environ, start_response, 
                                    message=error_html)
    if "command" in fields:
        #commit action
        response = main_action(fields["command"].value, fields, environ, values_options, values)
    
    return root_handler(environ, start_response, message="<p>Options saved</p>")

def main_action (action,  fields, environ, values_options, values):
    sys.stderr.write("action: %s\n" % action)
    if action == "Refresh Queue":
        pass
    elif action == "Clear Queue":
        pass
    elif action == "Nozzle Check":
        pass
    elif action == "Cleaning":
        pass
    elif action == "Cancel":
        pass
    elif action == "Print":
        #commit values to photoprint config file
        config = photoprint_options_read(environ)
        photoprint_options_parse(values, values_options, config)
        programatic_config(values, values_options, config)
        photoprint_options_commit(environ, config)
        pass
    elif action == "Save As Default":
        pass
    elif action == "Load Settings":
        pass
    else:
        sys.stderr.write("warning: unrecognized command option. Ignoring\n")
    return action


registered_handlers = {
    "": root_handler,
    "/": root_handler,
    "/config": config_print_handler,
    "/options": options_form_handler,
    "/options_commit": options_commit_handler,
    "/print": commit_print_handler,
    "/upload": upload_image_handler,
    "/info": info_handler,
    "/image": full_image_handler,
    "/thumbnail": thumbnail_handler,
    "/reset": reset_session_handler
    }


def respond_ok(start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    
def get_parameters(environ):
    if not "QUERY_STRING" in environ:
        return {}
    param_tuple = unquote_plus(environ["QUERY_STRING"]).split("&")
    parameters = {}
    for param in param_tuple:
        if "=" in param:
            key, value = param.split("=", 1)
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            parameters[key] = value
        else:
            parameters[param] = None

def get_path(environ):
    if not "PATH_INFO" in environ:
        return ""
    return environ["PATH_INFO"]

def make_session_id(environ):
    return hash(environ["HTTP_USER_AGENT"] + 
                environ["REMOTE_ADDR"] + 
                environ["HTTP_HOST"])

def reset_session_images(session):
    if "image" in session:
        try:
            pdb.gimp_image_delete(session["image"])
        except RuntimeError:
            pass
    if "image_path" in session:
        if os.path.exists(session["image_path"]):
            os.unlink(session["image_path"])
        del session["image_path"]
    if "thumbnail_path" in session:
        if os.path.exists(session["thumbnail_path"]):
            os.unlink(session["thumbnail_path"])
        del session["thumbnail_path"]
    
def reset_session(session_id):
    global current_session
    if session_id in sessions:
        session = sessions[session_id]
        reset_session_images(session)
    sessions[session_id] = {"id": session_id, "auth": False}
    current_session = sessions[session_id]
    
def http_server(environ, start_response):
    #FIXME: extremely light session management 
    # this app should be used in a small lan, with very few
    # transactions at a time.
    #Authentication is only needed for the configuration screen
    # (when it is implemented).
    # of special interest: the same broswer id from the same IP
    # will use the same session - even with a different user logged in
    session_id = make_session_id(environ)
    if not session_id in sessions:
        reset_session(session_id)
    parameters = get_parameters(environ)
    path = get_path(environ)
    if path in registered_handlers:
        return registered_handlers[path](environ, start_response, parameters)
    else:
        start_response("404 NOT FOUND", [])
        return []
    

def http_print_server(port, password):
    global admin_password
    admin_password = password
    srv = make_server('localhost', port, http_server)
    srv.serve_forever()
    

register(
         "http_print_server",
         "Presents a WEB printing interface using GIMP",
         "Presents a WEB printing interface using GIMP",
         "Joao S. O. Bueno",
         "Joao S. O. Bueno, GPL v3.0 or later",
         "2009",
         "Print Server...",
         "",
         [
           (PF_INT, "port", "Port for server to run", 4080),
           (PF_STRING, "password", "Administrative password", "")
         ],
         [],
         http_print_server,
         menu="<Image>/File/")
main()
         