
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# original from Arakne guide-lab   (
# version 1.1 with guides to path plugin added PKHG
# This is the Arakne guide-lab extended
# Extra: create a path along available guides or only inside a selected region;
# and stroke the the just created path (active vectors) with an option to remove this active vectors,
# where the foreground colour and selected pen is used.
# This is/was my gtk-plugin learning code, therefore a third tab may be looked at, will be adjusted
# Version 1.5 29 october 2016
# New message if intersections needed, but not (yet) available.
# Minor error in nb = number of selections to create ...
# Plan: add strange fill-ins for selections: TODO
# for Simple path shapes :
# http://gimpchat.com/viewtopic.php?f=9&t=14742&sid=733a9bcfdd54a151c195b79b652dca63
#clearer program 8nov2016 1647
#version 2.0 9nov2016=1448
#version 2.01 Simple path made free of 'Clipboard' and random made possible
#Version 2.02 direct choice of random simple shape and/ or there fill pattern random
#Version 2.03 no global debu no_debug_output set to True 13 nov 1646 hours
#gid 17-11-2016 https://github.com/PKHG/guidelab_paint.git
#Version 3.0 new layout guidelab on page 0 , help, paint op page 2
#Version 3.1 random shape fill working 27nov 1645 (PKHG local git!)
#Version 3.2 random pattern fille working 27 nov 1711 (PKHG local git!)
#version 3.2 repaired from error 27 nov 1711
#version 3.2 seems ok 29 nov 1148
#version 3.3 small name adjustments *_tab use rotated list of items 30 Nov TODO
#layout for shapes adjusted patterns now in ONE line ...
#1dec2016 cyclic use of simple shapes TODO 1204 1231 works OK
#2dec warning if no choice of shapes is done and cyclic use is activated
#version 3.4 rowwise or columwise paint shapes done 
#version 3.5 4dec16:1134 no intersections shapes like original working done

from collections import deque  #has a built in rotate d =deque(a_list) d.rotate(1), d has no slice

import gimp
import gimpplugin
from gimpenums import *
pdb = gimp.pdb
import gobject
import gtk
import gimpui
import _gimpui
import os
import sys

debug_output = False

sys.path.append(gimp.directory + "\\python_gtk")
print(sys.path[-1])
from time import time
from random import random
from random import randint
#global???!!!
pattern_available = False

def random_rgb():
    return(randint(0,255), randint(0,255), randint(0,255))
    ##return( (int(random() * 256), int(random() * 256), int(random() * 256)))

##########drawUi.py start
def newline(x1,y1,x2,y2):
    return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2]

def kreiseEllipse(image, mx, my, w, h, operation= 0, chosen_form = 'ellipse'):
    debug(("L65 kreiseEllipse called",mx,my,w,h,operation,chosen_form),1 )
    x = mx - w / 2
    y = my - h / 2
    if chosen_form == 'ellipse':
        pdb.gimp_image_select_ellipse(image, operation, x, y, w, h)
    else:
        pdb.gimp_image_select_rectangle(image, operation, x, y, w, h)
        

class drawUi(object):
    def __init__(self):
        self.ttips = gtk.Tooltips()
        pass

    def addTip(self, obj, tip):
        self.ttips.set_tip(obj,tip)
    
    def addRows(self, obj, table, col1,col2, row1,row2,cnn="",function=None):
        #gimp.message(" addRows   (%1d : %1d)  (%1d : %1d) " %(col1, row1, col2, row2))
        table.attach(obj, col1, col2, row1, row2)
        obj.show()
        if cnn!="": obj.connect(cnn, function)
        return obj

    def addProps(self,obj,props):
        for Key,Value in props:
            obj.set_property(Key, Value)

    def addLabel(self,tx,alignx=1.0,aligny=0.5):
        lb = gtk.Label(tx)
        lb.set_alignment(alignx,aligny)
        return lb
    
    def addButton(self, name="testbutton"):
        btn = gtk.Button(name)
        self.button_value = name
        return btn
    
    def fillCombo(self, Store, combobox):
        st = combobox.get_model()
        st.clear()
        for n in Store: st.append(n)
        combobox.set_model(st)
        combobox.set_active(0)
    
    def fillCombo2(self, Store, combobox):
        st = combobox.get_model()
        st.clear()
        #PKHG>DBG gimp.message(str(Store))
        #self.show_my_message(str(Store))
        for n in Store: st.append([Store[n]['tit'],n])
        combobox.set_model(st)
        combobox.set_active(0)
    
    def makeCombo(self, Store):
        st = gtk.ListStore(str, int)
        self.cmb = gtk.ComboBox(st)
        cell = gtk.CellRendererText()
        self.fillCombo(Store,self.cmb)
        self.cmb.pack_start(cell, True)
        self.cmb.add_attribute(cell, 'text', 0)
        self.cmb.set_active(0)
        return self.cmb
    
    def makeCombo2(self, Store):
        st = gtk.ListStore(str, str,)
        self.cmb = gtk.ComboBox(st)
        cell = gtk.CellRendererText()
        self.fillCombo2(Store,self.cmb)
        self.cmb.pack_start(cell, True)
        self.cmb.add_attribute(cell, 'text', 0)
        self.cmb.set_active(0)
        return self.cmb
    
    def getValues(self,arrFields):
        return (n.get_value() for n in arrFields)
    
    def getModelVal(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()
        lP = model.get_value(iter,1)
        return lP
##########drawUi.py end

def debug(val, urgent = 0 ):
    global debug_output
    #gimp.message(" debug called")
    if urgent > 0 :
        gimp.message(str(val))
    if not debug_output :
        return
    gimp.message(str(val))

def debugErr(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    debug(fname+'\n'+str(exc_tb.tb_lineno)+'\n'+str(e), urgent = 1)

#Globals???!!
horizontal_guides = []
vertical_guides = []

class Guidelabextra(object):
    """
    A combination of Araknes guide-lab 
    and guide-to_path with stroke possibility
    """
    titDel=("Delete")
    newG=("Add new")
    tabs=[]
    yes_no = False
    useRow = 10
    ui = drawUi()
    #PKHG>???TODO patterSector = PatternSelector()
    #tabTits = [('Add/Edit'),('Help guide lab'),('Help guides_to_path'),('Simple Path centured')] #PKHG help added
    tabTits = [('Add/Edit'),('Help texts'),('Paint stuff'),('Simple Path centured'),('select several ...')] #PKHG help added
    tipPos = ("Position of the current guide, double click on the value to edit")
    tipPrev = ("Distance between this guide and the previous. If this guide is the 1st then this will be the distance to the start of the image.")
    tipNext=("Distance between this guide and the next. If this guide is the last then this will be distance to the end of the image.")
    tipDel=("Double click to delete the current guide.")
    newGuideTip=("Write the position for the new guide\nLook what operations and replacements you can use in the help tab")
    
    def __init__(self, runmode, img):
        self.img = img
        self.image_start_name = img.name
        debug(("L190 __init__ called", self.image_start_name))  
        #self_starting_img = self.img
        #debug(("L192 *********** __init__",self.img,self_starting_img))
        backgroundlayer = self.img.layers[-1]
        if not backgroundlayer.name.startswith("Background"):
            backgroundlayer.name = "Background orig= " + backgroundlayer.name
        has_alpha = pdb.gimp_drawable_has_alpha(self.img.layers[-1])
        if runmode == RUN_INTERACTIVE:
            self.showDialog()
        elif runmode == RUN_WITH_LAST_VALS:
            self.showDialog()
        elif runmode == RUN_NONINTERACTIVE:
            return

 ######## use of adjust
    def next_adjust(self,adjust, object, startcol, startrow, framelabel = None):
        if framelabel:
            small_frame = gtk.Frame(framelabel)
        else:
            small_frame = gtk.Frame()
        small_frame.add(object)
        small_frame.show_all()
        adjust.put(small_frame, startcol, startrow)
        
#### test bucketfill
    def clear_selections(self, widget):
        self.selected_items_shapes = []
        self.cyclic_shapes_deque = None
        self.selected_items_patterns = []
        self.selected_items = []
        debug(("L220", self.selected_items,self.selected_items_shapes, self.selected_items_patterns),1)
        
    def ok_clicked(self, widget):
        #debug(("L223 ok_clicked called"),1)        
        #OrIG self.treeview.get_selection().selected_foreach(foreach, selected)
        tsSel = self.treeview.get_selection()
        res0,res1 = tsSel.get_selected_rows()
        debug(("L227 res0, ",res0),1)
        debug(("L228 res1, ",res1),1)
        self.selected_items = [el[1] for el in res1]
        if res1[0][0] == 0 :
            #self.selected_items.insert(0,'patterns')
            self.selected_items_patterns = [el for el in self.selected_items]
            dbgtmp = 'patterns'
        elif res1[0][0] == 1:
            #self.selected_items.insert(0,"shapes")
            self.selected_items_shapes = [el for el in self.selected_items]
            dbgtmp = "shapes"
            self.chosen_pattern = deque(self.selected_items_shapes)
            self.cyclic_shapes_deque = deque(self.chosen_pattern)

        debug(("ok_clicked", dbgtmp, self.selected_items),1)
        
    def testproc(self, widget        ):
        debug(("L244 testproc", widget     ))
        

    def fillbucket(self, teller, kachel, drawable, x, y, fill_mode = 0, paint_mode = 0, opacity = 100,
                   threshold = 128, sample_merged = False, fill_transparent = False,
                   select_criterion = 0, color = (255,0,0)):
        debug(("L250 fillbucket called,x,y,tel fill_mode  " , x, y, teller, fill_mode, kachel))
        
        if opacity > 100:
            opacity = 100
        if fill_mode == 2:
            num_patterns, pattern_list = pdb.gimp_patterns_get_list('^tile')
            debug(("L256 fillpattern pattenr name", kachel))
            if kachel <> 'random':
                pdb.gimp_context_set_pattern(kachel)
                pdb.gimp_patterns_refresh()
            else:
                fill_mode = 0 #for foreground color!
            debug(("L262 fillbucker pattern_name", kachel))
        elif fill_mode == 999: #use pattern!
            fill_mode = 2
            pdb.gimp_context_set_pattern(kachel)
            pdb.gimp_patterns_refresh()
            debug(("L267 fillbucker pattern_name", kachel))
        elif fill_mode == 1000: #centercolor to be used!
            fill_mode = 2
        pdb.gimp_context_set_foreground(color)
        pdb.gimp_edit_bucket_fill_full(drawable, fill_mode, paint_mode, opacity, threshold, sample_merged, fill_transparent, select_criterion, x, y)
        pdb.gimp_drawable_update(drawable,0,0,drawable.width,drawable.height)
        pdb.gimp_displays_flush()
        pdb.gimp_selection_none(self.img)
        
   
############## Simple path stuff
    def create_simple_pathes(self, widget, *data):
        #old version 1
        global horizontal_guides, vertical_guides
        debug(("L281 data in create_simple_pathes", data ),1)
        horizontal_guides = []
        for n in self.tsH:
            horizontal_guides.append((n[0]))
        vertical_guides = []
        for n in self.tsV:
            vertical_guides.append(n[0])
        number_of_intersections = len(horizontal_guides) * len(vertical_guides)
        #OK>kanweg2dec1643
        debug(("L290 pkhg 1644",number_of_intersections),1)
        if number_of_intersections == 0:
           
            pattern_fill_choice = self.fill_q.get_active()
            take_this_pattern = pdb.gimp_context_get_pattern()
            s = self.pathoptions.get_active()
            pdb.python_fu_plugin_simple_shapes_centered(self.img,\
                            self.img.layers[0], True, s, False,0,0,0,0,False,
                            10,10,10,10,  pattern_fill_choice,
                             take_this_pattern, 0, (255,0,0), 10)
            self.show_my_message("No intersections of guides available!\
            \nNormal use of simple_shapes_centerded done!")

            return
        ellipse_or_rectangle = self.ellipse_or_rectangle.get_active()
        debug(("L295"),1)
        w = self.widthSpinButton.get_value()
        h = self.heightSpinButton.get_value()
        #OK debug(("L298 h w",(h,w)),1)

        #self.pathoptions.set_active(25)
        s = self.pathoptions.get_active() #this is the simple shape chosen!
        no_pattern_list = [1, 6, 13, 14, 36]  #36 is Percentage Ruler, not fillable!
        if s in no_pattern_list:
            s = 25
            
        pattern_fill = self.inselection_q.get_active()
        debug(("L307 def create_simple_pathes  s, pattern_fill", s, pattern_fill),1)
        drawable = self.img.layers[0]
        #random_or_not = self.pattern_checkyn.get_active()
        random_simple_shape = self.random_simple_shape.get_active()
        random_simple_pattern = self.random_simple_pattern.get_active()
        debug(("L312 ", random_simple_shape, random_simple_pattern),1)
        debug(("L313 random_simple shape pattern", random_simple_shape, random_simple_pattern))
        num_patterns, pattern_list = pdb.gimp_patterns_get_list('')
        use_this_shape = 0 #randint(0,46)
        pattern_fill_choice = self.fill_q.get_active()
        flatten_choice = self.flatten_image_q.get_active()
        debug(("L318 flatten_choice", flatten_choice),1)

         ###########????#############
       
        colums_first = []
        for x in vertical_guides:
            for y in horizontal_guides:
                if x == drawable.width:
                    x = drawable.width - 1
                if y == drawable.height:
                    y = drawable.height - 1
                colums_first.append((x,y))
        debug(("L330 colums_first= ", colums_first),1)
        #rows_first_deque = deque(rows_first)
        
        rows_first = []
        for y in horizontal_guides:
            for x in vertical_guides:
                if x == drawable.width:
                    x = drawable.width - 1
                if y == drawable.height:
                    y = drawable.height - 1
                rows_first.append((x,y))
        debug(("L341 rows_first= ", rows_first),1)
        ###########????#############
        rowise = self.paint_colums_first.get_active()
        debug(("L344 rowise = ", rowise),1)
        colums_to_use = colums_first
        if rowise:
            colums_to_use = rows_first
        debug(("L348 colums_to_use = ", colums_to_use),1)
        for el in colums_to_use: #shapes into selections
            x, y = el #PKHG>2dec_02 colums_first_deque[0]
            debug(("L351 x y = ", x, y), 1) 
            kreiseEllipse(self.img, x, y, w, h, operation= 2,\
                              chosen_form = ellipse_or_rectangle)
            debug(("L354 r._simple_pattern",random_simple_pattern),1)
            if random_simple_pattern:
                #pattern_list = pattern_list[]
                num_patterns, pattern_list = pdb.gimp_patterns_get_list('')
                
                if self.selected_items == []:
                    debug(("L360 NO pattern items chosen",self.selected_items),1)
                elif len(self.selected_items_patterns) > 0:
                    pattern_list = [pattern_list[el]
                                    for el in self.selected_items_patterns]
                    num_patterns = len(pattern_list)
                    debug(("L365, pattern_list, num_p. =", pattern_list,
                           num_patterns),1)

                #else:
                   #debug(("L369 only one choice", num_patterns),1)
                
                random_pattern = pattern_list[randint(0, num_patterns - 1)]
                #debug(("L372 random pattern is ", random_pattern),1)
                #pdb.gimp_context_set_pattern(random_pattern)
                take_this_pattern = random_pattern
            
            else:
                take_this_pattern = pdb.gimp_context_get_pattern()
                debug(("L378 take_this_pattern = ", take_this_pattern),1)
                
            if random_simple_shape:
                debug(("L381 test simple random shapes",self.selected_items_shapes),1)
                if len(self.selected_items_shapes) > 0:
                    debug(("L383 1216",),1)
                    nr_of_shapes = len(self.selected_items_shapes)
                    if nr_of_shapes == 1:
                        self.pathoptions.set_active(self.selected_items_shapes[0])
                        use_this_shape = self.selected_items_shapes[0]
                    else:
                        #PKHG>2dec_01 to do warning if not possible!
                        use_cyclic = self.cyclic_shapes.get_active()
                        """
                        if (not use_cyclic) and self.cyclic_shapes_deque == None:
                            use_cylic = False
                            self.show_my_message("you ask for cyclic shapes,\
                            but you did not choose any ;-)")
                        """
                        debug(("L397 use_cyclic = ", use_cyclic),1)
                        if use_cyclic:
                             tmp = self.cyclic_shapes_deque[0]
                             debug(("L400 tmp = ", tmp),1)
                             use_this_shape = tmp
                             self.cyclic_shapes_deque.rotate(-1)                                
                        else:
                            tmp = randint(0, nr_of_shapes - 1)
                            use_this_shape = self.selected_items_shapes[tmp]
                        debug(("L406 cyclic use_this_shape", use_cyclic, use_this_shape),1)
                else:
                    use_this_shape = randint(0,46)
                debug(("L409 27nov  use_this_shape", use_this_shape),1)
                self.pathoptions.set_active(use_this_shape)
                #use_this_shape = pattern_list[randint(0,46)] #(1 + use_this_shape) % 47

                s = self.pathoptions.get_active() #this is the simple shape chosen!
                if s in no_pattern_list:
                    s = 25

                debug(("L417 s = ", s), 1)
                
                pdb.python_fu_plugin_simple_shapes_centered(self.img,\
                            drawable, True, s, False,0,0,0,0,False,
                            10,10,10,10, pattern_fill_choice,
                             take_this_pattern, 0, (255,0,0), 10)
                if flatten_choice:
                    #Flatten if wanted
                    drawable = pdb.gimp_image_flatten(self.img) 
            else:
                debug(("L427 reason why nothing"), 1)
                pdb.python_fu_plugin_simple_shapes_centered(self.img,\
                            drawable, True, s, False,0,0,0,0,False,
                            10,10,10,10, pattern_fill_choice,
                             take_this_pattern, 0, (255,0,0), 10)
                if flatten_choice:
                    #Flatten if wanted
                    drawable = pdb.gimp_image_flatten(self.img) 

            
        pdb.gimp_selection_none(self.img)
        
############## guides-to-path
    def python_guides_to_path_pkhg(self, image, layer):
        global horizontal_guides, vertical_guides
        #PKHG>DBG gimp.message("python_guides_to_path_pkhg called" )
        pdb.gimp_image_undo_group_start(image)
        start_time = time()
        #grab selection bounding box values
        selection = pdb.gimp_selection_bounds(image)
        #grab all guides-ids into guides
        x1, y1, x2, y2 = selection[1:]
        guides = []
        next_guide = 0
        next_guide = pdb.gimp_image_find_next_guide(image, next_guide)
        while next_guide != 0:
            guides.append(next_guide)
            next_guide = pdb.gimp_image_find_next_guide(image, next_guide)
        #check if guides in the selectin (a rectangle) and save horizontal and vertical values
        vertical_guides = []
        horizontal_guides = []
        for guide in guides:
            guide_orientation = pdb.gimp_image_get_guide_orientation(image, guide)
            guide_position = pdb.gimp_image_get_guide_position(image, guide)
            if guide_orientation == 1: #vertical guide
                if (guide_position >= x1) and (guide_position <= x2): #if it's within the selected x-range
                    vertical_guides.append(guide_position)
            else: #horizontal guide
                if (guide_position >= y1) and (guide_position <= y2): #if it's within the selected y-range
                    horizontal_guides.append(guide_position)
            #create the needed vectors into ONE vector
            #always either length of selection or width of selection,
            #that makes the algorithm linear time consuming
        nw = None
        myinfo = []
        for vertical in vertical_guides:
            myinfo += [[vertical, y1] * 3 + [vertical, y2]*3]
        for horizontal in horizontal_guides:
            myinfo += [[x1, horizontal]*3 + [ x2, horizontal]*3 ]
        if myinfo:
            nw = pdb.gimp_vectors_new(image,"guides PKHG")
            pdb.gimp_image_insert_vectors(image,nw, None, -1)
            for el in myinfo:
                pdb.gimp_vectors_stroke_new_from_points(nw, 0 ,12, el, 0)
            #gimp.message("time used = " + str(round(time() - start_time,3)))
            #PKHG>DBG pdb.gimp_message("guide_to_path_pkhg.py done")
        else:
            #PKHG>OLD debug("???? No guide set ;-)")
            self.show_my_message("no guide available")
        pdb.gimp_image_undo_group_end(image)
        
############ end guides-to-path

    def tabHelp(self, tab):
        row = 0
        msgs = [
            ("Double click on the <b>Delete</b> cell for delete the guide.")+"\n",
            "<b>"+("In the text fields you can use the following shortcuts:")+"</b>",
            ("<b>Width</b>, <b>width</b>, <b>W</b> or <b>w</b>:\n\tReplaced by the width of the current selected image"),
            ("<b>Height</b>, <b>height</b>, <b>H</b> or <b>h</b>:\n\tReplaced by the height of the current selected image")+"\n",
            "<b>"+("SAMPLES OF USAGE:")+"</b>",
            "\t"+("For add a guide on the vertical center:")+"<span foreground='blue' background='white'> <tt>h/2</tt> </span>",
            "\t"+("For add a guide at 10 pixels of the bottom:")+
            "<span foreground='blue' background='white'> <tt>H-10</tt></span>" + "\t"+("For add a guide at 10 pixels of the center")+
            ":<span foreground='blue' background='white'>  <tt>height/2+10</tt></span>" +
            ("\n\npushing the button <b>Path on Guides inside selections</b> creates a path") +
            ("\nyou may stroke an available path with pencil and background-color") +
                ("\nyou may opt for deleting the the active vextors") +"\n" +
                ("<span foreground='blue' background='white'>You may have a selection active, then only guides INSIDE </span>"),
                
        ]
        tx=""
        for line in msgs:
                tx+=line+"\n"
                lb=self.ui.addRows(self.ui.addLabel(tx,0,0),tab, 2, 4, row, row+1)
                lb.set_use_markup(True)
                
    def test_message(self, widget):
        if widget.get_name() == "test_button":
            self.show_my_message(widget.get_label()) #"Test button clicked")

    def show_my_message(self, msg = "Hallo die Enten"):
        """
        Helper for popup message screens
        """
        dialog = gtk.MessageDialog()
        dialog.set_markup(msg)
        dialog.format_secondary_text("\n\nRemove me ;-)\nRepair: set guide(s) or/and create the path !")
        dialog.run()
        dialog.destroy()
            
    def parseVal(self,val):
        s=val
        if s==self.newG: s='0'
        for nn in ['Width','width','W','w']: s=s.replace(nn,str(self.img.width))
        for nn in ['Height','height','H','h']: s=s.replace(nn,str(self.img.height))
        return eval(s)

    def guideExists(self, v, direction):
        i=self.img
        g=i.find_next_guide(0)
        dir=0 if direction=='h' else 1
        while (g>0):
            if i.get_guide_orientation(g)==dir:
                pos=i.get_guide_position(g)
                if pos==v: return True
            g=i.find_next_guide(g)
        return False

    def addGH(self, v):
        if self.guideExists(v, 'h'): return
        hid=self.img.add_hguide(v)
        self.tsH.append([v,hid,0,0,0])
        self.printNext(self.tsH)

    def addGV(self, v):
        if self.guideExists(v, 'v'): return
        hid=self.img.add_vguide(int(v))
        self.tsV.append([v,hid,0,0,0])
        self.printNext(self.tsV)

    def addH(self, widget):
        v=int(self.parseVal(self.newH.get_text()))
        h=self.img.height
        w=self.img.width
        unit=self.newHunit.get_active()
        #PKHG>Giebt 0 fuer px 1 fuer %: gimp.message("unit gewaehlt = " + str(unit))
        if unit==1: v=int(h/100.0*v)
        self.addGH(v)
        repli=self.cbH.get_active()
        if repli>0:
            center = h / 2.0
            if v!=center:
                self.addGH(h - v)
        if repli==2:
            self.addGV(v)
            self.addGV(w-v)

    def addV(self, widget):
        v=int(self.parseVal(self.newV.get_text()))
        w=self.img.width
        h=self.img.height
        unit=self.newVunit.get_active()
        if unit==1: v=int(w/100.0*v)
        self.addGV(v)
        repli=self.cbV.get_active()
        if repli>0:
            center = w / 2.0
            if v!=center:
                self.addGV(w - v)
        if repli==2:
            self.addGH(v)
            self.addGH(h-v)

    def evalSpin(self, widget, data=None):
        s=widget.get_text()
        v=self.parseVal(s)
        widget.set_value(v)

    def onEditGuide(self, widget, path, value, treeSt, name):
        v=int(self.parseVal(value))
        ts=treeSt
        if int(ts[path][0])==int(v): return
        self.img.delete_guide(ts[path][1])
        if name=="h":
            hid=self.img.add_hguide(min(v, self.img.height))
        else:
            hid=self.img.add_vguide(min(v, self.img.width))
        ts[path][1] = hid
        ts[path][0] = v
        self.printNext(ts)

    def printNext(self,ts):
        if len(ts)==0:return
        ts.set_sort_column_id (0, gtk.SORT_ASCENDING)
        ts[0][2]=int(ts[0][0])
        name=ts.get_name()
        for n in range(1,len(ts)):   ts[n][2]=int(ts[n][0])-int(ts[n-1][0])
        for n in range(0,len(ts)-1): ts[n][3]=int(ts[n+1][0])-int(ts[n][0])
        last=ts[len(ts)-1]
        last[3]=self.img.height-last[0] if name=="ts_h" else self.img.width-last[0]
        #debug(("L618 printNext ts[0][0]", ts[0][0]), urgent = 1) #ts[0] is a TreeModelRow object, [:] impossible!
        
    def delGuide(self, widget, row, col):
        tit=col.get_title()
        treeSt=widget.get_model()
        if tit==self.titDel:
            id=treeSt[row][1]
            self.img.delete_guide(id)
            for fila in treeSt:
                if fila[1] == id:
                    treeSt.remove(fila.iter)
                    self.printNext(treeSt)
                    break

    def addCol(self,tv,title,renderer,pos,postx,tip,sortCol=None):
        col = gtk.TreeViewColumn(title, renderer, text=postx) 
        label = gtk.Label(title)
        col.set_widget(label)
        label.show()
        self.ui.addTip(label,tip)
        tv.insert_column(col,pos)
        if sortCol != None : col.set_sort_column_id(sortCol)

    def addTV(self,name):
        tS=gtk.ListStore(int,int,int,int,int)
        tS.set_name("ts_"+name)
        tv=gtk.TreeView(tS)
        tv.set_name(name)
        rendImg=gtk.CellRendererPixbuf()
        #PKHF>TEST http://www.pygtk.org/pygtk2reference/gtk-stock-items.html Pictures!
        rendImg.set_property('stock-id',gtk.STOCK_DELETE)
        #rendImg.set_property('stock-id',gtk.STOCK_CUT)
        self.addCol(tv,self.titDel,rendImg,3,0,self.tipDel)
        rendSpin = gtk.CellRendererSpin()
        rendSpin.connect("edited", self.onEditGuide,tS,name)
        maxVal=self.img.height if name=='h' else self.img.width
        self.ui.addProps(rendSpin,[("editable",True),("adjustment",gtk.Adjustment(0,0,maxVal,1,10,0))])
        self.addCol(tv,("Position"),rendSpin,0,0,self.tipPos,0)
        ###self.addCol(tv,("Position"),rendSpin,0,self.tipPos,0)
        rendTx = gtk.CellRendererText()
        rendTx.set_property("editable", False)
        self.addCol(tv, ("Prev"), rendTx, 1,2, self.tipPrev)
        ###self.addCol(tv, ("Prev"), rendTx, 1, self.tipPrev)
        self.addCol(tv, ("Next"), rendTx, 2,3, self.tipNext)
        ###self.addCol(tv, ("Next"), rendTx, 2, self.tipNext)
        tv.set_rules_hint(True)
        tv.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        tv.set_show_expanders(False)
        tv.connect('row-activated',self.delGuide)
        selection = tv.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        sW = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        sW.set_shadow_type(gtk.SHADOW_IN)
        sW.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sW.add(tv)
        sW.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        tv.show()
        sW.show()
        return (tS,tv,sW)
    
    def getGuides(self,widget=None):
        i=self.img
        lH=[]
        lV=[]
        self.tsH.clear()
        self.tsV.clear()
        g=i.find_next_guide(0)
        while (g>0):
            lst = lH if i.get_guide_orientation(g)==0 else lV
            lst.append([i.get_guide_position(g),g,0,0,0])
            g=i.find_next_guide(g)
        lH.sort(key=lambda tup: tup[0])
        lV.sort(key=lambda tup: tup[0])
        if widget:
            try:
                self.name = widget.get_name()
            except:
                e = sys.exc_info()[0]
                debugErr(e)
                return           #PKHG>premature end of action!!!
            image = gimp.image_list()[0]
            name = widget.get_name()
        for n in lH: self.tsH.append(n)
        for n in lV: self.tsV.append(n)
        self.printNext(self.tsH)
        self.printNext(self.tsV)

    def delGuides(self,widget=None):
        i=self.img
        all=[]
        g=i.find_next_guide(0)
        while (g>0):
            all.append(g)
            g=i.find_next_guide(g)
        for i in reversed(all): self.img.delete_guide(i)
        
    def pattern_def(self, widget, *data):
        #PKHG>DBG OK
        gimp.message("L716" + str(data))
        pdb.gimp_context_set_pattern(data[0]) #PKHG>Name of chosen pattern
        
    def call_plugin(self, widget):
        name = widget.get_name()
        image = gimp.image_list()[0]
        self.activeornot = self.checkynGUI.get_active()
        self.dialog.set_keep_above(self.activeornot)
            
        if name == "Path on Guides inside selections":
            layer = image.layers[0]
            self.python_guides_to_path_pkhg(image, layer)
        elif name == "create_new_layer":
            #debug("L729 TODO add new layer")
            layer_new = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 1, 'new layer', 100, 0)
            pdb.gimp_image_add_layer(self.img, layer_new, 0)
        elif name == "fill_q":
            gimp.message("TODO activate fill_q")
        elif name == "pattern_select_button":
            gimp.message("L735 name = " + name)
        elif name == "stroke_guides":
            active_vectors = pdb.gimp_image_get_active_vectors(image)
            if active_vectors:
                pdb.gimp_edit_stroke_vectors(image.layers[0], active_vectors)
                pdb.gimp_item_set_visible(active_vectors, True)
                pdb.gimp_displays_flush()
                if self.checkyn.get_active():
                    pdb.gimp_image_remove_vectors(image, active_vectors)
            else:
                self.show_my_message("no active vectors available")
        elif name == "severalGuides":
            start = int(self.startSpinButton.get_value())
            step = int(self.stepSpinButton.get_value())
            amount = int(self.amountSpinButton.get_value())
            orientation = "horizontal"
            maxval = 0
            if self.orientation.get_active():  #only 0 and 1 (hor) and (vert)
                orientation = "vertical"
            if orientation == "horizontal":
                maxval = self.img.height
            else:
                maxval = self.img.width
            tmp = start
            nb = 1 #for old way
            nb = amount
            if start + step * amount > maxval:
                nb = int((maxval - start) / step)
                if start + step * nb <= maxval:
                    nb += 1
            res = [ start + i * step for i in range(nb)]
            for el in res:
                if orientation == "horizontal":
                    self.addGH(el)
                    if  horizontal_guides.count(el) == 0:
                        horizontal_guides.append(el)
                else:
                    self.addGV(el)
                    if vertical_guides.count(el) == 0:
                        vertical_guides.append(el)
            #debug((horizontal_guides,vertical_guides))
            #debug(("severalGuides called", start, step, amount, orientation, maxval, nb, tmp, res))

        
    def tt(self,w, data=None):
        if type(w) != type(gtk.CheckButton):
            s=w.get_text()
            v=self.parseVal(s)
            w.set_value(v)        
        
    def tabOne(self):
        """
        Create layout for the guide-lab
        """
        try:
            row=0
            guidelab_tab = 0
            self.ui.addRows(self.ui.addLabel(('H \nO\nR\nI\nZ\nO\nN\nT\nA\nL')), self.tabs[guidelab_tab], 0, 1, row, row+1)
            self.ui.addRows(self.ui.addLabel(('V \nE\nR\nT\nI\nC\nA\nL')), self.tabs[guidelab_tab], 5, 6, row, row+1)

            self.tsH,tvh,sWh=self.addTV('h')
            self.tsV,tvv,sWv=self.addTV('v')
            self.ui.addRows(sWh, self.tabs[guidelab_tab], 1, 5, row, row+1)
            self.ui.addRows(sWv, self.tabs[guidelab_tab], 6, 10, row, row+1)
            row += 1
            #newAt=('New guide at')
            newAt=('Guide ')
            addOpposite=("Add an aditional guide on the oposite side")
            # horizontal
            self.ui.addRows(self.ui.addLabel(newAt), self.tabs[guidelab_tab], 1, 2, row, row+1)
            self.newH=self.ui.addRows(gtk.SpinButton(gtk.Adjustment(0, 0, self.img.height, 1), 0.0, 0), self.tabs[guidelab_tab], 2, 3, row, row+1,"activate",self.evalSpin)
            self.newH.connect("focus-out-event",self.tt)
            self.newHunit=self.ui.addRows(self.ui.makeCombo([['px',0],['%',1]]), self.tabs[guidelab_tab], 3, 4, row, row+1)
            self.ui.addTip(self.newH, self.newGuideTip)

            self.ui.addRows(self.ui.addLabel("Replicate "), self.tabs[guidelab_tab], 1, 2, row+1, row+2)
            CORNERS=[[('None'),0],[('Mirror'),1],[('Perimeter'),2]]
            self.cbH=self.ui.addRows(self.ui.makeCombo(CORNERS), self.tabs[guidelab_tab], 2, 4, row+1, row+2)
            self.newHB=self.ui.addRows(gtk.Button('','Add'), self.tabs[guidelab_tab], 4, 5, row, row+2,"clicked",self.addH)

            self.ui.addRows(self.ui.addLabel(newAt), self.tabs[guidelab_tab], 6, 7, row, row+1)
            self.newV=self.ui.addRows(gtk.SpinButton(gtk.Adjustment(0,0,self.img.width,1),0.0,0), self.tabs[guidelab_tab], 7, 8, row, row+1,"activate",self.evalSpin)
            self.newV.connect("focus-out-event",self.tt)
            self.newVunit=self.ui.addRows(self.ui.makeCombo([['px',0],['%',1],['aaa',2]]), self.tabs[guidelab_tab], 8, 9, row, row+1)

            self.ui.addRows(self.ui.addLabel("Replicate "), self.tabs[guidelab_tab], 6, 7, row+1, row+2)
            CORNERS=[[('None'),0],[('Mirror'),1],[('Perimeter'),2]]
            self.cbV=self.ui.addRows(self.ui.makeCombo(CORNERS), self.tabs[guidelab_tab], 7, 9, row+1, row+2)
            
            self.newVB=self.ui.addRows(gtk.Button('',gtk.STOCK_ADD), self.tabs[guidelab_tab], 9, 10, row, row+2,"clicked",self.addV)
            row += 1
            self.getGuides()
            row += 1
            self.refresh=self.ui.addRows(gtk.Button(('Update manual changes')), self.tabs[guidelab_tab], 1, 5, row, row+1,'clicked',self.getGuides)
            self.refresh=self.ui.addRows(gtk.Button(('Delete all guides')), self.tabs[guidelab_tab], 6, 10, row, row+1,'clicked',self.delGuides)
            self.refresh.connect('clicked',self.getGuides)
            row += 1
            infoSeveral = gtk.Label("several guides")
            self.ui.addRows(infoSeveral, self.tabs[guidelab_tab], 0, 1, row, row + 1)

            self.ui.addRows(gtk.Label("start"), self.tabs[guidelab_tab], 1, 2, row, row + 1)
            self.startSpinButton = gtk.SpinButton(gtk.Adjustment(125, 0, self.img.width, 1), 0.0, 0)
            self.startSpinButton.set_name('start')
            r01 = self.ui.addRows(self.startSpinButton, self.tabs[guidelab_tab], 2, 3, row, row+1,"activate", self.evalSpin)
            self.ui.addRows(gtk.Label("step"), self.tabs[guidelab_tab], 3, 4, row, row + 1)
            self.stepSpinButton = gtk.SpinButton(gtk.Adjustment(250, 1, self.img.width, 1), 0.0, 0)
            self.stepSpinButton.set_name('step')
            r02 = self.ui.addRows(self.stepSpinButton, self.tabs[guidelab_tab], 4, 5, row, row + 1,"activate", self.evalSpin)
            self.ui.addRows(gtk.Label("amount"), self.tabs[guidelab_tab], 5, 6, row, row + 1)
            self.amountSpinButton = gtk.SpinButton(gtk.Adjustment(2, 1, self.img.width, 1), 0.0, 0)
            self.amountSpinButton.set_name('amount')
            self.r03 = self.ui.addRows(self.amountSpinButton, self.tabs[guidelab_tab], 6, 7, row, row + 1,"activate", self.evalSpin)
            self.orientation = self.ui.addRows(self.ui.makeCombo([['horizontal',0],['vertical',1]]), self.tabs[guidelab_tab], 7, 8, row, row + 1)          
            amount = int(self.amountSpinButton.get_value())
            #debug(amount)
            #res = self.orientation.get_active()
            #debug(("orientation",res))
            orientation = "horizontal"
            if self.orientation.get_active():  #only 0 and 1 (hor) and (vert)
                orientation = "vertical"
            tmpinfo = "create more guides"
            #debug(tmpinfo)
            self.severalGuides = gtk.Button(tmpinfo) 
            self.severalGuides.set_name("severalGuides")
            self.refresh = self.ui.addRows(self.severalGuides, self.tabs[guidelab_tab], 8, 9,
                                           row, row + 1, 'clicked' , self.call_plugin)
            row += 1
            #self.thisWindowOnTop = gtk.Label("This Gui always on Top?")
            #self.thisWindowOnTop.set_name("Gui_on_top")
            #self.refresh = self.ui.addRows(self.thisWindowOnTop, self.tabs[guidelab_tab], 0, 2,
            #                               row, row + 1)# 'clicked' , self.call_plugin)
            row += 1
            linesep1 = gtk.HSeparator()
            self.ui.addRows(linesep1, self.tabs[guidelab_tab],0,10, row,row + 1)
            row += 1
            self.checkynGUI = gtk.CheckButton("This window always on top: y/n")
            self.ui.addRows(self.checkynGUI, self.tabs[guidelab_tab], 2,4, row, row + 1, 'clicked', self.call_plugin)

            #self.ui.addRows(gtk.Label("-------------------------------------"), self.tabs[guidelab_tab], 3, 10, row, row + 1)
            row += 1
            linesep1 = gtk.HSeparator()
            self.ui.addRows(linesep1, self.tabs[guidelab_tab],0,10, row,row + 1)
            row += 1
            self.wishGuides = gtk.Button("Path on Guides inside selections")
            self.wishGuides.set_name("Path on Guides inside selections")
            self.refresh = self.ui.addRows(self.wishGuides, self.tabs[guidelab_tab], 1, 5,
                                           row, row + 1, 'clicked' , self.call_plugin)
            self.removeLabel = gtk.Label("remove vector")
            self.checkyn = gtk.CheckButton("y/n")
            self.ui.addRows(self.removeLabel, self.tabs[guidelab_tab], 6, 7, row, row + 1)
            self.ui.addRows(self.checkyn, self.tabs[guidelab_tab], 7, 8, row, row + 1, 'clicked', self.call_plugin)
            self.strokeGuides = gtk.Button("stroke active Vector") 
            self.strokeGuides.set_name("stroke_guides")
            self.refresh = self.ui.addRows(self.strokeGuides, self.tabs[guidelab_tab], 8, 9,
                                           row, row + 1, 'clicked' , self.call_plugin)
            row += 1
            linesep1 = gtk.HSeparator()
            self.ui.addRows(linesep1, self.tabs[guidelab_tab],0,10, row,row + 1)

#######21bov PKHG>today 21nov start painttab (for now)
            row = 0
            paint_tab = 2
            row += 1
            #self.newLabel = gtk.Label("Select ellipse or rectangle maybe width and height etc.")
            #self.ui.addRows(self.newLabel, self.tabs[paint_tab], 3, 5, row, row + 1 )
            #row += 1
            
            #self.ui.addRows(self.newLabel, self.tabs[paint_tab], 0, 5, row, row + 1 )
            #xrow += 1
            #myframe the container for all paint options ...
            myframe = gtk.Frame("Paint ellipse or rectangel on guide intersectionpoints ;-)")
            
            paint_adjust = gtk.Layout(hadjustment = None, vadjustment = None)
            """
            self.next_adjust(paint_adjust, gtk.Label("gaat dit"), 10 ,60)
            self.next_adjust(paint_adjust, gtk.Label("gaat ditook"), 100, 60, "Hallo how are you?")
            """
            start_x = 10
            self.ellipse_or_rectangle = self.ui.makeCombo([['ellipse',2],['rectangle',1]])
            self.next_adjust(paint_adjust, self.ellipse_or_rectangle , start_x, 20,
                             "Select ellipse or rectangle maybe width and height etc.")
            self.widthSpinButton = gtk.SpinButton(gtk.Adjustment(250, 2, self.img.width, 1), 0.0, 0)
            self.next_adjust(paint_adjust, self.widthSpinButton, start_x + 310, 20, "set width")
            self.heightSpinButton = gtk.SpinButton(gtk.Adjustment(250, 2, self.img.height, 1), 0.0, 0)
            self.next_adjust(paint_adjust,self.heightSpinButton, start_x + 380, 20, "set height")
            
            self.selection_type = self.ui.makeCombo([['no',0],['fg color',1],['centercolor',2],['pattern',3],['kacheln',4]])
            self.next_adjust(paint_adjust, self.selection_type, start_x, 70,"choose filltype")
            self.pattern_checkyn = gtk.CheckButton("y/n")
            self.next_adjust(paint_adjust,self.pattern_checkyn, start_x + 100, 70, "random fg or pattern")

            self.createnow_button = gtk.Button("OK, go!")
            self.createnow_button.connect('clicked', self.createellipses)
            self.next_adjust(paint_adjust, self.createnow_button, start_x + 310, 70,
                             "create at guide intersections")
            
            paint_adjust.show()
            #myframe.add(self.newLabel)
            
            myframe.add(paint_adjust)
            self.ui.addRows(myframe, self.tabs[paint_tab], 0,1 , row, row + 1)
            

#################end paint - tab (for now)

            #PKHG>Simple path layout
            row = 0
            simple_path_tab = 3
            self.ui.addRows(gtk.Label("Size used, use 'Paint stuff' \
                        others here:Parameters of Use for 'Simple paths centured' 1.0 beta "),
                        self.tabs[simple_path_tab], 0, 4, row, row + 1)
            row += 1
            self.ui.addRows(gtk.Label("choose:"), self.tabs[simple_path_tab], 0, 1, row, row + 1)
            self.pathoptions = self.ui.addRows(self.ui.makeCombo(
[
    ['Arrow',0],['Axis of symmetry',1],['Binoculars',2],['Circle',3],
['Crescent',4],['Cross',5],['Diagonals',6],
['Diamond',7],['Dodecagon',8],['Ellipse',9],
['Flower 1 Out',10],['Flower 2 In',11],['GEAR',12],
['Grid rectangular (c) Ofnuts v0.0',13],['Start Grid==',14],['Mobius band',15],
['Octaagon',16],['Pentagon',17],['Pentagram',18],
[' Petal (butterfly)',19],['Pie 1/2',20],['Pie 3/4 - 1/4',21],
['Pie 7/8 - 1/8',22],['Playing cards Clubs',23],['Playing cards Diamonds',24],
['Playing cards Hearts',25],['Playing cards Spades',26],['POLYGON',27],
['Protractor Inside circle',28],['Start Protra',29],['Quadrant',30],
['Quatrefoil',31],['Rectangle',32],['Recycle two arrows',33],
['Recycle three arrows',34],['Roses compass',35],['Percentage Ruler',36],
['Semicircle',37],['Square',38],['STAR',39],
['Star pentagons',40],['Triangle equilateral',41],['Triangle isosceles',42],
['Triangle Reuleaux',43],['Trefoil',44],['Yin-Yang',45],
['Wilber',46]
]),self.tabs[simple_path_tab], 1, 2, row, row + 1)

            #not with pattern no_pattern_list = [1, 6, 13, 14, 36]
            #self.ui.addRows(gtk.Label("In selection?"), self.tabs[simple_path_tab], 2, 3, row, row + 1)
            self.inselection_q = gtk.CheckButton("in selection(s) y/n?!")
            self.ui.addRows(self.inselection_q, self.tabs[simple_path_tab], 3, 4, row, row + 1, 'clicked', self.call_plugin)

            row += 1
            self.ui.addRows(gtk.Label("Resize layer?"), self.tabs[simple_path_tab], 0, 1, row, row + 1)
            self.resize_q = gtk.CheckButton("y/n")
            self.ui.addRows(self.resize_q, self.tabs[simple_path_tab], 1, 2, row, row + 1, 'clicked', self.call_plugin)
            self.ui.addRows(gtk.Label("Resize all layers to image size?"), self.tabs[simple_path_tab], 2, 3, row, row + 1)
            self.resize_all_q = gtk.CheckButton("y/n")
            self.ui.addRows(self.resize_all_q, self.tabs[simple_path_tab], 3, 4, row, row + 1, 'clicked', self.call_plugin)
            
            row += 1
            self.ui.addRows(gtk.Label("from right (pix)"), self.tabs[simple_path_tab], 0, 1, row, row + 1)
            self.ui.addRows(gtk.Label("from left (pix)"), self.tabs[simple_path_tab], 1, 2, row, row + 1)
            self.ui.addRows(gtk.Label("from top (pix)"), self.tabs[simple_path_tab], 2, 3, row, row + 1)
            self.ui.addRows(gtk.Label("from bottom (pix)"), self.tabs[simple_path_tab], 3, 4, row, row + 1)
            row += 1
            self.resize_left = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_left.set_name('resize_left')
            r1 = self.ui.addRows(self.resize_left, self.tabs[simple_path_tab], 0, 1, row, row+1,"activate", self.evalSpin)
            self.resize_right = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_right.set_name('resize_right')
            r1 = self.ui.addRows(self.resize_right, self.tabs[simple_path_tab], 1, 2, row, row+1,"activate", self.evalSpin)
            self.resize_top = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_top.set_name('resize_top')
            r1 = self.ui.addRows(self.resize_top, self.tabs[simple_path_tab], 2, 3, row, row+1,"activate", self.evalSpin)
            self.resize_bottom = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_bottom.set_name('resize_bottom')
            r1 = self.ui.addRows(self.resize_bottom, self.tabs[simple_path_tab], 3, 4, row, row+1,"activate", self.evalSpin)
            row += 1  #gimpui ... for 
            #self.pattern_select  = self.ui.addRows(self.PatternSelector, self.tabs[simple_path_tab], 0, 1, row, row + 1)
            #self.ui.addRows(gtk.Label("pattern fill?"), self.tabs[simple_path_tab], 0, 1, row, row + 1)
            self.flatten_image_q = gtk.CheckButton("FLATTEN image?")
            self.ui.addRows(self.flatten_image_q, self.tabs[simple_path_tab], 0, 1, row, row + 1)
            self.fill_q = gtk.CheckButton("pattern fill?")
            self.fill_q.set_name("fill_q")
            self.ui.addRows(self.fill_q, self.tabs[simple_path_tab], 1, 2, row, row + 1)
            #PKHG>no general OK!!, 'clicked', self.call_plugin)
            self.random_simple_pattern = gtk.CheckButton("random pattern for Simple shape?")
            self.ui.addRows(self.random_simple_pattern, self.tabs[simple_path_tab], 2, 3,
                            row, row + 1)            
            self.pattern_select_button = _gimpui.PatternSelectButton()
            #PKHG>works ;-) gimp.message(str(dir(self.pattern_select_button)))
            self.rpattern = self.ui.addRows(self.pattern_select_button,
                                            self.tabs[simple_path_tab], 3, 4,
                                            row, row + 1,"pattern_set", self.pattern_def)
            row += 1
            self.random_simple_shape = gtk.CheckButton("random Simple shape?")
            self.ui.addRows(self.random_simple_shape, self.tabs[simple_path_tab], 0, 1, row, row + 1)
           
            self.cyclic_shapes = gtk.CheckButton("use selected shapes cyclic")
            self.ui.addRows(self.cyclic_shapes, self.tabs[simple_path_tab], 1, 2, row, row + 1)
            self.paint_colums_first = gtk.CheckButton("paint rowise")
            self.ui.addRows(self.paint_colums_first, self.tabs[simple_path_tab], 2, 3, row, row + 1)
            
            row += 1 
            final_simple_path_centered = gtk.Button("OK: do now!")
            self.ui.addRows(final_simple_path_centered, self.tabs[simple_path_tab], 0, 4 , row, row + 1, 'clicked', self.create_simple_pathes)

################# please change here ##################
            row = 0
            test4 = 4
            """
            num_patterns, mydata = pdb.gimp_patterns_get_list('')
            kanweg1 = gtk.Label(" label 1148 16 nov ")
            test01 = self.ui.addRows(kanweg1, self.tabs[test4], 1, 2 , row, row + 1)
            row += 1
            """


################# end test tile for treeview #######################
        except Exception,e:
            debug(e)

    def createellipses(self, widget):
        global horizontal_guides, vertical_guides
        
        self.img = gimp.image_list()[-1]
        horizontal_guides = []
        for n in self.tsH:
            horizontal_guides.append((n[0]))
        vertical_guides = []
        for n in self.tsV:
            vertical_guides.append(n[0])
        debug(("L1054 should be done"))
        number_of_intersections = len(horizontal_guides) * len(vertical_guides)
        
        ellipse_or_rectangle = self.ellipse_or_rectangle.get_active()
        if ellipse_or_rectangle == 0:
            ellipse_or_rectangle = 'ellipse'
        else:
            ellipse_or_rectangle = 'rectangle'
        debug(("L1062 ellipse_or_rectangle ", ellipse_or_rectangle),1)
        #debug((vertical_guides, horizontal_guides))
        if number_of_intersections == 0:
            self.show_my_message("no guide-intersection yet available")
            return
        #PKHG>premature end of this def, if no intersections available ;-( !!
        ftypes = ['no', 'fg color', 'centercolor', 'pattern', 'kacheln'] #PKHG>31oct pay attention!
        debug(("L1069 createellipses"))
        tmp = self.selection_type.get_active()
        debug(("1028 active filltype" , tmp))      
        filltype = ftypes[int(self.selection_type.get_active())]
        debug(("L1073 filltype werd ", filltype))
        w = self.widthSpinButton.get_value()
        h = self.heightSpinButton.get_value()
        if filltype == 'no':
            for x in vertical_guides:
                for y in horizontal_guides:
                    kreiseEllipse(self.img, x, y, w, h, operation= 0, chosen_form = ellipse_or_rectangle)
            #return
        elif filltype == 'fg color' or filltype == 'centercolor':
            drawable = self.img.layers[0]
            random_chosen = self.pattern_checkyn.get_active() #not good: self.fill_q.get_active()
            debug(("L1084 filltype random_chosen", filltype, random_chosen))            
            for x in vertical_guides:
                for y in horizontal_guides:
                    if x == drawable.width:
                        x = drawable.width - 1
                    if y == drawable.height:
                        y = drawable.height - 1
                        
                    kreiseEllipse(self.img, x, y, w, h, operation= 2,
                                  chosen_form = ellipse_or_rectangle)
                    if filltype == 'centercolor':
                        #PKHH>orig num_channels, color = pdb.gimp_drawable_get_pixel(drawable, x, y)
                        num_channels, color = pdb.gimp_drawable_get_pixel(self.img.layers[-1], x, y)
                        #debug(("center color",color," tel",tel))
                        debug(("L1098 x y = centercolor",x,y, color))
                    else:
                        debug(("L1100 no center_color",random_chosen))
                        if random_chosen:
                            color = random_rgb()
                        else:
                            color = pdb.gimp_context_get_foreground()
                    debug(("L1105 random or not filltype",random_chosen,filltype))
                    pdb.gimp_context_set_foreground(color)
                    debug(("L1107 color=", color))
                    #pdb.gimp_edit_bucket_fill_full(drawable, fill_mode = 0 =foregroundcolor,
                    #paint_mode, opacity, threshold, sample_merged, fill_transparent, select_criterion, x, )
                    pdb.gimp_edit_bucket_fill_full(drawable, 0, 0, 100, 128, False, False, 0, x, y)
                    debug(("L1111 random colors"))
                    pdb.gimp_drawable_update(drawable,0,0,drawable.width,drawable.height)
                    pdb.gimp_displays_flush()
                    
            pdb.gimp_selection_none(self.img)
            random_pattern = pattern_list[randint(0, num_patterns - 1)]
            #return
        elif filltype == 'pattern':
            drawable = self.img.layers[0]
            random_or_not = self.pattern_checkyn.get_active()
            num_patterns, pattern_list = pdb.gimp_patterns_get_list('')
            for x in vertical_guides:
                for y in horizontal_guides:
                    if x == drawable.width:
                        x = drawable.width - 1
                    if y == drawable.height:
                        y = drawable.height - 1
                    kreiseEllipse(self.img, x, y, w, h, operation= 2,
                                  chosen_form = ellipse_or_rectangle)
                    #pdb.gimp_edit_bucket_fill_full(drawable, fill_mode = 0 =foregroundcolor,
                    #paint_mode, opacity, threshold, sample_merged, fill_transparent, select_criterion, x, y)
                    debug(("941 install pattern"))
                    if random_or_not:
                        #pattern_list = pattern_list[]
                        random_pattern = pattern_list[randint(0, num_patterns - 1)]
                        debug(("L1136 random pattern is ",len(pattern_list) == num_patterns, random_pattern))
                        pdb.gimp_context_set_pattern(random_pattern)
                        take_this_pattern = random_pattern
                    else:
                        take_this_pattern = pdb.gimp_context_get_pattern()
                        #debug(("L1141 take_this_pattern = ", take_this_pattern))

                    pdb.gimp_edit_bucket_fill_full(drawable, 2, 0, 100, 128, False, False, 0, x, y)
                    pdb.gimp_drawable_update(drawable,0,0,drawable.width,drawable.height)
                    pdb.gimp_displays_flush()
            pdb.gimp_selection_none(self.img)
 
        elif filltype == 'kacheln':
            available_pictures = gimp.image_list()
            tile_bilder = [el.name for el in available_pictures if el.name.startswith('tile')]
            if len(tile_bilder) < 1:
                gimp.message("Kacheln holen")
                #waar = "c:/Users/Peter/.gimp-2.8/patterns/"
                waar = gimp.directory + "\\patterns\\"
                num_patterns, pattern_list = pdb.gimp_patterns_get_list('^tile')
                #at PKHG 9 nov 2016: ('alpha-tile_1', 'alpha-tile_1 #1', 'tile_1', 'tile_2', 'tile_3', 'tile_4')
                gimp.message(str(pattern_list))
                chosen_names = pattern_list[:] #PKHG>TODO 5october 
                patnames = []
                for i in range(4):
                    patnames.append(chosen_names[i] + ".pat")
                doen = []
                for i in range(4):
                    doen.append(waar + patnames[i])
                pat_images = []
                for i in range(4):
                    pat_images.append(pdb.file_pat_load(doen[i],chosen_names[i] ))
                for i in range(4):
                    tmp = pdb.gimp_file_load(doen[i], chosen_names[i])
                    pdb.gimp_display_new(tmp)
                debug("L1171 kacheln als bilder geladen")
            else:
                debug("L1173 kacheln sind schon als bilder geladen")
            debug("L1174 Kacheln checken")
            waar = "c:/Users/Peter/.gimp-2.8/patterns/"
            num_patterns, pattern_list = pdb.gimp_patterns_get_list('tile')
            #on 9 nov by PKHG ('alpha-tile_1', 'alpha-tile_1 #1', 'tile_1', 'tile_2', 'tile_3', 'tile_4')
            chosen_names = pattern_list[2:] #PKHG>TODO 9october 
            debug(("L1179 Kacheln kacheln= ",chosen_names))
            drawable = self.img.layers[0]
            for x in vertical_guides:
                for y in horizontal_guides:
                    if x == drawable.width:
                        x = drawable.width - 1
                    if y == drawable.height:
                        y = drawable.height - 1
                    kreiseEllipse(self.img, x, y, w, h, operation= 2,
                                  chosen_form = ellipse_or_rectangle)
                    take_this_kachel = chosen_names[randint(0,len(chosen_names) - 1)]
                    pdb.gimp_context_set_pattern(take_this_kachel)
                    pdb.gimp_edit_bucket_fill_full(drawable, 2, 0, 100, 128, False, False, 0, x, y)

                    
                    pdb.gimp_drawable_update(drawable,0,0,drawable.width,drawable.height)
                    pdb.gimp_displays_flush()
                    
            pdb.gimp_selection_none(self.img)
                    

    def showDialog(self):
        self.dialog = gimpui.Dialog("Pygtk Menu", "rotdlg")
        self.dialog.set_position(gtk.WIN_POS_CENTER)
        self.table = gtk.Table(3, 1, False)
        self.table.set_homogeneous(False)
        #self.dialog.set_size_request(600,500)
        self.table.set_row_spacings(1)
        self.table.set_col_spacings(1)
        self.table.show()
        self.nB = gtk.Notebook()
        self.ui.addRows(self.nB, self.table, 0, 1, 0, 1)
        #DBG gdk titel layout gimp.message("L1211 Anzahl tabTits %2d" % (len(self.tabTits)))
        for n in range(0, len(self.tabTits)):
            if n < 4:
                t = gtk.Table(6, 2, False)
            elif n == 4:
                t = gtk.Table(2, 2, False)
                self.selected_items = []
                self.selected_items_shapes = []
                self.selected_items_patterns = []
                #frame = gtk.Frame("make your choices")
                #frame.show()
                #PKHG>25nov
                self.mydata_shapes = ['Arrow', 'Axis of symmetry', 'Binoculars',
                                          'Circle', 'Crescent', 'Cross',
                                          'Diagonals', 'Diamond', 'Dodecagon',
                                          'Ellipse', 'Flower 1 Out', 'Flower 2 In',
                                          'GEAR', 'Grid rectangular (c) Ofnuts v0.0', 'Start Grid==',
                                          'Mobius band', 'Octaagon', 'Pentagon',
                                          'Pentagram', 'Petal (butterfly)', 'Pie 1/2',
                                          'Pie 3/4 - 1/4', 'Pie 7/8 - 1/8', 'Playing cards Clubs',
                                          'Playing cards Diamonds', 'Playing cards Hearts', 'Playing cards Spades',
                                          'POLYGON', 'Protractor Inside circle', 'Start Protra',
                                          'Quadrant', 'Quatrefoil', 'Rectangle',
                                          'Recycle two arrows', 'Recycle three arrows', 'Roses compass',
                                          'Percentage Ruler', 'Semicircle', 'Square',
                                          'STAR', 'Star pentagons', 'Triangle equilateral',
                                          'Triangle isosceles', 'Triangle Reuleaux', 'Trefoil',
                                          'Yin-Yang', 'Wilber'] 
                

                num_patterns, self.mydata_pattern = pdb.gimp_patterns_get_list('')
                self.treestore = gtk.TreeStore(str)
                for parent in range(2):
                    if parent == 0:
                        piter = self.treestore.append(None, ['Patterns'])
                        for child in range(len(self.mydata_pattern)):
                            self.treestore.append(piter,[self.mydata_pattern[child]])
                    elif parent == 1 :
                        piter = self.treestore.append(None, ['Shapes'])
                        for child in range(len(self.mydata_shapes)):
                            self.treestore.append(piter,[self.mydata_shapes[child]])
                self.treeview = gtk.TreeView(self.treestore)
                self.tvcolumn = gtk.TreeViewColumn('Column 0')
                self.treeview.append_column(self.tvcolumn)
                # create a CellRendererText to render the data
                self.cell = gtk.CellRendererText()
                # add the cell to the tvcolumn and allow it to expand
                self.tvcolumn.pack_start(self.cell, True)
                # set the cell "text" attribute to column 0 - retrieve text
                # from that column in treestore
                self.tvcolumn.add_attribute(self.cell, 'text', 0)
                self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
                
                vbox = gtk.VBox(False,8) #PKHG>TODO what do this parameters mean?
                vbox.set_border_width(5)
                vbox.show()
                label = gtk.Label('Select ONE or SEVERAL items out of the following list:')
                label.show()
                vbox.pack_start(label, gtk.FALSE, gtk.FALSE)
                #PKHG>??? self.shape_or_pattern = self.ui.makeCombo([['pattern', 0],['shapes', 1]])
                #PKHG>??? vbox.pack_start(self.shape_or_pattern, gtk.FALSE, gtk.FALSE)
                sw = gtk.ScrolledWindow()
                sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
                sw.set_policy(gtk.POLICY_NEVER,
                              gtk.POLICY_AUTOMATIC)
                vbox.pack_start(sw)
                sw.add(self.treeview)
                #frame.add(vbox)
                
               
               
                #second_vbox = gtk.VBox("clear selections")
                clearbutton = gtk.Button("clear the selections done")
                clearbutton.connect("clicked", self.clear_selections)
                #clearbutton.show()
                vbox.pack_end(clearbutton, gtk.FALSE)
                #second_vbox.pack_end(clearbutton, gtk.FALSE)
                #second_vbox.show()
                button = gtk.Button('OK (simple shapes choices done?!)')
                #button.show()
                button.connect("clicked", self.ok_clicked)
                vbox.pack_end(button,gtk.FALSE)
                
                vbox.show_all()                
                t.attach(vbox, 0, 1, 0, 1)
 
            #PKHG>NOT Needed if table has 3rd paramger False t.set_homogeneous(False)
            if n == 3 or n == 4:
                t.set_row_spacings(0)
                t.set_col_spacings(1)
            else:
                t.set_row_spacings(1)
                t.set_col_spacings(2)
            t.show()
            self.tabs.append(t)
            self.nB.append_page(self.tabs[n], gtk.Label(self.tabTits[n]))
            #hier entstand self.tabs[guidelab_tab] und self.tabs[1] und self.tabs[2]
        
        self.tabOne()
                
        self.tabHelp(self.tabs[1])
        #self.tabHelp2(self.tabs[2])
        
        self.dialog.vbox.hbox1 = gtk.HBox(False, 1)
        self.dialog.vbox.hbox1.show()
        self.dialog.vbox.pack_start(self.dialog.vbox.hbox1, True, True, 1)
        self.dialog.vbox.hbox1.pack_start(self.table, True, True, 1)
                
        cancel_button = self.dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        cancel_button.connect("clicked", self.kobtn)
                
        self.dialog.connect("expose-event",self.expose)
        #self.dialog.show()
        self.dialog.set_keep_above(False)   #better not always on top
        #PKHG>??? not used? ssw,ssh=self.dialog.get_size()
        self.dialog.run()
    
    def expose(self,widget, otro):
        return
    
    def createGuides(self):
        self.range.connect('clicked',self.createGuides)
    
    def extraInfo(self,tit1,maxFloat,field=None):
        self.infoETit.set_text(tit1)
        if isinstance(maxFloat, str):
            self.infoE.set_text(maxFloat)
        else:
            self.infoE.set_text('%.2f'%(maxFloat))

    def kobtn(self, widget):
        return 0

class AraknelabExtra(gimpplugin.plugin):
    def start(self):
        gimp.main(self.init, self.quit, self.query, self._run)
    def init(self):
        pass
    def quit(self):
        pass
    def query(self):
        cright = "PeterPKHG (guideslab from: jfgarcia)"
        date = "09November2016"
        plug_descr = ("paint with guidelab")
        plug_params = [(PDB_INT32, "run_mode", "Run mode"), (PDB_IMAGE, "image", "Input image"),]
        gimp.install_procedure("guidelabextrainstall", plug_descr, plug_descr, "PeterPKHG(orig guid-lab:jfgarcia)", cright, date, "<Image>/Image/Guides/paint with guidelab", "RGB*, GRAY*", PLUGIN, plug_params,[])

    def guidelabextrainstall(self, runmode, img):
        Guidelabextra(runmode, img)
        

if __name__ == '__main__':
    AraknelabExtra().start()



"""
Command: last-kbd-macro
Key: none

Macro:

ESC
C-s			;; isearch-forward
L[0-9]+			;; self-insert-command * 7
RET			;; newline
ESC
:(insert		;; self-insert-command * 8
SPC			;; self-insert-command
(what-line))		;; self-insert-command * 12
RET			;; newline
C-r			;; isearch-backward
L			;; self-insert-command
C-r			;; isearch-backward
RET			;; newline
ESC
d			;; self-insert-command
C-d			;; delete-char
L			;; self-insert-command


(fset 'renumberLlabels
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ([escape 19 76 91 48 45 57 93 43 return escape 58 40 105 110 115 101 114 116 32 42 119 104 97 116 45 108 105 110 101 41 backspace backspace backspace backspace backspace backspace backspace backspace backspace backspace backspace 40 119 104 97 116 45 108 105 110 101 41 41 return 18 76 18 return escape 100 4 76] 0 "%d")) arg)))

"""
