#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import math
from gimpfu import *

# GIMP plugin to create simple path shapes centered in the image.
# (c) MareroQ 2016 http://gimpchat.com/viewtopic.php?f=9&t=14742&hilit=simple+shape+path
# ...

# License: GPLv3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# To view a copy of the GNU General Public License
# visit: http://www.gnu.org/licenses/gpl.html
#
# ------------
#| Change Log |
# ------------
# Rel 0.1: Initial release.
# Rel 0.2: Add shapes: "Pentagon","Star pentagons","Pentagram","Yin-Yang","Petals","Quadrant","Flower".
# Rel 0.3: Add border to layer - requires Changing Image Border.scm. The combined two scripts:
#          by TheUncle2k (http://theuncle2k.deviantart.com/art/Resize-image-to-layers-150439776) "Resize_image_to_layers_by_theuncle2k.scm"
#          and Art Wade (fencepost) "All-layers-to-image-size.scm". Thanks for authors.
#          Add shapes: "Trefoil","Quatrefoil","Cross","Crescent","Pie","Semicircle", "Arrow"   
#          Sorted shapes alphabetical
# Rel 0.4: Add shapes: "Octagon","Triangle Reuleaux (curvilinear)","Flower" divided into two (in and out).
#          Add option shape in selection.
#          Add option inspired by Dinasset "Stroke Color" and "Fill Pattern" created by Tin Tran (http://bakon.ca/gimplearn/viewtopic.php?f=3&t=141#p324). Thanks Trandoductin!.
# Rel 0.5: Add shapes: "Recycle".
#          Included: needed stroke outside the selection.
# Rel 0.6  Add shapes: "Roses compass 4-point"
#          				and "Ruler" created by Tin Tran (Draw Percentage Ruler Script for GIMP: http://bakon.ca/gimplearn/viewtopic.php?f=3&t=139&p=320#p320)
# Rel 0.7  Add shapes: "Dodecagon","Mobius band"
# Rel 0.8  Add shapes: "Recycle symbol" (experimental for Mahvin)
#					   "Binoculars"
#                  		and "Protractor" created by Tin Tran (Draw_Protractor Rel 1: http://bakon.ca/gimplearn/viewtopic.php?f=3&t=175#p512)
# Rel 0.9  Repair of error for "Protractor" and "Ruler" (not centered when no selection).
#          Show a selection, after you run the shape, when you select "In Selection" on the menu.
#          "Protractor" rel 3: Draw marks as a single stroke for speed, outside and inside circle
#          Add shape: "Wilber"
# Rel 1.0 alfa: Show a selection only when you select "In Selection" on the menu (no show for no selection)
#               Add shapes "Grid" (Grid rectangular (c) Ofnuts v0.0 https://sourceforge.net/projects/gimp-path-tools/files/scripts/
#				Add shapes "Pie 1/2 and 7/8"
#               Add a separate option for Mark Length
#               Add fills selection with Active Brush created by Tin Tran (Fill_Selection_With_Brush ver.3 http://bakon.ca/gimplearn/viewtopic.php?f=3&t=177#p522)
#				Shape "Ruler" return to the basic version.
# Rel 1.0 beta: Repair of error for Gimp 2.9 (called deprecated procedure 'gimp_selection_load'.It should call 'gimp-image-select-item' instead!)
#               Add transparency layer (create new) for fill and stroke
# Rel 1.0   Correction shapes "Recycle" (bad axis)
#           Add shapes "Gear", "Star" Polygon" created by Jonathan Stipe 2004-2006(necessary script-fu Shape-path.scm)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#==============================================================================================================================================================================
#Small changes by PKHG 15 dec 2016
def color_to_hex(color):
	whole_color = (color[0],color[1],color[2]);
	return '#%02x%02x%02x' % whole_color
def vector_to_line_stroke(image, vector, layer, color="#000000", width=1, capstyle="butt", joinstyle="miter", miterlimit=10, shaperendering="auto"):
    import re, tempfile
    import os, string, sys
    newelements = {
            'stroke': color,
            'stroke-width': width,
            'stroke-linecap': capstyle,
            'stroke-linejoin': joinstyle,
            'stroke-miterlimit': miterlimit,
			'shape-rendering': shaperendering,
            }
    svg = pdb.gimp_vectors_export_to_string(image, vector)
    #fix width and height to be resolution (px/inch)-independent
    svg = re.sub(r'(<svg\s[^>]*\swidth\s*=\s*)\S*"', r'\1"%dpx"' % image.width, svg, flags=re.DOTALL)
    svg = re.sub(r'(<svg\s[^>]*\sheight\s*=\s*)\S*"', r'\1"%dpx"' % image.height, svg, flags=re.DOTALL)
    svg = re.sub(r'(<path\s[^>]*)\sstroke\s*=\s*"black"', r'\1', svg, flags=re.DOTALL)
    svg = re.sub(r'(<path\s[^>]*)\sstroke-width\s*=\s*"1"', r'\1', svg, flags=re.DOTALL)
    svg = re.sub(r'(<path\s)', r'\1' + ''.join([r'%s="%s" ' % i for i in newelements.items()]), svg, flags=re.DOTALL)
    tmpfile = tempfile.TemporaryFile(suffix=".svg")
	
    #gets just the file name to use, added by Tin Tran, tempFile.TemporaryFile above gave write permission error
    filename = os.path.basename(tmpfile.name)
    svgfile =  "~\\.gimp-2.8\\tmp\\" + filename
    svgfile = os.path.expanduser(svgfile)
    tmpfile = open(svgfile,"w")
	#end of addition by Tin Tran
	
    tmpfile.write(svg)
    tmpfile.flush();
    newlayer = pdb.gimp_file_load_layer(image, tmpfile.name)
    tmpfile.close()
    image.add_layer(newlayer) #needs to be added to the image to be able to copy from
    copyname = pdb.gimp_edit_named_copy(newlayer, "stroke")
    image.remove_layer(newlayer)
    floating_sel = pdb.gimp_edit_named_paste(layer, copyname, True)
    pdb.gimp_floating_sel_anchor(floating_sel)
	
    #added by Tin Tran, remove the file when we're done
    os.remove(svgfile)
#=====================================================================================================================
def newline(x1, y1, x2, y2):
    return [x1,y1]*3+[x2,y2]*3

def plugin_simple_shapes_centered(image, layer, sel, s, R_1, R, L, T, B,
         R_2, M_L, H_L, V_L, R_L, fill, fillpattern, stroke, strokecolor, strokewidth):

	pdb.gimp_image_undo_group_start(image)
	pdb.gimp_context_push()
	before_vectors = list(image.vectors)
	selection = pdb.gimp_selection_bounds(image)
        """
	x1 = selection[1];
	y1 = selection[2];
	x2 = selection[3];
	y2 = selection[4];
        """
        x1, y1, x2, y2 = selection[1:]
	
	if sel:
		temp = pdb.gimp_selection_save(image)
		if x2-x1>=y2-y1:
			m = (x1+x2-y2+y1)/2
			v = y1
			W = (y2 - y1)
			H = (y2 - y1)
			W1 = 2*(x1+(x2 - x1)/2)
			H1 = 2*(y1+(y2 - y1)/2)
			j = x1
			k = y1
		else:
			m = x1
			v = (y1+y2-x2+x1)/2
			W = x2 - x1
			H = x2 - x1
			W1 = 2*(x1+(x2 - x1)/2)
			H1 = 2*(y1+(y2 - y1)/2)
			j = x1
			k = y1

	else:
		W1 = pdb.gimp_image_width(image)  #szer
		H1 = pdb.gimp_image_height(image) #wys
		k = 0
		j = 0
		if W1>H1:
			m =(W1-H1)/2
			v = 0
			W = H1
			H = H1

		else:
			m = 0
			v = (H1-W1)/2
			W = W1
			H = W1
        Wd8 = W / 8
	if s==0: # Arrow

		new_vectors = pdb.gimp_vectors_new(image,"Arrow >")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 84,
		(5*Wd8 +m, Wd8 +v,5*Wd8 +m, Wd8 +v,5*Wd8 +m, Wd8 +v,   5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v,5*Wd8 +m,3*Wd8 +v,
		5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v,5*Wd8 +m,3*Wd8 +v,   m,3*Wd8 +v,m,3*Wd8 +v,m,3*Wd8 +v,
		m,3*Wd8 +v, m,3*Wd8 +v, m,3*Wd8 +v,   m,5*Wd8 +v, m,5*Wd8 +v, m,5*Wd8 +v,
		m,5*Wd8 +v, m,5*Wd8 +v, m,5*Wd8 +v,   5*Wd8 +m,5*Wd8 +v, 5*Wd8 +m,5*Wd8 +v, 5*Wd8 +m,5*Wd8 +v,
		5*Wd8 +m,5*Wd8 +v, 5*Wd8 +m,5*Wd8 +v, 5*Wd8 +m,5*Wd8 +v,  5*Wd8 +m,7*Wd8 +v, 5*Wd8 +m,7*Wd8 +v,5*Wd8 +m,7*Wd8 +v,
		5*Wd8 +m,7*Wd8 +v, 5*Wd8 +m,7*Wd8 +v,5*Wd8 +m,7*Wd8 +v,   W +m,W/2 +v,W +m,W/2 +v,W +m,W/2 +v,
		W +m,W/2 +v,W +m,W/2 +v,W +m,W/2 +v,   5*Wd8 +m, Wd8 +v,5*Wd8 +m, Wd8 +v,5*Wd8 +m, Wd8 +v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Arrow ^")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 84,
		(W/2 +m, v,W/2 +m, v,W/2 +m, v,    Wd8 +m,3*Wd8 +v, Wd8 +m,3*Wd8 +v,Wd8 +m,3*Wd8 +v,
		Wd8 +m,3*Wd8 +v, Wd8 +m,3*Wd8 +v,Wd8 +m,3*Wd8 +v,  3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,
		3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,  3*Wd8+m,W+v,3*Wd8+m,W+v,3*Wd8+m,W+v,
		3*Wd8+m,W+v,3*Wd8+m,W+v,3*Wd8+m,W+v,  5*Wd8 +m,W +v, 5*Wd8 +m,W +v,5*Wd8 +m,W +v,
		5*Wd8 +m,W +v, 5*Wd8 +m,W +v,5*Wd8 +m,W +v,  5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v,5*Wd8 +m,3*Wd8 +v,
		5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v,5*Wd8 +m,3*Wd8 +v,  7*Wd8 +m,3*Wd8 +v,7*Wd8 +m,3*Wd8 +v,7*Wd8 +m,3*Wd8 +v,
		7*Wd8 +m,3*Wd8 +v,7*Wd8 +m,3*Wd8 +v,7*Wd8 +m,3*Wd8 +v,  W/2 +m, v,W/2 +m, v,W/2 +m, v,), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Arrow <")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 84,
		(3*Wd8 +m,Wd8 +v,3*Wd8 +m,Wd8 +v,3*Wd8 +m,Wd8 +v,   m, W/2+v,m, W/2+v,m, W/2+v,
		m, W/2+v,m, W/2+v,m, W/2+v,    3*Wd8 +m, 7*Wd8 +v, 3*Wd8 +m, 7*Wd8 +v, 3*Wd8 +m, 7*Wd8 +v, 
		3*Wd8 +m, 7*Wd8 +v, 3*Wd8 +m, 7*Wd8 +v,   3*Wd8 +m, 5*Wd8 +v,3*Wd8 +m, 5*Wd8 +v,3*Wd8 +m, 5*Wd8 +v,
		3*Wd8 +m,5*Wd8 +v, 3*Wd8 +m,5*Wd8 +v, 3*Wd8 +m,5*Wd8 +v,   W+m, 5*Wd8 +v,W+m, 5*Wd8 +v,W+m, 5*Wd8 +v,
		W+m, 5*Wd8 +v,W+m, 5*Wd8 +v,W+m, 5*Wd8 +v,   W+m, 3*Wd8 +v,W+m, 3*Wd8 +v,W+m, 3*Wd8 +v,
		W+m, 3*Wd8 +v,W+m, 3*Wd8 +v,W+m, 3*Wd8 +v,  3*Wd8 +m,3*Wd8 +v, 3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,
		3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v, 3*Wd8 +m,Wd8 +v,3*Wd8 +m,Wd8 +v,3*Wd8 +m,Wd8 +v,), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Arrow v")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 84,
		(3*Wd8 +m,v, 3*Wd8 +m,v, 3*Wd8 +m,v,   3*Wd8 +m,5*Wd8 +v,3*Wd8 +m,5*Wd8 +v,3*Wd8 +m,5*Wd8 +v,
		3*Wd8 +m,5*Wd8 +v,3*Wd8 +m,5*Wd8 +v,3*Wd8 +m,5*Wd8 +v,   Wd8 +m,5*Wd8 +v,Wd8 +m,5*Wd8 +v,Wd8 +m,5*Wd8 +v,
		Wd8 +m,5*Wd8 +v,Wd8 +m,5*Wd8 +v,Wd8 +m,5*Wd8 +v,     W/2 +m,W +v, W/2 +m,W +v, W/2 +m,W +v, 
		W/2 +m,W +v, W/2 +m,W +v, W/2 +m,W +v,  7*Wd8 +m,5*Wd8 +v, 7*Wd8 +m,5*Wd8 +v, 7*Wd8 +m,5*Wd8 +v, 
		7*Wd8 +m,5*Wd8 +v, 7*Wd8 +m,5*Wd8 +v,7*Wd8 +m,5*Wd8 +v,  5*Wd8 +m,5*Wd8 +v,5*Wd8 +m,5*Wd8 +v,5*Wd8 +m,5*Wd8 +v,
		5*Wd8 +m,5*Wd8 +v,5*Wd8 +m,5*Wd8 +v,5*Wd8 +m,5*Wd8 +v,   5*Wd8 +m,v,5*Wd8 +m,v,5*Wd8 +m,v,
		5*Wd8 +m,v,5*Wd8 +m,v,5*Wd8 +m,v,   3*Wd8 +m,v, 3*Wd8 +m,v,3*Wd8 +m,v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==1: # Axis of symmetry
		new_vectors = pdb.gimp_vectors_new(image,"Axis of symmetry")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 12,
                                        newline(W1/2, k, W1/2, H1-k), 0)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 12,
                                        newline(j, H1/2, W1-j, H1/2), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==2: # Binoculars
		f= M_L
		g = f/2
		h = f/4

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,W/4+v-h ,W/2+g ,W/2+g)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.name = active_vectors.name.replace("Selection", "Bin-BL big")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Bin-BL big")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m+f ,W/4+v-h+f ,W/2+g-2*f ,W/2+g-2*f)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.name = active_vectors.name.replace("Selection", "Bin-BL small")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Bin-BL small")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, W/2+m-f+g ,W/4+v-h ,W/2+g ,W/2+g)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.name = active_vectors.name.replace("Selection", "Bin-RL big")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Bin-RL big")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0,  W/2+m+g ,W/4+v-h+f ,W/2+g-2*f ,W/2+g-2*f)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.name = active_vectors.name.replace("Selection", "Bin-RL small")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Bin-RL small")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,W/4+v-h ,W/2+g ,W/2+g)
		pdb.gimp_image_select_ellipse(image, 1, m+f ,W/4+v-h+f ,W/2+g-2*f ,W/2+g-2*f)
		pdb.gimp_image_select_ellipse(image, 0, W/2+m-f+g ,W/4+v-h ,W/2+g ,W/2+g)
		pdb.gimp_image_select_ellipse(image, 1,  W/2+m+g ,W/4+v-h+f ,W/2+g-2*f ,W/2+g-2*f)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Binoculars")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Binoculars")

	if s==3: # Circle
		new_vectors = pdb.gimp_vectors_new(image,"Circle")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,W/2+m ,W/2+v ,W/2 ,W/2, 0)
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==4: # Crescent

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, Wd8+m ,v ,W ,W)
		pdb.gimp_image_select_ellipse(image,1, W/2+m, W/16+v, 7*Wd8, 7*H/8)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Crescent")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Crescent")
		pdb.gimp_selection_none(image)
		
	if s==5: # Cross

		new_vectors = pdb.gimp_vectors_new(image,"Cross")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 144,
		(3*Wd8 +m, v, 3*Wd8 +m, v, 3*Wd8 +m, v,    3*Wd8 +m,3*Wd8 +v, 3*Wd8 +m,3*Wd8 +v, 3*Wd8 +m,3*Wd8 +v,
		3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,3*Wd8 +m,3*Wd8 +v,     m,3*Wd8 +v, m,3*Wd8 +v, m,3*Wd8 +v,
		m,3*Wd8 +v, m,3*Wd8 +v, m,3*Wd8 +v,    m,5*Wd8 +v, m,5*Wd8 +v, m,5*Wd8 +v,
		m,5*Wd8 +v, m,5*Wd8 +v, m,5*Wd8 +v,   3*Wd8 +m,5*Wd8 +v, 3*Wd8 +m,5*Wd8 +v, 3*Wd8 +m,5*Wd8 +v,
		3*Wd8 +m,5*Wd8 +v, 3*Wd8 +m,5*Wd8 +v, 3*Wd8 +m,5*Wd8 +v,   3*Wd8 +m,W +v, 3*Wd8 +m,W +v, 3*Wd8 +m,W +v,
		3*Wd8 +m,W +v, 3*Wd8 +m,W +v, 3*Wd8 +m,W +v,   5*Wd8 +m,W +v, 5*Wd8 +m,W +v, 5*Wd8 +m,W +v,
		5*Wd8 +m,W +v, 5*Wd8 +m,W +v, 5*Wd8 +m,W +v,   5*Wd8 +m,5*Wd8 +v,5*Wd8 +m,5*Wd8 +v,5*Wd8 +m,5*Wd8 +v,
		5*Wd8 +m,5*Wd8 +v, 5*Wd8 +m,5*Wd8 +v, 5*Wd8 +m,5*Wd8 +v,   W+m, 5*Wd8+v, W+m, 5*Wd8+v, W+m, 5*Wd8+v,
		W+m, 5*Wd8+v, W+m, 5*Wd8+v, W+m, 5*Wd8+v,    W+m, 3*Wd8+v, W+m, 3*Wd8+v, W+m, 3*Wd8+v,
		W+m, 3*Wd8+v, W+m, 3*Wd8+v, W+m, 3*Wd8+v,  5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v,
		5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v, 5*Wd8 +m,3*Wd8 +v,   5*Wd8 +m,v, 5*Wd8 +m,v, 5*Wd8 +m,v,
		5*Wd8 +m,v, 5*Wd8 +m,v, 5*Wd8 +m,v,   3*Wd8 +m, v, 3*Wd8 +m, v, 3*Wd8 +m, v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==6: # Diagonals
		new_vectors = pdb.gimp_vectors_new(image,"Diagonals")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 12, newline( j, k, W1-j, H1-k), 0)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 12, newline( W1-j, k, j, H1-k), 0)
		pdb.gimp_item_set_visible(new_vectors, 1)

	if s==7: # Diamond
		new_vectors = pdb.gimp_vectors_new(image,"Diamond")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 48, 
		(W/2+m, v, W/2+m, v, W/2+m, v, W+m, W/2+v, W+m, W/2+v, W+m, W/2+v,
		W+m, W/2+v, W+m, W/2+v, W+m, W/2+v, W/2+m, W+v, W/2+m, W+v, W/2+m, W+v,
		W/2+m, W+v,W/2+m, W+v,W/2+m, W+v,  m, W/2+v, m, W/2+v, m, W/2+v,
		m, W/2+v,m, W/2+v,m, W/2+v,  W/2+m, v,W/2+m, v,W/2+m, v),0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==8: # Dodecagon
		d = W/2 - math.sqrt(3)*W/4

		new_vectors = pdb.gimp_vectors_new(image,"Dodecagon")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 144,
		(W/2+m, v, W/2+m, v, W/2+m, v,   W/4+m, d+v,W/4+m, d+v,W/4+m, d+v,
		W/4+m, d+v,  W/4+m, d+v,  W/4+m, d+v,   d+m, W/4+v, d+m, W/4+v, d+m, W/4+v,
		 d+m, W/4+v, d+m, W/4+v, d+m, W/4+v,   m, W/2+v, m, W/2+v, m, W/2+v,
		m, W/2+v,m, W/2+v,m, W/2+v,    d +m, 3*W/4 +v,d +m, 3*W/4 +v,d +m, 3*W/4 +v,
		d +m, 3*W/4 +v,d +m, 3*W/4 +v,d +m, 3*W/4 +v,   W/4+m, W-d+v,W/4+m, W-d+v,W/4+m, W-d+v, 
		W/4+m, W-d+v,W/4+m, W-d+v,W/4+m, W-d+v,   W/2+m, W+v,W/2+m, W+v,W/2+m, W+v,
		W/2+m, W+v,W/2+m, W+v,W/2+m, W+v,     3*W/4+m, W-d +v,3*W/4+m, W-d +v,3*W/4+m, W-d +v,
		3*W/4+m, W-d +v,3*W/4+m, W-d +v,3*W/4+m, W-d +v,    W-d+m, 3*W/4+v,W-d+m, 3*W/4 +v,W-d+m, 3*W/4 +v,
		W-d+m, 3*W/4+v,W-d+m, 3*W/4 +v,W-d+m, 3*W/4 +v,   W+m, W/2+v, W+m, W/2+v, W+m, W/2+v,
		W+m, W/2+v, W+m, W/2+v, W+m, W/2+v,   W-d+m, W/4+v,W-d+m, W/4+v,W-d+m, W/4+v,
		W-d+m, W/4+v,W-d+m, W/4+v,W-d+m, W/4+v,  3*W/4 +m, d+v,3*W/4 +m, d+v,3*W/4 +m, d+v,
		3*W/4 +m, d+v,3*W/4 +m, d+v,3*W/4 +m, d+v,  W/2+m, v, W/2+m, v, W/2+m, v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)		
		
	if s==9: # Ellipse
		new_vectors = pdb.gimp_vectors_new(image,"Ellipse")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,W/2+m ,W/2+v, W/2+m-j ,W/2+v-k, 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==10: # Flower 1 Out
		e = W/2 - math.sqrt(3)*W/4
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v, W ,W)
		pdb.gimp_image_select_ellipse(image, 3, -W/2+e+m ,-3*W/4+v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fo_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fo_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v, W ,W)
		pdb.gimp_image_select_ellipse(image, 3, -W+2*e+m,v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fo_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fo_2")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, -W/2+e+m,3*W/4 + v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fo_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fo_3")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W/2-e+m,3*W/4 + v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fo_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fo_4")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W-2*e+m,v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fo_5")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fo_5")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W/2-e+m,-3*W/4+v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fo_6")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fo_6")
		pdb.gimp_selection_none(image)

	if s==11: # Flower 2 In
		e = W/2 - math.sqrt(3)*W/4
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, -W/2+e+m ,-W/4 +v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W/2-e+m ,-W/4 + v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fi_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fi_1")
		
		pdb.gimp_selection_none(image)		
		pdb.gimp_image_select_ellipse(image, 0, m ,-W/2+v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, -W/2 +e+m ,W/4+v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fi_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fi_2")
	
		pdb.gimp_selection_none(image)		
		pdb.gimp_image_select_ellipse(image, 0, -W/2+e+m ,-W/4 +v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, m ,W/2+v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fi_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fi_3")
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, -W/2 +e+m ,W/4+v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W/2-e+m ,W/4+v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fi_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fi_4")
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0,m ,W/2+v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W/2-e+m ,-W/4 + v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fi_5")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fi_5")
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,-W/2+v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 3, W/2-e+m ,W/4+v ,W ,W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Fi_6")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Fi_6")
		pdb.gimp_selection_none(image)

	if s==12: # GEAR
		oradius=(H_L)*W/200  #Outer Radius=H
		iradius=(V_L)*W/200  #Inner Radius=V
		teeth=M_L            #Number of teeth=M->L
		rotation=R_L
		pdb.script_fu_gear_path_ssc(image, layer, 'Gear', W/2+m, H/2+v, oradius, iradius, teeth, rotation, run_mode=RUN_NONINTERACTIVE)
		
	if s==13: # Grid rectangular (c) Ofnuts v0.0
# Start Grid======================================================================================================================================
#   v0.0: 2013-04-20 first published version
#   v0.1: 2014-01-25 add entry for Offset & Spacing specification  https://sourceforge.net/projects/gimp-path-tools/files/scripts/
		def strokePoints(x1,y1,x2,y2):
			return [x1,y1]*3+[x2,y2]*3
			
		def steps(first,last,count):
			step=(last-first)/(count-1.)
		#	print 'Step(%3.2f,%3.2f,%d)=%3.2f' % (first,last,count,step)
			return [first+(step*x) for x in range(count-1)]+[last]

		class GridPathSelectionRenderer(object):
			if sel == True:
				def __init__(self,image,linesH,linesV):
					self.image=image
					self.linesH=linesH
					self.linesV=linesV
				
					self.minX=0
					self.maxX=0
					self.minY=0
					self.maxY=0
			if sel == False:
				def __init__(self,image,linesH,linesV):
					pdb.gimp_selection_none(image)
					self.image=image
					self.linesH=linesH
					self.linesV=linesV
				
					self.minX=m
					self.maxX=W1+m
					self.minY=v
					self.maxY=H1+v

			def generateVerticalStrokes(self):
				for x in steps(self.minX,self.maxX,self.linesV):
					points=strokePoints(x,self.minY,x,self.maxY)
					pdb.gimp_vectors_stroke_new_from_points(self.path,0, len(points),points,False)
					
			def generateHorizontalStrokes(self):
				for y in steps(self.minY,self.maxY,self.linesH):
					points=strokePoints(self.minX,y,self.maxX,y)
					pdb.gimp_vectors_stroke_new_from_points(self.path,0, len(points),points,False)
			
			def run(self):
				defined,self.minX,self.minY,self.maxX,self.maxY=pdb.gimp_selection_bounds(self.image)
				self.path=pdb.gimp_vectors_new(self.image, 'Grid %d x %d' % (self.linesH,self.linesV))
				pdb.gimp_image_add_vectors(self.image, self.path, 0)
				if self.linesV > 1:
					self.generateVerticalStrokes()
				if self.linesH > 1:
					self.generateHorizontalStrokes()
				self.path.visible=True	
			
		class GridPathRenderer(object):
			def __init__(self,image):
				self.image=image
				
				self.minX=0
				self.maxX=image.width
				self.minY=0
				self.maxY=image.height

			def generateVerticalStrokes(self):
				x=self.minX+self.offsetH
				while x<self.maxX: 
					points=strokePoints(x,self.minY,x,self.maxY)
					pdb.gimp_vectors_stroke_new_from_points(self.path,0, len(points),points,False)
					x+=self.spacingH
					
			def generateHorizontalStrokes(self):
				y=self.minY+self.offsetV
				while y<self.maxY: 
					points=strokePoints(self.minX,y,self.maxX,y)
					pdb.gimp_vectors_stroke_new_from_points(self.path,0, len(points),points,False)
					y+=self.spacingV
			def run(self):
				defined,self.minX,self.minY,self.maxX,self.maxY=pdb.gimp_selection_bounds(self.image)
				self.path=pdb.gimp_vectors_new(self.image, 'Grid %3.1fx%3.1f@%3.1f,%3.1f' % (self.spacingH,self.spacingV,self.offsetH,self.offsetV))
				pdb.gimp_image_add_vectors(self.image, self.path, 0)
				if self.spacingH > 0.:
					self.generateVerticalStrokes()
				if self.spacingV > 0:
					self.generateHorizontalStrokes()
				self.path.visible=True
	#if sel == True:
		linesH = H_L
		linesV = V_L
	try:
		GridPathSelectionRenderer(image,int(linesH),int(linesV)).run()

        except Exception as e:
		print
		



# End Grid =======================================================================================================================================	

	if s==14: # Hexagon
		d = W/2 - math.sqrt(3)*W/4

		new_vectors = pdb.gimp_vectors_new(image,"Hexagon")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 72,
		(W/4+m, d+v,  W/4+m, d+v,  W/4+m, d+v,        W/2+W/4+m,d+v,  W/2+W/4+m, d+v,    W/2+W/4+m, d+v,
		W/4+m, d+v,  W/4+m, d+v,  W/4+m, d+v,       m, W/2 +v, m, W/2 +v,m, W/2 +v,
		m, W/2 +v, m, W/2 +v,m, W/2 +v,               W/4+m, W-d+v,  W/4+m, W-d+v,  W/4+m,W-d+v, 
		W/4+m, W-d+v,  W/4+m, W-d+v,  W/4+m,W-d+v,      W/2+W/4+m, W-d+v, W/2+W/4+m, W-d+v,W/2+W/4+m, W-d+v,
		W/2+W/4+m, W-d+v, W/2+W/4+m, W-d+v,W/2+W/4+m, W-d+v,     W+m, W/2 +v, W+m, W/2 +v,W+m, W/2 +v,
		W+m, W/2 +v, W+m, W/2 +v,W+m, W/2 +v, W/2+W/4+m,d+v,  W/2+W/4+m, d+v,    W/2+W/4+m, d+v,), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==15: # Mobius band

		b = 3*W/(8*math.tan(math.pi/6))
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_polygon(image, 0, 10, (3*Wd8+m,v,   m, b+v,    Wd8+m,7*Wd8+v,  5*Wd8 +m, v,  3*Wd8+m,v ))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Mobius band_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Mobius band_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_polygon(image, 0, 10, (7*Wd8+m,7*Wd8+v, 3*Wd8+m,v, 5*Wd8+m,v, W+m, b+v, 7*Wd8+m,7*Wd8+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Mobius band_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Mobius band_2")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_polygon(image, 0, 10, (m, b+v,  Wd8+m,7*Wd8+v,  7*Wd8+m,7*Wd8+v, W+m, b+v, m, b+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Mobius band_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Mobius band_3")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_polygon(image, 0, 10, (3*Wd8+m,v,   m, b+v,    W/4+m,b+v,  5*Wd8 +m, v,  3*Wd8+m,v ))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Mobius alternative-3-2-A")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Mobius alternative-3-2-A")		
		
	if s==16: # Octaagon
		a = W*math.sqrt(2)/(2+math.sqrt(2))
		b = a/math.sqrt(2)

		new_vectors = pdb.gimp_vectors_new(image,"Octagon")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 96,(
		b+a+m, v, b+a+m, v,b+a+m, v,  b+m,v,b+m,v,b+m,v,
		b+m,v,b+m,v,b+m,v,   m, b+v, m, b+v,m, b+v,
		m, b+v, m, b+v,m, b+v,  m, a+b+v,m, a+b+v,m, a+b+v,
		m, a+b+v,m, a+b+v,m, a+b+v, b+m,W+v,b+m,W+v,b+m,W+v,
		b+m,W+v,b+m,W+v,b+m,W+v, a+b+m,W+v, a+b+m,W+v,
		a+b+m,W+v, a+b+m,W+v, a+b+m,W+v,  W+m,a+b+v,W+m,a+b+v,W+m,a+b+v,
		W+m,a+b+v,W+m,a+b+v,W+m,a+b+v,   W+m, b+v ,W+m, b+v, W+m, b+v,
		W+m, b+v ,W+m, b+v, W+m, b+v,  b+a+m, v, b+a+m, v,b+a+m, v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==17: # Pentagon

		alfa = 36 
		q = 1.0
		r = q*W/2
		x1 = W/2 + r*math.sin((alfa + 72)*math.pi/180)
		y1 = H/2 + r*math.cos((alfa + 72)*math.pi/180)
		x2 = W/2 + r*math.sin((alfa + 144)*math.pi/180)
		y2 = H/2 + r*math.cos((alfa + 144)*math.pi/180)
		x3 = W/2 + r*math.sin((alfa + 216)*math.pi/180)
		y3 = H/2 + r*math.cos((alfa + 216)*math.pi/180)
		x4 = W/2 + r*math.sin((alfa + 288)*math.pi/180)
		y4 = H/2 + r*math.cos((alfa + 288)*math.pi/180)
		x5 = W/2 + r*math.sin((alfa + 360)*math.pi/180)
		y5 = H/2 + r*math.cos((alfa + 360)*math.pi/180)
		new_vectors = pdb.gimp_vectors_new(image,"Pentagon")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 60,(
		x1+m,y1+v,x1+m,y1+v,x1+m,y1+v,  x2+m,y2+v,x2+m,y2+v,x2+m,y2+v,
		x2+m,y2+v,x2+m,y2+v,x2+m,y2+v,  x3+m,y3+v,x3+m,y3+v,x3+m,y3+v,
		x3+m,y3+v,x3+m,y3+v,x3+m,y3+v,  x4+m,y4+v,x4+m,y4+v,x4+m,y4+v,
		x4+m,y4+v,x4+m,y4+v,x4+m,y4+v,  x5+m,y5+v,x5+m,y5+v,x5+m,y5+v,
		x5+m,y5+v,x5+m,y5+v,x5+m,y5+v,  x1+m,y1+v,x1+m,y1+v,x1+m,y1+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==18: # Pentagram

		alfa = 36
		q = 1.0
		r = q*W/2
		x1 = W/2 + r*math.sin((alfa + 72)*math.pi/180)
		y1 = H/2 + r*math.cos((alfa + 72)*math.pi/180)
		x2 = W/2 + r*math.sin((alfa + 144)*math.pi/180)
		y2 = H/2 + r*math.cos((alfa + 144)*math.pi/180)
		x3 = W/2 + r*math.sin((alfa + 216)*math.pi/180)
		y3 = H/2 + r*math.cos((alfa + 216)*math.pi/180)
		x4 = W/2 + r*math.sin((alfa + 288)*math.pi/180)
		y4 = H/2 + r*math.cos((alfa + 288)*math.pi/180)
		x5 = W/2 + r*math.sin((alfa + 360)*math.pi/180)
		y5 = H/2 + r*math.cos((alfa + 360)*math.pi/180)
		new_vectors = pdb.gimp_vectors_new(image,"Pentagram")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 60,(
		x1+m,y1+v,x1+m,y1+v,x1+m,y1+v,  x3+m,y3+v,x3+m,y3+v,x3+m,y3+v,
		x3+m,y3+v,x3+m,y3+v,x3+m,y3+v,  x5+m,y5+v,x5+m,y5+v,x5+m,y5+v,
		x5+m,y5+v,x5+m,y5+v,x5+m,y5+v,  x2+m,y2+v,x2+m,y2+v,x2+m,y2+v,
		x2+m,y2+v,x2+m,y2+v,x2+m,y2+v,  x4+m,y4+v,x4+m,y4+v,x4+m,y4+v,
		x4+m,y4+v,x4+m,y4+v,x4+m,y4+v,  x1+m,y1+v,x1+m,y1+v,x1+m,y1+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==19: #  Petal (butterfly)
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, -W/2+m, v, W, H)
		pdb.gimp_image_select_ellipse(image, 3 ,m, -W/2+v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Petal_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Petal_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m, -W/2+v, W, H)
		pdb.gimp_image_select_ellipse(image, 3, W/2+m, v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Petal_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Petal_2")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, W/2+m, v, W, H)
		pdb.gimp_image_select_ellipse(image, 3, m, W/2+v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Petal_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Petal_3")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, -W/2+m, v, W, H)
		pdb.gimp_image_select_ellipse(image, 3, m, W/2+v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Petal_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Petal_4")
		pdb.gimp_selection_none(image)
		
	if s==20: # Pie 1/2 PKHG>5de creates 4 half circles 
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, W/2+m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/2_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/2_1")

		pdb.gimp_selection_none(image)
                gimp.message("m v W" +str(m) + " " + str(v) + " " + str(W))
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, m + W/2 , W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/2_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/2_2")		
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, m, H/2 + v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/2_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/2_3")
                
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, m,  v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/2_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/2_4")		
                
	if s==21: # Pie 3/4 - 1/4
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,1, W/2+m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_3/4_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_3/4_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, W/2+m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/4_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/4_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image, 1, m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_3/4_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_3/4_2")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image, 3, m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/4_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/4_2")		
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,1, m, W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_3/4_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_3/4_3")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, m, W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/4_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/4_3")		
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,1, W/2+m, W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_3/4_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_3/4_4")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, W/2+m, W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/4_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/4_4")
		pdb.gimp_selection_none(image)		
		
	if s==22: # Pie 7/8 - 1/8

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(W/2+m, v, W/2+m, W/2+v, W+m, v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(W/2+m, v, W/2+m, W/2+v, W+m, v))		
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_1")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(W+m, v, W/2+m, W/2+v, W+m, W/2+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_2")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(W+m, v, W/2+m, W/2+v, W+m, W/2+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_2")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(W+m, W+v, W/2+m, W/2+v, W+m, W/2+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_3")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(W+m, W+v, W/2+m, W/2+v, W+m, W/2+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_3")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(W+m, W+v, W/2+m, W/2+v, W/2+m, W+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_4")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(W+m, W+v, W/2+m, W/2+v, W/2+m, W+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_4")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(W/2+m, W/2+v, W/2+m, W+v, m, W+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_5")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_5")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(W/2+m, W/2+v, W/2+m, W+v, m, W+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_5")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_5")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(m, W/2+v, W/2+m, W/2+v, m, W+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_6")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_6")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(m, W/2+v, W/2+m, W/2+v, m, W+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_6")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_6")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(m, v, W/2+m, W/2+v, m, W/2+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_7")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_7")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(m, v, W/2+m, W/2+v, m, W/2+v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_7")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_7")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_polygon(image ,3 ,6 ,(W/2+m, v, W/2+m, W/2+v, m, v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_1/8_8")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_1/8_8")
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)		
		pdb.gimp_image_select_polygon(image ,1 ,6 ,(W/2+m, v, W/2+m, W/2+v, m, v))	
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Pie_7/8_8")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Pie_7/8_8")


	if s==23: # Playing cards Clubs

		new_vectors = pdb.gimp_vectors_new(image,"Clubs")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 54,
		(6*Wd8 +m,-5*W/64+v, 6*Wd8+m,2*Wd8+v, 6*Wd8+m,-5*W/64+v,
		2*Wd8+m,-5*W/64+v,  2*Wd8+m,2*Wd8+v, -5*W/64+m,2*Wd8+v,
		-5*W/64+m,6*Wd8+v,  2*Wd8+m,6*Wd8+v,  3*Wd8+m, 6*Wd8+v,
		7*W/16+m,11*W/16+v,  W/2+m-Wd8,5*Wd8+v,  W/2+m,7*Wd8+v,
		3*Wd8+m,W+v, Wd8+m,W+v, 3*Wd8+m,W+v,
		5*Wd8+m,W+v, 7*Wd8+m,W+v, 5*Wd8+m,W+v,
		W/2+m,7*Wd8+v, W/2+m+Wd8,5*Wd8+v, 9*W/16+m,11*W/16+v,
		5*Wd8+m,6*Wd8+v, 6*Wd8+m, 6*Wd8+v, 69*W/64+m,6*Wd8+v,
		 69*W/64+m,2*Wd8+v,  6*Wd8+m,2*Wd8+v,  6*Wd8+m,2*Wd8+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==24: # Playing cards Diamonds

		new_vectors = pdb.gimp_vectors_new(image,"Diamonds")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 30,
		( m+W/2,v+Wd8, m+W/2,v, m+W/2,v+Wd8,
		m+H/8,v+H/2, m,v+H/2, m+H/8,v+H/2, 
		m+W/2,v+7*Wd8, m+W/2,v+H, m+W/2,v+7*Wd8,
		m+7*H/8,v+H/2, m+H,v+H/2, m+7*H/8,v+H/2,
		m+W/2,v+Wd8, m+W/2,v, m+W/2,v+Wd8), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==25: # Playing cards Hearts

		new_vectors = pdb.gimp_vectors_new(image,"Hearts")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 30,
		( W/2+m,-W/10+v,  W/2+m,W/4+1+v,  W/2+m,-W/10+v,
		m, -W/16+v, m,W/4+v,  m,W/2+v,
		3*Wd8+m,5*Wd8+v,  W/2+m,W+v,  5*Wd8+m,5*Wd8+v,
		W+m, W/2+v, W+m,W/4+v,  W+m,-W/16+v,
		W/2+m,-W/10+v,  W/2+m,W/4+1+v,  W/2+m,-W/10+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==26: # Playing cards Spades

		new_vectors = pdb.gimp_vectors_new(image,"Spades")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 48,
		( 5*Wd8+m, 2*Wd8+v,  W/2+m,v,  3*Wd8+m, 2*Wd8+v,
		m,2*Wd8+v,  m,W/2+v,  m,6*Wd8+v,
		2*Wd8+m, 7*Wd8+v, W/2+m-W/100,5*Wd8+v,  W/2+m,7*Wd8+v,
		3*Wd8+m, W+v,  Wd8+m,W+v,  3*Wd8+m, W+v,
		5*Wd8+m, W+v,  7*Wd8+m,W+v,  5*Wd8+m, W+v,
		W/2+m, 7*Wd8+v, W/2+m+W/100,5*Wd8+v,  6*Wd8+m, 7*Wd8+v,
		W+m,6*Wd8+v,  W+m,W/2+v,  W+m,2*Wd8+v,
		5*Wd8+m, 2*Wd8+v,  W/2+m,v,  3*Wd8+m, 2*Wd8+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==27: # POLYGON

		sides=M_L            #Number=M->L
		rotation=R_L
		pdb.script_fu_polygon_path_ssc(image, layer, 'Polygon', W/2+m, H/2+v, W/2, sides, rotation, run_mode=RUN_NONINTERACTIVE)	
		
	if s==28: # Protractor Inside circle
# Start Protractor
#===================================================================================================================================================	
# Rel 1: Initial release.
# Rel 2: Draw marks as a single stroke for speed.
# Rel 3: Add option to draw marks inside circle or outside circle [download: http://bakon.ca/gimplearn/viewtopic.php?f=3&t=175#p512]
# Created by Tin Tran http://bakon.ca/gimplearn/  
# Comments directed to http://gimpchat.com or http://gimpscripts.com

		pdb.gimp_selection_none(image)
		if sel == False:
			x1 = m
			y1 = v
			x2 = W+m
			y2 = H+v
	
		W = float(abs(x2-x1))
		H = float(abs(y2-y1))
		radius = min(W,H)/2.0
		midx = x1 + (W/2.0)
		midy = y1 + (H/2.0)

		marklength = M_L
	
		vectors_name = "Protractor Marks"
		vectors = pdb.gimp_vectors_new(image,vectors_name)
		pdb.gimp_image_insert_vectors(image,vectors,None,-1)
	
		gimp.progress_init("Drawing Protractor Marks...")
		closed = 0
		mark_control_points = []
		for mark in range(0,361):
			gimp.progress_update(float(mark)/360)
			#Determine mark length
			mlength = float(marklength)/4 #regular marks are 1/4 of full mark length
			if mark % 5 == 0: #every 5 marks, make the mlength 1/2 of full mark length
				mlength = float(marklength)/2
			if mark % 10 == 0:
				mlength = marklength
			rad = (mark/360.0) * math.pi * 2
			# draw star in center
			if mark % 45 == 0:
			
				mx1 = midx 
				my1 = midy 
				mx2 = midx + (math.cos(rad) * (mlength))
				my2 = midy + (math.sin(rad) * (mlength))
			
				# draw mark to mark degree
				control_points = ([mx1,my1]*3) + ([mx2,my2]*3)
				pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		
			#horizontal rulers top and bottom
		
			mx1 = midx + (math.cos(rad) * radius)
			my1 = midy + (math.sin(rad) * radius)
			mradius = (radius - mlength)
			mx2 = midx + (math.cos(rad) * mradius)
			my2 = midy + (math.sin(rad) * mradius)
		
		# draw mark to mark degree
			mark_control_points = mark_control_points + ([mx1,my1]*3) + ([mx2,my2]*3) + ([mx1,my1]*3)
		pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(mark_control_points),mark_control_points,1)	
		pdb.gimp_item_set_visible(vectors,1)		
		#Draw Circle

	if s==29: # Protractor Outside circle

		pdb.gimp_selection_none(image)
		if sel == False:
			x1 = m
			y1 = v
			x2 = W+m
			y2 = H+v
	
		W = float(abs(x2-x1))
		H = float(abs(y2-y1))
		radius = min(W,H)/2.0
		midx = x1 + (W/2.0)
		midy = y1 + (H/2.0)

		marklength = M_L
	
		vectors_name = "Protractor Marks"
		vectors = pdb.gimp_vectors_new(image,vectors_name)
		pdb.gimp_image_insert_vectors(image,vectors,None,-1)
	
		gimp.progress_init("Drawing Protractor Marks...")
		closed = 0
		mark_control_points = []
		for mark in range(0,361):
			gimp.progress_update(float(mark)/360)
			#Determine mark length
			mlength = float(marklength)/4 #regular marks are 1/4 of full mark length
			if mark % 5 == 0: #every 5 marks, make the mlength 1/2 of full mark length
				mlength = float(marklength)/2
			if mark % 10 == 0:
				mlength = marklength
			rad = (mark/360.0) * math.pi * 2
			# draw star in center
			if mark % 45 == 0:
			
				mx1 = midx 
				my1 = midy 
				mx2 = midx + (math.cos(rad) * (mlength))
				my2 = midy + (math.sin(rad) * (mlength))
			
				# draw mark to mark degree
				control_points = ([mx1,my1]*3) + ([mx2,my2]*3)
				pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		
			#horizontal rulers top and bottom
		
			mx1 = midx + (math.cos(rad) * radius)
			my1 = midy + (math.sin(rad) * radius)
			mradius = (radius + mlength)
			mx2 = midx + (math.cos(rad) * mradius)
			my2 = midy + (math.sin(rad) * mradius)
		
		# draw mark to mark degree
			mark_control_points = mark_control_points + ([mx1,my1]*3) + ([mx2,my2]*3) + ([mx1,my1]*3)
		pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(mark_control_points),mark_control_points,1)	
		pdb.gimp_item_set_visible(vectors,1)		
		#Draw Circle
#End Protractor ===============================================================================================================================================
	if s==30: # Quadrant
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quadrant_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quadrant_1")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, W/2+m, v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quadrant_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quadrant_2")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,3, W/2+m, W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quadrant_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quadrant_3")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image, 3, m, W/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quadrant_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quadrant_4")
		pdb.gimp_selection_none(image)
		
	if s==31: # Quatrefoil

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, W/4+m ,v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 0, m ,W/4+v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 0, W/4+m ,W/2+v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 0, W/2+m ,W/4+v ,W/2 ,W/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quatrefoil-outside")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quatrefoil-outside")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, m, v, W/2, H)
		pdb.gimp_image_select_ellipse(image, 3, W/4+m ,v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 3, m ,W/4+v ,W/2 ,W/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quatrefoil-inside-1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quatrefoil-inside-1")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, m, v, W/2, H)
		pdb.gimp_image_select_ellipse(image, 3, m ,W/4+v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 3, W/4+ m ,W/2+v ,W/2 ,W/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quatrefoil-inside-2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quatrefoil-inside-2")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, W/2+m, v, W/2, H)
		pdb.gimp_image_select_ellipse(image, 3, W/4+m ,W/2+v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 3, W/2+ m ,W/4+v ,W/2 ,W/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quatrefoil-inside-3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quatrefoil-inside-3")
		pdb.gimp_selection_none(image)		
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, W/2+m, v, W/2, H)
		pdb.gimp_image_select_ellipse(image, 3, W/4+m ,v ,W/2 ,W/2)
		pdb.gimp_image_select_ellipse(image, 3, W/2+ m ,W/4+v ,W/2 ,W/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Quatrefoil-inside-4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Quatrefoil-inside-4")
		pdb.gimp_selection_none(image)
		
	if s==32: # Rectangle
		new_vectors = pdb.gimp_vectors_new(image,"Rectangle")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 30, 
		(j,k, j,k, j,k,    W1-j,k, W1-j,k ,W1-j,k,
		W1-j,H1-k, W1-j,H1-k, W1-j,H1-k,    j,H1-k, j,H1-k, j,H1-k,
		j,k, j,k, j,k), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==33: # Recycle two arrows

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, W/2 +m, v, W/2, W)
		pdb.gimp_image_select_ellipse(image, 3, m ,v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 1, W/4+m ,W/4+v ,W/2 ,W/2)
		pdb.gimp_image_select_polygon(image, 1, 10, (5*Wd8 + m, 5*Wd8 + v,  W/2 + m, 5*Wd8 + v,  W/2 +m, W+v, 6*Wd8 +m, W+v,  5*Wd8+m, 5*Wd8+v))
		pdb.gimp_image_select_polygon(image, 0, 8, (5*Wd8 + m, 5*Wd8 + v,  W/2 + m, 7*Wd8 + v,  6*Wd8 +m, W+v,  5*Wd8+m, 5*Wd8+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Recycle_D")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Recycle_D")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, m, v, W/2, W)
		pdb.gimp_image_select_ellipse(image, 3, m ,v ,W ,W)
		pdb.gimp_image_select_ellipse(image, 1, W/4+m ,W/4+v ,W/2 ,W/2)
		pdb.gimp_image_select_polygon(image, 1, 10, (W/4 + m,v, 3*Wd8+ m, 3*Wd8 + v,  W/2 +m, 3*Wd8+v, W/2 +m, v,  W/4 + m,v))
		pdb.gimp_image_select_polygon(image, 0, 8, (W/4 + m, v,  3*Wd8 + m, 3*Wd8 + v,  W/2 +m, Wd8+v,  W/4 + m, v,))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Recycle_C")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Recycle_C")
		pdb.gimp_selection_none(image)

	if s==34: # Recycle three arrows
		new_vectors = pdb.gimp_vectors_new(image,"Recycle_1")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		R1 = pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 84,(
		40*W/100+m, 39*W/100+v,40*W/100+m, 39*W/100+v,40*W/100+m, 39*W/100+v,      50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,
		50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,       55*W/100+m, 13*W/100+v,55*W/100+m, 13*W/100+v,55*W/100+m, 13*W/100+v,
		55*W/100+m, 13*W/100+v,55*W/100+m, 13*W/100+v,57*W/100+m, 10*W/100+v,       59*W/100+m, 10*W/100+v, 63*W/100+m, 10*W/100+v,63*W/100+m, 10*W/100+v,		
		63*W/100+m, 10*W/100+v,63*W/100+m, 10*W/100+v,66*W/100+m, 10*W/100+v,       36*W/100+m, 10*W/100+v,36*W/100+m, 10*W/100+v,36*W/100+m, 10*W/100+v,
		36*W/100+m, 10*W/100+v,36*W/100+m, 10*W/100+v,33*W/100+m, 10*W/100+v,       31*W/100+m, 11*W/100+v,30*W/100+m, 13*W/100+v,30*W/100+m, 13*W/100+v,
		30*W/100+m, 13*W/100+v,30*W/100+m, 13*W/100+v,30*W/100+m, 13*W/100+v,      21*W/100+m, 28*W/100+v,21*W/100+m, 28*W/100+v,21*W/100+m, 28*W/100+v,
		21*W/100+m, 28*W/100+v, 21*W/100+m, 28*W/100+v,21*W/100+m, 28*W/100+v,     40*W/100+m, 39*W/100+v,40*W/100+m, 39*W/100+v,40*W/100+m, 39*W/100+v,
		), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		pdb.gimp_image_get_active_vectors(image)
		x = pdb.gimp_vectors_copy(new_vectors)
		pdb.gimp_image_insert_vectors(image, x, None, -1)
		pdb.gimp_vectors_stroke_rotate(new_vectors, R1 ,W/2+m ,W/2+v ,-120)
	
		pdb.gimp_image_get_active_vectors(image)
		y = pdb.gimp_vectors_copy(x)
		pdb.gimp_image_insert_vectors(image, y, None, -1)
		pdb.gimp_vectors_stroke_rotate(y, R1 ,W/2+m ,W/2+v ,120)
		
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Recycle_2")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		R2 = pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 108,(
		50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,          55*W/100+m, 13*W/100+v,55*W/100+m, 13*W/100+v,55*W/100+m, 13*W/100+v,
		55*W/100+m, 13*W/100+v,55*W/100+m, 13*W/100+v,57*W/100+m, 10*W/100+v,          59*W/100+m, 10*W/100+v, 63*W/100+m, 10*W/100+v,63*W/100+m, 10*W/100+v,
		63*W/100+m, 10*W/100+v, 63*W/100+m, 10*W/100+v,66*W/100+m, 10*W/100+v,         68*W/100+m, 10*W/100+v, 70*W/100+m, 13*W/100+v, 70*W/100+m, 13*W/100+v,
		70*W/100+m, 13*W/100+v,70*W/100+m, 13*W/100+v,70*W/100+m, 13*W/100+v,          74*W/100+m, 20*W/100+v,74*W/100+m, 20*W/100+v,74*W/100+m, 20*W/100+v,
		74*W/100+m, 20*W/100+v,74*W/100+m, 20*W/100+v,74*W/100+m, 20*W/100+v,    79*W/100+m, 17*W/100+v,79*W/100+m, 17*W/100+v,79*W/100+m, 17*W/100+v,
		79*W/100+m, 17*W/100+v,79*W/100+m, 17*W/100+v,79*W/100+m, 17*W/100+v,          72*W/100+m, 41*W/100+v,72*W/100+m, 41*W/100+v,72*W/100+m, 41*W/100+v,
		72*W/100+m, 41*W/100+v,72*W/100+m, 41*W/100+v,72*W/100+m, 41*W/100+v,          48*W/100+m, 35*W/100+v,48*W/100+m, 35*W/100+v,48*W/100+m, 35*W/100+v,
		48*W/100+m, 35*W/100+v,48*W/100+m, 35*W/100+v,48*W/100+m, 35*W/100+v,          55*W/100+m, 31*W/100+v,55*W/100+m, 31*W/100+v,55*W/100+m, 31*W/100+v,
		55*W/100+m, 31*W/100+v,55*W/100+m, 31*W/100+v,55*W/100+m, 31*W/100+v,          50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v,50*W/100+m, 22*W/100+v
		), 0)
		
		pdb.gimp_item_set_visible(new_vectors, True)
		pdb.gimp_image_get_active_vectors(image)
		x = pdb.gimp_vectors_copy(new_vectors)
		pdb.gimp_image_insert_vectors(image, x, None, -1)
		pdb.gimp_vectors_stroke_rotate(new_vectors, R2 ,W/2+m ,W/2+v ,-120)
	
		pdb.gimp_image_get_active_vectors(image)
		y = pdb.gimp_vectors_copy(x)
		pdb.gimp_image_insert_vectors(image, y, None, -1)
		pdb.gimp_vectors_stroke_rotate(y, R2 ,W/2+m ,W/2+v ,120)
		pdb.gimp_item_set_visible(new_vectors, True)		
		
	if s==35: # Roses compass

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_polygon(image, 0, 8, (W/2+m,v,  3*Wd8+m,3*Wd8+v, W/2+m, W/2+v, W/2+m,v))
		pdb.gimp_image_select_polygon(image, 0, 8, (m, W/2+v, 3*Wd8+m, 5*Wd8+v, W/2+m, W/2+v, m, W/2+v))
		pdb.gimp_image_select_polygon(image, 0, 8, (W/2+m, W/2+v, W/2+m, W+v, 5*Wd8 +m, 5*Wd8 +v,W/2+m, W/2+v))
		pdb.gimp_image_select_polygon(image, 0, 8, (W/2+m, W/2+v, W+m, W/2+v, 5*Wd8 +m, 3*Wd8 +v, W/2+m, W/2+v))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Roses_L")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Róża wiatrów L")
		pdb.gimp_selection_none(image)
		
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_polygon(image, 0, 8, (W/2+m,v, W/2+m,W/2 +v, 5*Wd8+m,3*Wd8+v, W/2+m,v))
		pdb.gimp_image_select_polygon(image, 0, 8, (3*Wd8+m,3*Wd8+v, m, W/2+v, W/2+m, W/2+v, 3*Wd8+m,3*Wd8+v))
		pdb.gimp_image_select_polygon(image, 0, 8, (W/2+m, W/2+v, 3*Wd8+m,5*Wd8+v, W/2+m, W+v, W/2+m, W/2+v,))
		pdb.gimp_image_select_polygon(image, 0, 8, (W/2+m, W/2+v, 5*Wd8 +m, 5*Wd8 +v, W+m, W/2+v,  W/2+m, W/2+v,))
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Roses_R")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Róża wiatrów P")
		pdb.gimp_selection_none(image)
		
	if s==36: # Ruller
#===================================================================================================================================================
# Start "Draw_Percentage_Ruler Rel 1"
# Created by Tin Tran http://bakon.ca/gimplearn/
# Comments directed to http://gimpchat.com or http://gimpscripts.com

		pdb.gimp_selection_none(image)
	
		W = float(abs(x2-x1))
		H = float(abs(y2-y1))

		marklength = M_L
		vectors_name = "Percentage Ruler"
		vectors = pdb.gimp_vectors_new(image,vectors_name)
		pdb.gimp_image_insert_vectors(image,vectors,None,-1)
	
		gimp.progress_init("Drawing Percentage Rulers...")
		closed = 0
	
		for mark in range(0,101):
			gimp.progress_update(float(mark)/100)
			#Determine mark length
			mlength = float(marklength)/4 #regular marks are 1/4 of full mark length
			if mark % 5 == 0: #every 5 marks, make the mlength 1/2 of full mark length
				mlength = float(marklength)/2
			if mark % 10 == 0:
				mlength = marklength
			
			#horizontal rulers top and bottom
			mx1 = float(W)/100 * mark + x1
			mx2 = mx1
			my1 = y1
			my2 = y1 - mlength
			control_points = ([mx1,my1]*3) + ([mx2,my2]*3)
			pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		
			my1 = y2
			my2 = y2 + mlength
			control_points = ([mx1,my1]*3) + ([mx2,my2]*3)
			pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		
			#vertical marks
			mx1 = x1
			mx2 = x1 - mlength
			my1 = float(H)/100 * mark + y1
			my2 = my1
			control_points = ([mx1,my1]*3) + ([mx2,my2]*3)
			pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		
			mx1 = x2
			mx2 = x2 + mlength
			control_points = ([mx1,my1]*3) + ([mx2,my2]*3)
			pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		
		
			#here, we have control points all calculated depending on method, so we add the points
			pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)

		#Draw box 
		control_points = ([x1,y1]*3) + ([x2,y1]*3)
		pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		control_points = ([x2,y1]*3) + ([x2,y2]*3)
		pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		control_points = ([x1,y2]*3) + ([x2,y2]*3)
		pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		control_points = ([x1,y1]*3) + ([x1,y2]*3)
		pdb.gimp_vectors_stroke_new_from_points(vectors,VECTORS_STROKE_TYPE_BEZIER,len(control_points),control_points,closed)
		pdb.gimp_item_set_visible(vectors,1)
# End "Draw_Percentage_Ruler"
#===================================================================================================================================================
	if s==37: # Semicircle
	
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,1, W/2+m, v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Semicircle_1")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Semicircle_1")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image, 1, -W/2+m, v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Semicircle_2")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Semicircle_2")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,1, m, W/2+v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Semicircle_3")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Semicircle_3")

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, m ,v ,W ,W)
		pdb.gimp_image_select_rectangle(image,1, m, -W/2+v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Semicircle_4")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Semicircle_4")
		pdb.gimp_selection_none(image)

	if s==38: # Square
		new_vectors = pdb.gimp_vectors_new(image,"Square")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 30, 
		(m,v, m,v,m,v,  W+m,v, W+m,v ,W+m,v,
		W+m,W+v, W+m,W+v, W+m,W+v,  m,W+v, m,W+v, m,W+v,
		m,v, m,v,m,v,), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==39: # STAR
	
		oradius=(H_L)*W/200  #Outer Radius=H
		iradius=(V_L)*W/200  #Inner Radius=V
		points=M_L           #Number=M->L
		rotation=R_L
		pdb.script_fu_star_path_ssc(image, layer, 'Star', W/2+m, H/2+v, oradius, iradius, points, rotation, run_mode=RUN_NONINTERACTIVE)	
		
	if s==40: # Star pentagons

		alfa = 36
		q = 1.0
		r = q*W/2
		x1 = W/2 + r*math.sin((alfa + 72)*math.pi/180)
		y1 = H/2 + r*math.cos((alfa + 72)*math.pi/180)
		x2 = W/2 + r*math.sin((alfa + 144)*math.pi/180)
		y2 = H/2 + r*math.cos((alfa + 144)*math.pi/180)
		x3 = W/2 + r*math.sin((alfa + 216)*math.pi/180)
		y3 = H/2 + r*math.cos((alfa + 216)*math.pi/180)
		x4 = W/2 + r*math.sin((alfa + 288)*math.pi/180)
		y4 = H/2 + r*math.cos((alfa + 288)*math.pi/180)
		x5 = W/2 + r*math.sin((alfa + 360)*math.pi/180)
		y5 = H/2 + r*math.cos((alfa + 360)*math.pi/180)
		alfa = 0  # 18 36 54
		q = 0.5*(3-math.sqrt(5))
		r = q*W/2
		xm1 = W/2 + r*math.sin((alfa + 72)*math.pi/180)
		ym1 = H/2 + r*math.cos((alfa + 72)*math.pi/180)
		xm2 = W/2 + r*math.sin((alfa + 144)*math.pi/180)
		ym2 = H/2 + r*math.cos((alfa + 144)*math.pi/180)
		xm3 = W/2 + r*math.sin((alfa + 216)*math.pi/180)
		ym3 = H/2 + r*math.cos((alfa + 216)*math.pi/180)
		xm4 = W/2 + r*math.sin((alfa + 288)*math.pi/180)
		ym4 = H/2 + r*math.cos((alfa + 288)*math.pi/180)
		xm5 = W/2 + r*math.sin((alfa + 360)*math.pi/180)
		ym5 = H/2 + r*math.cos((alfa + 360)*math.pi/180)
		
		new_vectors = pdb.gimp_vectors_new(image,"Star pentagons")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 120,(
		x1+m,y1+v,x1+m,y1+v,x1+m,y1+v,  xm1+m,ym1+v,xm1+m,ym1+v,xm1+m,ym1+v,
		xm1+m,ym1+v,xm1+m,ym1+v,xm1+m,ym1+v,  x5+m,y5+v,x5+m,y5+v,x5+m,y5+v,
		x5+m,y5+v,x5+m,y5+v,x5+m,y5+v,  xm5+m,ym5+v,xm5+m,ym5+v,xm5+m,ym5+v,
		xm5+m,ym5+v,xm5+m,ym5+v,xm5+m,ym5+v,  x4+m,y4+v,x4+m,y4+v,x4+m,y4+v,
		x4+m,y4+v,x4+m,y4+v,x4+m,y4+v,  xm4+m,ym4+v,xm4+m,ym4+v,xm4+m,ym4+v,
		xm4+m,ym4+v,xm4+m,ym4+v,xm4+m,ym4+v,  x3+m,y3+v,x3+m,y3+v,x3+m,y3+v,
		x3+m,y3+v,x3+m,y3+v,x3+m,y3+v,  xm3+m,ym3+v,xm3+m,ym3+v,xm3+m,ym3+v,
		xm3+m,ym3+v,xm3+m,ym3+v,xm3+m,ym3+v,  x2+m,y2+v,x2+m,y2+v,x2+m,y2+v,
		x2+m,y2+v,x2+m,y2+v,x2+m,y2+v,  xm2+m,ym2+v,xm2+m,ym2+v,xm2+m,ym2+v,
		xm2+m,ym2+v,xm2+m,ym2+v,xm2+m,ym2+v,  x1+m,y1+v,x1+m,y1+v,x1+m,y1+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==41: # Triangle equilateral
		d = 3*W/4
		e = d/math.sqrt(3)

		new_vectors = pdb.gimp_vectors_new(image,"Triangle equilateral")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
                res = 	(W/2+m,v, W/2+m,v, W/2+m,v,
                         W/2 + e+m,d+v,  W/2 + e+m,d+v, W/2 + e+m,d+v,
		         W/2-e+m, d+v, W/2-e+m, d+v, W/2-e+m, d+v,
                         W/2+m, v, W/2+m, v, W/2+m, v,
                         W/2+m, v, W/2+m, v, W/2+m, v,
                         W/2+m, v, W/2+m, v, W/2+m, v,
                         )
                pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 36, res,0 )
                """ 
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 36, 
		(W/2+m,v, W/2+m,v, W/2+m,v,  W/2 + e+m,d+v,  W/2 + e+m,d+v, W/2 + e+m,d+v,
		W/2 +e+m, d+v, W/2 +e+m, d+v, W/2 +e+m, d+v, W/2 -e+m, d+v, W/2 -e+m, d+v, W/2- e+m, d+v,
		W/2-e+m, d+v, W/2-e+m, d+v, W/2-e+m, d+v,   W/2+m, v, W/2+m, v, W/2+m, v ), 0)
                """
		pdb.gimp_item_set_visible(new_vectors, True)

	if s==42: # Triangle isosceles
		new_vectors = pdb.gimp_vectors_new(image,"Triangle isosceles")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 24, 
		(W1/2,k, W1/2,k, W1/2,k,  W1-j,H1-k, W1-j,H1-k ,W1-j,H1-k,  j, H1-k, j,H1-k, j, H1-k,  W1/2,k, W1/2,k, W1/2,k), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
	if s==43: # "Triangle Reuleaux"
	
		R = W - math.sqrt(3)*W/2
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, -W/2+m ,-W+v ,2*W ,2*W)
		pdb.gimp_image_select_ellipse(image, 3, -W+m ,-R+v ,2*W ,2*W)
		pdb.gimp_image_select_ellipse(image, 3, m ,-R+v ,2*W ,2*W)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Triangle Reuleaux")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Triangle Reuleaux")
		pdb.gimp_selection_none(image)
		
	if s==44: # Trefoil

		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, 3*W/16+m ,v ,5*Wd8 ,5*Wd8)
		pdb.gimp_image_select_ellipse(image, 0, m ,3*Wd8+v ,5*Wd8 ,5*Wd8)
		pdb.gimp_image_select_ellipse(image, 0, 3*Wd8+m ,3*Wd8+v ,5*Wd8 ,5*Wd8)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Trefoil")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Trefoil")
		pdb.gimp_selection_none(image)

	if s==45: # Yin-Yang
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_rectangle(image,0, m, v, W/2, H)
		pdb.gimp_image_select_ellipse(image, 3 ,m, v, W, H)
		pdb.gimp_image_select_ellipse(image, 0, W/2-W/4+m, v, W/2, H/2)
		pdb.gimp_image_select_ellipse(image, 1, W/2-W/4+m, H/2+v, W/2, H/2)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Yang")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Yang")
		pdb.gimp_selection_invert(image)
		pdb.gimp_image_select_ellipse(image,3, m, v, W, H)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		pdb.gimp_selection_none(image)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Yin")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Yin")
		pdb.gimp_image_select_ellipse(image, 0, 7*W/16+m, 3*W/16+v, Wd8, H/8)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Eye Yang")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Oko Yang")
		pdb.gimp_selection_none(image)
		pdb.gimp_image_select_ellipse(image, 0, 7*W/16+m, 11*W/16+v, Wd8, H/8)
		pdb.plug_in_sel2path(image, layer, run_mode=RUN_NONINTERACTIVE)
		active_vectors = pdb.gimp_image_get_active_vectors(image)
		active_vectors.visible = True
		active_vectors.name = active_vectors.name.replace("Selection", "Eye Yin")
		active_vectors.name = active_vectors.name.replace("Zaznaczenie", "Oko Yin")
		pdb.gimp_selection_none(image)

	if s==46: # Wilber

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-01-head outline")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
                Wd100 = W / 100
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 156,(
		25*Wd100+m, 30*Wd100+v, 30*Wd100+m, 40*Wd100+v, 30*Wd100+m, 40*Wd100+v,     18*Wd100+m, 11*Wd100+v, 24*Wd100+m, 18*Wd100+v, 27*Wd100+m, 21*Wd100+v,
		24*Wd100+m, 18*Wd100+v, 24*Wd100+m, 18*Wd100+v, 27*Wd100+m, 21*Wd100+v,     35*Wd100+m, 31*Wd100+v, 44*Wd100+m, 35*Wd100+v, 44*Wd100+m, 35*Wd100+v,
		44*Wd100+m, 35*Wd100+v, 44*Wd100+m, 35*Wd100+v, 54*Wd100+m, 39*Wd100+v,     60*Wd100+m, 39*Wd100+v, 69*Wd100+m, 36*Wd100+v, 69*Wd100+m, 36*Wd100+v,
		69*Wd100+m, 36*Wd100+v, 69*Wd100+m, 36*W/100+v, 78*Wd100+m, 33*Wd100+v,     90*Wd100+m, 25*Wd100+v, 95*Wd100+m, 13*Wd100+v, 95*Wd100+m, 13*Wd100+v,
		95*Wd100+m, 13*Wd100+v, 95*Wd100+m, 13*Wd100+v, 96*Wd100+m, 10*Wd100+v,     98*Wd100+m, 18*Wd100+v, 97*Wd100+m, 29*Wd100+v, 97*Wd100+m, 29*Wd100+v,
		97*Wd100+m, 29*Wd100+v, 97*Wd100+m, 29*Wd100+v, 96*Wd100+m, 40*Wd100+v,     90*Wd100+m, 46*Wd100+v, 81*Wd100+m, 52*Wd100+v, 81*Wd100+m, 52*Wd100+v,
		81*Wd100+m, 52*Wd100+v, 81*Wd100+m, 52*Wd100+v, 79*Wd100+m, 65*Wd100+v,     69*Wd100+m, 75*Wd100+v,  54*Wd100+m, 76*Wd100+v,  54*Wd100+m, 76*Wd100+v,
		54*Wd100+m, 76*Wd100+v, 54*Wd100+m, 76*Wd100+v, 60*Wd100+m, 73*Wd100+v,     62*Wd100+m, 70*Wd100+v, 63*Wd100+m, 67*Wd100+v,  63*Wd100+m, 67*Wd100+v,
		63*Wd100+m, 67*Wd100+v, 63*Wd100+m, 67*Wd100+v,  64*Wd100+m, 63*Wd100+v,    63*Wd100+m, 62*Wd100+v,  61*Wd100+m, 60*Wd100+v,  61*Wd100+m, 60*Wd100+v,
		61*Wd100+m, 60*Wd100+v,  61*Wd100+m, 60*Wd100+v,  58*Wd100+m, 69*Wd100+v,   37*Wd100+m, 74*Wd100+v,  27*Wd100+m, 72*Wd100+v, 27*Wd100+m, 72*Wd100+v,
		27*Wd100+m, 72*Wd100+v, 27*Wd100+m, 72*Wd100+v, 24*Wd100+m, 72*Wd100+v,     18*Wd100+m, 70*Wd100+v, 18*Wd100+m, 70*Wd100+v, 18*Wd100+m, 70*Wd100+v,
		18*Wd100+m, 70*Wd100+v, 18*Wd100+m, 70*Wd100+v, 26*Wd100+m, 66*Wd100+v,     26.5*Wd100+m, 57*Wd100+v, 21*Wd100+m, 49*Wd100+v, 21*Wd100+m, 49*Wd100+v,
		21*Wd100+m, 49*Wd100+v, 21*Wd100+m, 49*Wd100+v, 21*Wd100+m, 49*Wd100+v,     23*Wd100+m, 47*Wd100+v, 23*Wd100+m, 47*Wd100+v, 23*Wd100+m, 47*Wd100+v		), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-02-left eye")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,30*Wd100+m ,47*Wd100+v ,7*Wd100 ,7*Wd100, 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Wilber-03-left eye pupil")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,31*Wd100+m ,49*Wd100+v ,4*Wd100 ,4*Wd100, 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Wilber-04-left eye pupil highlight")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,30*Wd100+m ,48*Wd100+v ,2*Wd100 ,2*Wd100, 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		
		new_vectors = pdb.gimp_vectors_new(image,"Wilber-05-mouth")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 48,(
		54*Wd100+m, 76*Wd100+v, 54*Wd100+m, 76*Wd100+v, 60*Wd100+m, 73*Wd100+v,     62*Wd100+m, 70*Wd100+v, 63*Wd100+m, 67*Wd100+v,  63*Wd100+m, 67*Wd100+v,
		63*Wd100+m, 67*Wd100+v, 63*Wd100+m, 67*Wd100+v,  64*Wd100+m, 63*Wd100+v,    63*Wd100+m, 62*Wd100+v,  61*Wd100+m, 60*Wd100+v,  61*Wd100+m, 60*Wd100+v,
		61*Wd100+m, 60*Wd100+v,  61*Wd100+m, 60*Wd100+v,  58*Wd100+m, 69*Wd100+v,   38*Wd100+m, 74*Wd100+v, 27*Wd100+m, 72*Wd100+v, 27*Wd100+m, 72*Wd100+v,
		27*Wd100+m, 72*Wd100+v,  27*Wd100+m, 72*Wd100+v, 34*Wd100+m, 75*Wd100+v,    46*Wd100+m, 78*Wd100+v, 54*Wd100+m, 76*Wd100+v, 60*Wd100+m, 73*Wd100+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-06-nose")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 48,(
		4*Wd100+m, 46*Wd100+v, 10*Wd100+m, 44*Wd100+v, 16*Wd100+m, 43*Wd100+v,       21*Wd100+m, 47*Wd100+v, 24*Wd100+m, 55*Wd100+v, 24*Wd100+m, 55*Wd100+v,
		24*Wd100+m, 55*Wd100+v, 24*Wd100+m, 55*Wd100+v, 26*Wd100+m, 62*Wd100+v,   	 23*Wd100+m, 68*Wd100+v, 18*Wd100+m, 70*Wd100+v, 18*Wd100+m, 70*Wd100+v,
		18*Wd100+m, 70*Wd100+v,18*Wd100+m, 70*Wd100+v, 12*Wd100+m, 71*Wd100+v,       6*Wd100+m,67*Wd100+v, 4*Wd100+m,60*Wd100+v,  4*Wd100+m, 60*Wd100+v,
		4*Wd100+m,60*Wd100+v,4*Wd100+m,60*Wd100+v, Wd100+m, 52*Wd100+v,   4*Wd100+m, 46*Wd100+v,  10*Wd100+m, 44*Wd100+v,  17*Wd100+m, 43*Wd100+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)		
		
		new_vectors = pdb.gimp_vectors_new(image,"Wilber-07-nose highlight")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,11*Wd100+m ,51*Wd100+v ,4*Wd100 ,5*Wd100, 15)
		pdb.gimp_item_set_visible(new_vectors, True)		

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-08-right eye")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,47*Wd100+m ,48*Wd100+v ,10*Wd100 ,10*Wd100, 0)
		pdb.gimp_item_set_visible(new_vectors, True)

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-09-right eye pupil")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,49*Wd100+m ,51*Wd100+v ,5*Wd100 ,5*Wd100, 0)
		pdb.gimp_item_set_visible(new_vectors, True)

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-10-right eye pupil highlight")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_bezier_stroke_new_ellipse(new_vectors ,48*Wd100+m ,50*Wd100+v ,2*Wd100 ,2*Wd100, 0)
		pdb.gimp_item_set_visible(new_vectors, True)

		new_vectors = pdb.gimp_vectors_new(image,"Wilber-11-shadow")
		pdb.gimp_image_insert_vectors(image, new_vectors, None, -1)
		pdb.gimp_vectors_stroke_new_from_points(new_vectors, 0, 60,(
		95*Wd100+m, 13*Wd100+v, 95*Wd100+m, 13*Wd100+v, 96*Wd100+m, 10*Wd100+v,   98*Wd100+m, 18*Wd100+v, 97*Wd100+m, 29*Wd100+v, 97*Wd100+m, 29*Wd100+v,
		97*Wd100+m, 29*Wd100+v, 97*Wd100+m, 29*Wd100+v, 96*Wd100+m, 40*Wd100+v,   90*Wd100+m, 46*Wd100+v, 81*Wd100+m, 52*Wd100+v, 81*Wd100+m, 52*Wd100+v,
		81*Wd100+m, 52*Wd100+v, 81*Wd100+m, 52*Wd100+v, 79*Wd100+m, 65*Wd100+v,   69*Wd100+m, 75*Wd100+v,  54*Wd100+m, 76*Wd100+v,  54*Wd100+m, 76*Wd100+v,
		54*Wd100+m, 76*Wd100+v, 54*Wd100+m, 76*Wd100+v, 67*Wd100+m, 76*Wd100+v,   79*Wd100+m, 63*Wd100+v,77*Wd100+m, 49*Wd100+v,77*Wd100+m, 49*Wd100+v,
		77*Wd100+m, 49*Wd100+v,77*Wd100+m, 49*Wd100+v,95*Wd100+m, 41*Wd100+v,     95*Wd100+m, 13*Wd100+v, 95*Wd100+m, 13*Wd100+v, 96*Wd100+m, 10*Wd100+v), 0)
		pdb.gimp_item_set_visible(new_vectors, True)
		


	if R_1:
		pdb.script_fu_resize_image_to_layers_by_the_edge(image, layer, R, L, T, B, R_2, run_mode=RUN_NONINTERACTIVE)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ by Tin Tran

	# See which vectors are added as new vectors, it's new if it's not in our before_vectors list, we'll add it to our new_vectors list
	pdb.gimp_selection_none(image)
	new_vectors = []
	for vectors in image.vectors:
		if vectors not in before_vectors:
			new_vectors.append(vectors)

	#Loop through each new added vectors
	if fill==1:
		W = pdb.gimp_image_width(image)  #szer
		H = pdb.gimp_image_height(image)
		for vectors in new_vectors:
	
		#Select the vectors, this is like front end's "Path To Selection"
			pdb.gimp_image_select_item(image,CHANNEL_OP_REPLACE,vectors)
			fill_layer = gimp.Layer(image, "Fill Layer", W, H, RGBA_IMAGE, 100, NORMAL_MODE)
			image.add_layer(fill_layer, -1)
		#Set context pattern and fill selection with pattern fill

			pdb.gimp_context_set_pattern(fillpattern)
			pdb.gimp_edit_fill(fill_layer,PATTERN_FILL)    #GIMP 2.8
			#pdb.gimp_edit_fill(fill_layer,FILL_PATTERN)	  #GIMP 2.9

		# Now we select None so that Stroke path call later will stroke the whole path and not just selected area
			pdb.gimp_selection_none(image)
	    # Stroke path using SVG method.
	if fill==2:
		W = pdb.gimp_image_width(image)  #szer
		H = pdb.gimp_image_height(image)

		for vectors in new_vectors:
	
		#Select the vectors, this is like front end's "Path To Selection"
			pdb.gimp_image_select_item(image,CHANNEL_OP_REPLACE,vectors)
			brush_layer = gimp.Layer(image, "Brush Layer", W, H, RGBA_IMAGE, 100, NORMAL_MODE)
			image.add_layer(brush_layer, -1)
			selection = pdb.gimp_selection_bounds(image);
			
			x1 = selection[1];
			y1 = selection[2];
			x2 = selection[3];
			y2 = selection[4];
			width = W1
			height = H1
			horizontalspacing = H_L
			verticalspacing = V_L
			context_brush_size = pdb.gimp_context_get_brush_size()
			bwidth = context_brush_size * (horizontalspacing/100.0)
			bheight = context_brush_size * (verticalspacing/100.0)
			gimp.progress_init("Filling Selection with Active Brush...")
			
			for x in range(0,int(W1/bwidth)+1):
				gimp.progress_update(x*1.0/(int(W1/bwidth)+1))
				for y in range(0,int(H1/bheight)+1):
					ix = x1 + (x * bwidth)
					iy = y1 + (y * bheight)
					if pdb.gimp_selection_value(image,ix,iy) > 0:
						#pdb.gimp_airbrush(layer,100,2,(ix,iy))
						pdb.gimp_paintbrush(brush_layer,0,2,(ix,iy),PAINT_CONSTANT,0)		
	if stroke:
		for vectors in new_vectors:
			W = pdb.gimp_image_width(image)  #szer
			H = pdb.gimp_image_height(image)
			stroke = gimp.Layer(image, "Stroke Layer", W, H, RGBA_IMAGE, 100, NORMAL_MODE)
			image.add_layer(stroke, -1)
			vector_to_line_stroke(image,vectors,stroke,color_to_hex(strokecolor),strokewidth,"square","bevel",10,"auto")
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	if sel == True:	
		pdb.gimp_image_select_item(image,CHANNEL_OP_REPLACE,temp)
	pdb.gimp_image_undo_group_end(image)
	pdb.gimp_displays_flush()

register(
        "plugin_simple_shapes_centered",
        "Simple paths shapes centered in the image or selection Ver - 1.0.\n===========================================\nYou can also add a margin on each side (resize the layer and not the path).This option requires script Changing Image Border.scm.\n------------------------------------------------------------------------------\nThanks to Tin Tran, Ofnuts, TheUncle2k,Fencepost and J.Stipe.\n",
        "Simple path shapes centered in the image v.1.0",
        "MrQ",
        "GPL",
        "2016",
        "<Image>/Filters/Path/Simple shapes centered...",
        "RGB*, GRAY*",
        [
		#(PF_IMAGE, "image", "Input image", None),
		#(PF_VECTORS, "drawable", "Input drawable", None),
		(PF_BOOL, "sel", ("In selection? "), False),
		(PF_OPTION, "s", "Shape:", 43, 
		[
		 "Arrow [Paths:4]",																#0
		 "Axis of symmetry",															#1
		 "Binoculars [Paths:1+4]\nM->L = [Outer radius - Inner radius](pix)",			#2
		 "Circle",																		#3
		 "Crescent",																	#4
		 "Cross",																		#5
		 "Diagonals",																	#6
		 "Diamond",																		#7
		 "Dodecagon",																	#8
		 "Ellipse",																		#9
		 "Flower Out [Paths:6]", 														#10
		 "Flower In [Paths:6]", 														#11
		 "GEAR \nM->L = Number of teeth (min.3)    R = Rotation\nH = Outer Radius(%)           V = Inner Radius(%)",	#12
		 "Grid rectangular (c) Ofnuts \nH = Horizontal lines\nV = Vertical lines",		#13
		 "Hexagon",																		#14
		 "Mobius band [Paths:3+1]",														#15
		 "Octagon",																		#16
		 "Pentagon",																	#17
		 "Pentagram",																	#18
		 "Petals [Paths:4]",															#19
		 "Pie 1/2 [Paths:4]",															#20
		 "Pie 1/4 [Paths:4+4]",        													#21
		 "Pie 1/8 [Paths:8+8]",        													#22
		 "Playing cards: Clusb",														#23
		 "Playing cards: Diamonds",														#24
		 "Playing cards: Hearts",														#25
		 "Playing cards: Spades",														#26
		 "POLYGON \nM->L = Sides (min.3)  R = Rotation",								#27
		 "Protractor in circle (c) Tin Tran \nM->L = Mark Length (pix)",  				#28
		 "Protractor out circle (c) Tin Tran \nM->L = Mark Length (pix)", 				#29
		 "Quadrant [Paths:4]",															#30
		 "Quatrefoil [Paths:1+4]",														#31
		 "Rectangle",																	#32
		 "Recycle (two arrows) [Paths:2]",												#33
		 "Recycle (three arrows) [Paths:3+3]",   										#34
		 "Roses compass 4-point [Paths:2]",      										#35
		 "Ruler (c) Tin Tran \nM->L = Mark Length (pix)",								#36
		 "Semicircle [Paths:4]", 														#37
		 "Square",																		#38
		 "STAR\nM->L = Number of points (min.3)    R = Rotation\nH = Outer Radius(%)           V = Inner Radius(%)",#39
		 "Star pentagons",																#40
		 "Triangle equilateral",														#41
		 "Triangle isosceles", 															#42
		 "Triangle Reuleaux (curvilinear)", 											#43
		 "Trefoil",																		#44
		 "Yin-Yang [Paths:4]",															#45
		 "WILBER [Paths:11]",															#46
		]),
		(PF_BOOL, "resize_1", ("Resize layer? "), False),
		(PF_SPINNER, "R", "Resize on the Right (pix)", 10, (-10000, 10000, 1)),
		(PF_SPINNER	, "L", "Resize on the Left (pix)", 10, (-10000, 10000, 1)),
		(PF_SPINNER, "T", "Resize from Top (pix)", 10, (-10000, 10000, 1)),
		(PF_SPINNER, "B", "Resize from Bottom (pix)", 10, (-10000, 10000, 1)),
		(PF_BOOL, "resize_2", ("Resize all layers to image size? "), False),
		(PF_SPINNER, "M_L", "'M->L' Mark Length (pix)", 10, (1, 1000, 1)),
		(PF_SPINNER, "H_L", "'H' Horizontal\n[ % for fill brush]", 10, (1, 100, 1)),
		(PF_SPINNER, "V_L", "'V' Vertical\n[% for fill brush]", 10, (1, 100, 1)),
		(PF_SPINNER, "R_L", "'R' Rotation (angle)", 0, (0, 360, 1)),
		(PF_OPTION, "fill", "Fill ?:", 0, ["No fill", "Fill pattern (path to selection)", "Fills Selection with Active Brush [H,V = percentage]"]),
		#(PF_BOOL, "fill", ("Fill (path to selection)? "), False),
		(PF_PATTERN, "fillpattern", "Fill Pattern:", 0),
		(PF_BOOL, "stroke", ("Stroke path (using SVG method) ? "), False),
		(PF_COLOR, "strokecolor",  "Stroke Color:",  (0,0,0)),
		(PF_SPINNER, "strokewidth", "Stroke Line Width (pix)", 6, (1, 200, 1))
		],
		[],
		plugin_simple_shapes_centered)

main()
