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
import gimp
import gimpplugin
from gimpenums import *
pdb = gimp.pdb
import gtk
import gimpui
import _gimpui
import os
import sys
sys.path.append(gimp.directory + "\\python_gtk")
print(sys.path[-1])
from time import time
from random import random
from random import randint
#global???!!!
pattern_available = False
no_debug_output = False
def random_rgb():
    return(randint(0,255), randint(0,255), randint(0,255))
    ##return( (int(random() * 256), int(random() * 256), int(random() * 256)))

##########drawUi.py start
def newline(x1,y1,x2,y2):
    return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2]

def kreiseEllipse(image, mx, my, w, h, chan = 0, chosen_form = 'ellipse'):
    debug(("L41 kreiseEllipse called",chosen_form))
    x = mx - w / 2
    y = my - h / 2
    if chosen_form == 'ellipse':
        pdb.gimp_image_select_ellipse(image, chan, x, y, w, h)
    else:
        pdb.gimp_image_select_rectangle(image, chan, x, y, w, h)
        

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

def debug(val):
    global no_debug_output
    if no_debug_output:
        return
    gimp.message(str(val))

def debugErr(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    debug(fname+'\n'+str(exc_tb.tb_lineno)+'\n'+str(e))

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
    tabTits = [('Add/Edit'),('Help guide lab'),('Help guides_to_path'),('Simple Path centured'),('Waehle Kacheln')] #PKHG help added
    tipPos = ("Position of the current guide, double click on the value to edit")
    tipPrev = ("Distance between this guide and the previous. If this guide is the 1st then this will be the distance to the start of the image.")
    tipNext=("Distance between this guide and the next. If this guide is the last then this will be distance to the end of the image.")
    tipDel=("Double click to delete the current guide.")
    newGuideTip=("Write the position for the new guide\nLook what operations and replacements you can use in the help tab")
    
    def __init__(self, runmode, img):
        self.img = img
        self.image_start_name = img.name
        debug(("L62 __init__ called", self.image_start_name))  
        #self_starting_img = self.img
        #debug(("L160 *********** __init__",self.img,self_starting_img))
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
#### test bucketfill

    def testproc(self,  *data):
        debug(("L185 testproc",data))
        

    def fillbucket(self, teller, kachel, drawable, x, y, fill_mode = 0, paint_mode = 0, opacity = 100,
                   threshold = 128, sample_merged = False, fill_transparent = False,
                   select_criterion = 0, color = (255,0,0)):
        debug(("L175 fillbucket called,x,y,tel fill_mode  " , x, y, teller, fill_mode, kachel))
        
        if opacity > 100:
            opacity = 100
        if fill_mode == 2:
            num_patterns, pattern_list = pdb.gimp_patterns_get_list('^tile')
            debug(("L180 fillpattern pattenr name", kachel))
            if kachel <> 'random':
                pdb.gimp_context_set_pattern(kachel)
                pdb.gimp_patterns_refresh()
            else:
                fill_mode = 0 #for foreground color!
            debug(("L178 fillbucker pattern_name", kachel))
        elif fill_mode == 999: #use pattern!
            fill_mode = 2
            pdb.gimp_context_set_pattern(kachel)
            pdb.gimp_patterns_refresh()
            debug(("L188 fillbucker pattern_name", kachel))
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
        debug(("L220 data in create_simple_pathes"  , data ))
        horizontal_guides = []
        for n in self.tsH:
            horizontal_guides.append((n[0]))
        vertical_guides = []
        for n in self.tsV:
            vertical_guides.append(n[0])
        number_of_intersections = len(horizontal_guides) * len(vertical_guides)
        if number_of_intersections == 0:
            show_my_message("No intersections of guides available! Try again ;-) ")
            return
        ellipse_or_rectangle = self.ellipse_or_rectangle.get_active()
        #PKHG>TODO10oct
        w = self.widthSpinButton.get_value()
        h = self.heightSpinButton.get_value()
        #debug(("L229 h w",(h,w)))

        #self.pathoptions.set_active(25)
        s = self.pathoptions.get_active() #this is the simple shape chosen!
        no_pattern_list = [1, 6, 13, 14, 36]  #36 is Percentage Ruler, not fillable!
        if s in no_pattern_list:
            s = 25
            
        pattern_fill = self.inselection_q.get_active()
        #debug(("L233 def create_simple_pathes L230 s, pattern_fill", s, pattern_fill))
        drawable = self.img.layers[0]
        #random_or_not = self.pattern_checkyn.get_active()
        random_simple_shape = self.random_simple_shape.get_active()
        random_simple_pattern = self.random_simple_pattern.get_active()
        debug(("L243 random_simple shape pattern", random_simple_shape, random_simple_pattern))
        num_patterns, pattern_list = pdb.gimp_patterns_get_list('')
        count_shapes = 0 #randint(0,46)
        pattern_fill_choice = self.fill_q.get_active()
        flatten_choice = self.flatten_image_q.get_active()
        #debug(("L847 flatten_choice", flatten_choice))
        
        for x in vertical_guides:
            for y in horizontal_guides:
                if x == drawable.width:
                    x = drawable.width - 1
                if y == drawable.height:
                    y = drawable.height - 1
                kreiseEllipse(self.img, x, y, w, h, chan = 2,
                                  chosen_form = ellipse_or_rectangle)
                if random_simple_pattern:
                    #pattern_list = pattern_list[]
                    random_pattern = pattern_list[randint(0, num_patterns - 1)]
                    debug(("L247 random pattern is ",len(pattern_list) == num_patterns, random_pattern))
                    pdb.gimp_context_set_pattern(random_pattern)
                    take_this_pattern = random_pattern
                    #self.pathoptions.set_active(count_shapes)
                    #count_shapes = (1 + count_shapes) % 47
                
                else:
                    take_this_pattern = pdb.gimp_context_get_pattern()
                    debug(("L252 take_this_pattern = ", take_this_pattern))

                if random_simple_shape:
                    count_shapes = randint(0,46)
                    self.pathoptions.set_active(count_shapes)
                    #count_shapes = pattern_list[randint(0,46)] #(1 + count_shapes) % 47

                s = self.pathoptions.get_active() #this is the simple shape chosen!
                if s in no_pattern_list:
                    s = 25

                
                #>> pdb.python_fu_plugin_simple_shapes_centered(image, drawable, sel (int in selection?),
                #s = int which type of vectors,
                #resize_1, R, L, T, B, resize_2, M_L, H_L, V_L, R_L, fill, fillpattern, stroke, strokecolor, strokewidth)
                #PKHG>TODO M_L till R_L
                #stroke  using svg or not now 0
                #>>version 11-11 > pdb.python_fu_MareoQplugin_simple_shapes_centered(image,
                #drawable, sel, s, resize_1, M_L, H_L, V_L, R_L, fill, fillpattern,
                #H_B, V_B, stroke, strokecolor, strokewidth)


                debug(("266 s = ", s))
                
                pdb.python_fu_plugin_simple_shapes_centered(self.img, drawable, True,s,
                                                    False,0,0,0,0,False,10,10,10,10, pattern_fill_choice,
                                                    take_this_pattern, 0, (255,0,0), 10)
                if flatten_choice:
                    drawable = pdb.gimp_image_flatten(self.img) #Flatten wohl oder nicht PKHG>TODO
                    
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
            "\t"+("For add a guide at 10 pixels of the bottom:")+"<span foreground='blue' background='white'> <tt>H-10</tt></span>",
            "\t"+("For add a guide at 10 pixels of the center")+":<span foreground='blue' background='white'>  <tt>height/2+10</tt></span>"
        ]
        tx=""
        for line in msgs:
                tx+=line+"\n"
                lb=self.ui.addRows(self.ui.addLabel(tx,0,0),tab, 2, 4, row, row+1)
                lb.set_use_markup(True)
                
    def test_message(self, widget):
        if widget.get_name() == "test_button":
            self.show_my_message(widget.get_label()) #"Test button clicked")
            
    def tabHelp2(self, tab):
        """
        Content of third tab, help guides and strokes
        """
        msg2 = [("pushing the button <b>create_the_path</b> creates a path") ,
                ("you may stroke an available path with pencil and background-color"),
                ("you may opt for deleting the the active vextors") +"\n",
                ("<span foreground='blue' background='white'>You may have a selection active, then only guides INSIDE </span>"),
                ("<span foreground='blue' background='white'>will be used for a new path.</span>"),
            ]
        row = 0
        tx = ""        
        for line in msg2:
            tx += line + "\n"
            lb = self.ui.addRows(self.ui.addLabel(tx, 0, 0), tab, 5, 7, row, row + 1)
            lb.set_use_markup(True)
        
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
        gimp.message("L448" + str(data))
        pdb.gimp_context_set_pattern(data[0]) #PKHG>Name of chosen pattern
        
    def call_plugin(self, widget):
        name = widget.get_name()
        image = gimp.image_list()[0]
        self.activeornot = self.checkynGUI.get_active()
        self.dialog.set_keep_above(self.activeornot)
            
        if name == "create_the_path":
            layer = image.layers[0]
            self.python_guides_to_path_pkhg(image, layer)
        elif name == "create_new_layer":
            #debug("L491 TODO add new layer")
            layer_new = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 1, 'new layer', 100, 0)
            pdb.gimp_image_add_layer(self.img, layer_new, 0)
        elif name == "fill_q":
            gimp.message("TODO activate fill_q")
        elif name == "pattern_select_button":
            gimp.message("L458 name = " + name)
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
            self.ui.addRows(self.ui.addLabel(('H \nO\nR\nI\nZ\nO\nN\nT\nA\nL')), self.tabs[0], 0, 1, row, row+1)
            self.ui.addRows(self.ui.addLabel(('V \nE\nR\nT\nI\nC\nA\nL')), self.tabs[0], 5, 6, row, row+1)

            self.tsH,tvh,sWh=self.addTV('h')
            self.tsV,tvv,sWv=self.addTV('v')
            self.ui.addRows(sWh, self.tabs[0], 1, 5, row, row+1)
            self.ui.addRows(sWv, self.tabs[0], 6, 10, row, row+1)
            row += 1
            #newAt=('New guide at')
            newAt=('Guide ')
            addOpposite=("Add an aditional guide on the oposite side")
            # horizontal
            self.ui.addRows(self.ui.addLabel(newAt), self.tabs[0], 1, 2, row, row+1)
            self.newH=self.ui.addRows(gtk.SpinButton(gtk.Adjustment(0, 0, self.img.height, 1), 0.0, 0), self.tabs[0], 2, 3, row, row+1,"activate",self.evalSpin)
            self.newH.connect("focus-out-event",self.tt)
            self.newHunit=self.ui.addRows(self.ui.makeCombo([['px',0],['%',1]]), self.tabs[0], 3, 4, row, row+1)
            self.ui.addTip(self.newH, self.newGuideTip)

            self.ui.addRows(self.ui.addLabel("Replicate "), self.tabs[0], 1, 2, row+1, row+2)
            CORNERS=[[('None'),0],[('Mirror'),1],[('Perimeter'),2]]
            self.cbH=self.ui.addRows(self.ui.makeCombo(CORNERS), self.tabs[0], 2, 4, row+1, row+2)
            self.newHB=self.ui.addRows(gtk.Button('','Add'), self.tabs[0], 4, 5, row, row+2,"clicked",self.addH)

            self.ui.addRows(self.ui.addLabel(newAt), self.tabs[0], 6, 7, row, row+1)
            self.newV=self.ui.addRows(gtk.SpinButton(gtk.Adjustment(0,0,self.img.width,1),0.0,0), self.tabs[0], 7, 8, row, row+1,"activate",self.evalSpin)
            self.newV.connect("focus-out-event",self.tt)
            self.newVunit=self.ui.addRows(self.ui.makeCombo([['px',0],['%',1],['aaa',2]]), self.tabs[0], 8, 9, row, row+1)

            self.ui.addRows(self.ui.addLabel("Replicate "), self.tabs[0], 6, 7, row+1, row+2)
            CORNERS=[[('None'),0],[('Mirror'),1],[('Perimeter'),2]]
            self.cbV=self.ui.addRows(self.ui.makeCombo(CORNERS), self.tabs[0], 7, 9, row+1, row+2)
            
            self.newVB=self.ui.addRows(gtk.Button('',gtk.STOCK_ADD), self.tabs[0], 9, 10, row, row+2,"clicked",self.addV)
            row += 1
            self.getGuides()
            row += 1
            self.refresh=self.ui.addRows(gtk.Button(('Update manual changes')), self.tabs[0], 1, 5, row, row+1,'clicked',self.getGuides)
            self.refresh=self.ui.addRows(gtk.Button(('Delete all guides')), self.tabs[0], 6, 10, row, row+1,'clicked',self.delGuides)
            self.refresh.connect('clicked',self.getGuides)
            row += 1
            infoSeveral = gtk.Label("several guides")
            self.ui.addRows(infoSeveral, self.tabs[0], 0, 1, row, row + 1)

            self.ui.addRows(gtk.Label("start"), self.tabs[0], 1, 2, row, row + 1)
            self.startSpinButton = gtk.SpinButton(gtk.Adjustment(125, 0, self.img.width, 1), 0.0, 0)
            self.startSpinButton.set_name('start')
            r01 = self.ui.addRows(self.startSpinButton, self.tabs[0], 2, 3, row, row+1,"activate", self.evalSpin)
            self.ui.addRows(gtk.Label("step"), self.tabs[0], 3, 4, row, row + 1)
            self.stepSpinButton = gtk.SpinButton(gtk.Adjustment(250, 1, self.img.width, 1), 0.0, 0)
            self.stepSpinButton.set_name('step')
            r02 = self.ui.addRows(self.stepSpinButton, self.tabs[0], 4, 5, row, row + 1,"activate", self.evalSpin)
            self.ui.addRows(gtk.Label("amount"), self.tabs[0], 5, 6, row, row + 1)
            self.amountSpinButton = gtk.SpinButton(gtk.Adjustment(2, 1, self.img.width, 1), 0.0, 0)
            self.amountSpinButton.set_name('amount')
            self.r03 = self.ui.addRows(self.amountSpinButton, self.tabs[0], 6, 7, row, row + 1,"activate", self.evalSpin)
            self.orientation = self.ui.addRows(self.ui.makeCombo([['horizontal',0],['vertical',1]]), self.tabs[0], 7, 8, row, row + 1)          
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
            self.refresh = self.ui.addRows(self.severalGuides, self.tabs[0], 8, 9,
                                           row, row + 1, 'clicked' , self.call_plugin)
            row += 1
            self.thisWindowOnTop = gtk.Label("This Gui always on Top?")
            self.thisWindowOnTop.set_name("Gui_on_top")
            self.refresh = self.ui.addRows(self.thisWindowOnTop, self.tabs[0], 0, 2,
                                           row, row + 1)# 'clicked' , self.call_plugin)
            self.checkynGUI = gtk.CheckButton("y/n")
            self.ui.addRows(self.checkynGUI, self.tabs[0], 2,3, row, row + 1, 'clicked', self.call_plugin)

            self.ui.addRows(gtk.Label("-------------------------------------"), self.tabs[0], 3, 10, row, row + 1)            

            row += 1
            self.wishGuides = gtk.Button("create_the_path")
            self.wishGuides.set_name("create_the_path")
            self.refresh = self.ui.addRows(self.wishGuides, self.tabs[0], 1, 5,
                                           row, row + 1, 'clicked' , self.call_plugin)
            self.removeLabel = gtk.Label("remove vector")
            self.checkyn = gtk.CheckButton("y/n")
            self.ui.addRows(self.removeLabel, self.tabs[0], 6, 7, row, row + 1)
            self.ui.addRows(self.checkyn, self.tabs[0], 7, 8, row, row + 1, 'clicked', self.call_plugin)
            self.strokeGuides = gtk.Button("stroke active Vector") 
            self.strokeGuides.set_name("stroke_guides")
            self.refresh = self.ui.addRows(self.strokeGuides, self.tabs[0], 8, 9,
                                           row, row + 1, 'clicked' , self.call_plugin)
            row += 1
            self.newLabel = gtk.Label("Prepare width and height of selections, for intersection points, if wanted")
            self.ui.addRows(self.newLabel, self.tabs[0], 0, 5, row, row + 1 )
            row +=1
            self.ui.addRows(gtk.Label("set width"), self.tabs[0], 0, 1, row, row + 1)
            self.widthSpinButton = gtk.SpinButton(gtk.Adjustment(250, 2, self.img.width, 1), 0.0, 0)
            self.widthSpinButton.set_name('widthEllipse')
            r1 = self.ui.addRows(self.widthSpinButton, self.tabs[0], 1, 2, row, row+1,"activate", self.evalSpin)
            self.ui.addRows(gtk.Label("set height"), self.tabs[0], 2, 3, row, row + 1)
            self.heightSpinButton = gtk.SpinButton(gtk.Adjustment(250, 2, self.img.height, 1), 0.0, 0)
            self.heightSpinButton.set_name('heightEllipse')
            r2 = self.ui.addRows(self.heightSpinButton, self.tabs[0], 3, 4, row, row + 1,"activate", self.evalSpin)
            self.ellipse_or_rectangle = self.ui.addRows(self.ui.makeCombo([['ellipse',0],['rectangle',1]]), self.tabs[0], 4, 5, row, row + 1)
            
            ellipseButton = gtk.Button("selection(s) at intersection(s)")
            self.ui.addRows(ellipseButton, self.tabs[0], 5, 7  , row, row + 1, 'clicked', self.createellipses)

            row += 1
            self.ui.addRows(gtk.Label("fill selections?!"), self.tabs[0], 0, 1, row, row + 1)
            self.filltype = self.ui.addRows(self.ui.makeCombo([['no',0],['fg color',1],['centercolor',2],['pattern',3],['kacheln',4]]), self.tabs[0], 1, 2, row, row + 1)
            self.ui.addRows(gtk.Label("opacity fill-bucket?!"), self.tabs[0], 2, 3, row, row + 1)
            self.opacityforbucket = gtk.SpinButton(gtk.Adjustment(100, 0, 100, 5), 0.0, 0)
            self.widthSpinButton.set_name('opacityforbucket')
            r1 = self.ui.addRows(self.opacityforbucket, self.tabs[0], 3, 4, row, row+1,"activate", self.evalSpin)
            self.ui.addRows(gtk.Label("random col. or pat.?!"), self.tabs[0], 4, 5, row, row + 1)
            self.pattern_checkyn = gtk.CheckButton("y/n")
            self.ui.addRows(self.pattern_checkyn, self.tabs[0], 5, 6, row, row + 1, 'clicked', self.call_plugin)
            
            row += 1
            self.ui.addRows(gtk.Label("New layer"), self.tabs[0], 0, 1, row, row + 1)
            self.new_layer = gtk.Button("OK: do now!")
            self.new_layer.set_name("create_new_layer")
            self.ui.addRows(self.new_layer, self.tabs[0], 1, 2 , row, row + 1, 'clicked', self.call_plugin)

            #PKHG>Simple path layout
            row = 0
            self.ui.addRows(gtk.Label("Parameters of Use for 'Simple paths centured' 1.0 beta "), self.tabs[3], 1, 4, row, row + 1)
            row += 1
            self.ui.addRows(gtk.Label("choose:"), self.tabs[3], 0, 1, row, row + 1)
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
]),self.tabs[3], 1, 2, row, row + 1)

            #not with pattern no_pattern_list = [1, 6, 13, 14, 36]
            self.ui.addRows(gtk.Label("In selection?"), self.tabs[3], 2, 3, row, row + 1)
            self.inselection_q = gtk.CheckButton("y/n")
            self.ui.addRows(self.inselection_q, self.tabs[3], 3, 4, row, row + 1, 'clicked', self.call_plugin)

            row += 1
            self.ui.addRows(gtk.Label("Resize layer?"), self.tabs[3], 0, 1, row, row + 1)
            self.resize_q = gtk.CheckButton("y/n")
            self.ui.addRows(self.resize_q, self.tabs[3], 1, 2, row, row + 1, 'clicked', self.call_plugin)
            self.ui.addRows(gtk.Label("Resize all layers to image size?"), self.tabs[3], 2, 3, row, row + 1)
            self.resize_all_q = gtk.CheckButton("y/n")
            self.ui.addRows(self.resize_all_q, self.tabs[3], 3, 4, row, row + 1, 'clicked', self.call_plugin)
            
            row += 1
            self.ui.addRows(gtk.Label("from right (pix)"), self.tabs[3], 0, 1, row, row + 1)
            self.ui.addRows(gtk.Label("from left (pix)"), self.tabs[3], 1, 2, row, row + 1)
            self.ui.addRows(gtk.Label("from top (pix)"), self.tabs[3], 2, 3, row, row + 1)
            self.ui.addRows(gtk.Label("from bottom (pix)"), self.tabs[3], 3, 4, row, row + 1)
            row += 1
            self.resize_left = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_left.set_name('resize_left')
            r1 = self.ui.addRows(self.resize_left, self.tabs[3], 0, 1, row, row+1,"activate", self.evalSpin)
            self.resize_right = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_right.set_name('resize_right')
            r1 = self.ui.addRows(self.resize_right, self.tabs[3], 1, 2, row, row+1,"activate", self.evalSpin)
            self.resize_top = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_top.set_name('resize_top')
            r1 = self.ui.addRows(self.resize_top, self.tabs[3], 2, 3, row, row+1,"activate", self.evalSpin)
            self.resize_bottom = gtk.SpinButton(gtk.Adjustment(10, -100, 100, 5), 0.0, 0)
            self.resize_bottom.set_name('resize_bottom')
            r1 = self.ui.addRows(self.resize_bottom, self.tabs[3], 3, 4, row, row+1,"activate", self.evalSpin)
            row += 1  #gimpui ... for 
            #self.pattern_select  = self.ui.addRows(self.PatternSelector, self.tabs[3], 0, 1, row, row + 1)
            #self.ui.addRows(gtk.Label("pattern fill?"), self.tabs[3], 0, 1, row, row + 1)
            self.flatten_image_q = gtk.CheckButton("FLATTEN image?")
            self.ui.addRows(self.flatten_image_q, self.tabs[3], 0, 1, row, row + 1)
            self.fill_q = gtk.CheckButton("pattern fill?")
            self.fill_q.set_name("fill_q")
            self.ui.addRows(self.fill_q, self.tabs[3], 1, 2, row, row + 1)
            #PKHG>no general OK!!, 'clicked', self.call_plugin)
            self.pattern_select_button = _gimpui.PatternSelectButton()
            #PKHG>works ;-) gimp.message(str(dir(self.pattern_select_button)))
            self.rpattern = self.ui.addRows(self.pattern_select_button, self.tabs[3], 2, 3,
                                            row, row + 1,"pattern_set", self.pattern_def)
            row += 1
            self.random_simple_shape = gtk.CheckButton("random Simple shape?")
            self.ui.addRows(self.random_simple_shape, self.tabs[3], 0, 1, row, row + 1)
            self.random_simple_pattern = gtk.CheckButton("random pattern for Simple shape?")
            self.ui.addRows(self.random_simple_pattern, self.tabs[3], 1, 2, row, row + 1)

            row += 1 
            final_simple_path_centered = gtk.Button("OK: do now!")
            self.ui.addRows(final_simple_path_centered, self.tabs[3], 0, 4 , row, row + 1, 'clicked', self.create_simple_pathes) 

################# please change here ##################
            row = 0
            test4 = 4
            num_patterns, mydata = pdb.gimp_patterns_get_list('')
            kanweg1 = gtk.Label(" label 1148 16 nov ")
            test01 = self.ui.addRows(kanweg1, self.tabs[test4], 0, 1 , row, row + 1)
            row += 1


################# end test tile for treeview #######################
        except Exception,e:
            debug(e)

    def createellipses(self, widget):
        global horizontal_guides, vertical_guides
        
        self.img = gimp.image_list()[-1]
        debug("L791 createellipses called")
        horizontal_guides = []
        for n in self.tsH:
            horizontal_guides.append((n[0]))
        vertical_guides = []
        for n in self.tsV:
            vertical_guides.append(n[0])
        number_of_intersections = len(horizontal_guides) * len(vertical_guides)
        ellipse_or_rectangle = self.ellipse_or_rectangle.get_active()
        if ellipse_or_rectangle == 0:
            ellipse_or_rectangle = 'ellipse'
        else:
            ellipse_or_rectangle = 'rectangle'
            debug(("L801 ellipse_or_rectangle ", ellipse_or_rectangle))
        #debug((vertical_guides, horizontal_guides))
        if number_of_intersections == 0:
            self.show_my_message("no guide-intersection yet available")
            return
        #PKHG>premature end of this def, if no intersections available ;-( !!
        ftypes = ['no', 'fg color', 'centercolor', 'pattern', 'kacheln'] #PKHG>31oct pay attention!
        tmp = self.filltype.get_active()
        debug(("L816 active filltype" , tmp))      
        filltype = ftypes[int(self.filltype.get_active())]
        debug(("L815 filltype werd ", filltype))
        w = self.widthSpinButton.get_value()
        h = self.heightSpinButton.get_value()
        if filltype == 'no':
            for x in vertical_guides:
                for y in horizontal_guides:
                    kreiseEllipse(self.img, x, y, w, h, chan = 0, chosen_form = ellipse_or_rectangle)
            #return
        elif filltype == 'fg color' or filltype == 'centercolor':
            drawable = self.img.layers[0]
            random_chosen = self.pattern_checkyn.get_active() #not good: self.fill_q.get_active()
            debug(("L826 filltype random_chosen", filltype, random_chosen))            
            for x in vertical_guides:
                for y in horizontal_guides:
                    if x == drawable.width:
                        x = drawable.width - 1
                    if y == drawable.height:
                        y = drawable.height - 1
                        
                    kreiseEllipse(self.img, x, y, w, h, chan = 2,
                                  chosen_form = ellipse_or_rectangle)
                    if filltype == 'centercolor':
                        #PKHH>orig num_channels, color = pdb.gimp_drawable_get_pixel(drawable, x, y)
                        num_channels, color = pdb.gimp_drawable_get_pixel(self.img.layers[-1], x, y)
                        #debug(("center color",color," tel",tel))
                        debug(("L840 x y = centercolor",x,y, color))
                    else:
                        debug(("L842 no center_color",random_chosen))
                        if random_chosen:
                            color = random_rgb()
                        else:
                            color = pdb.gimp_context_get_foreground()
                    debug(("L845 random or not filltype",random_chosen,filltype))
                    pdb.gimp_context_set_foreground(color)
                    debug(("L831 color=", color))
                    #pdb.gimp_edit_bucket_fill_full(drawable, fill_mode = 0 =foregroundcolor,
                    #paint_mode, opacity, threshold, sample_merged, fill_transparent, select_criterion, x, )
                    pdb.gimp_edit_bucket_fill_full(drawable, 0, 0, 100, 128, False, False, 0, x, y)
                    debug(("L822 random colors"))
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
                    kreiseEllipse(self.img, x, y, w, h, chan = 2,
                                  chosen_form = ellipse_or_rectangle)
                    #pdb.gimp_edit_bucket_fill_full(drawable, fill_mode = 0 =foregroundcolor,
                    #paint_mode, opacity, threshold, sample_merged, fill_transparent, select_criterion, x, y)
                    debug(("941 install pattern"))
                    if random_or_not:
                        #pattern_list = pattern_list[]
                        random_pattern = pattern_list[randint(0, num_patterns - 1)]
                        debug(("L867 random pattern is ",len(pattern_list) == num_patterns, random_pattern))
                        pdb.gimp_context_set_pattern(random_pattern)
                        take_this_pattern = random_pattern
                    else:
                        take_this_pattern = pdb.gimp_context_get_pattern()
                        #debug(("L872 take_this_pattern = ", take_this_pattern))

                    pdb.gimp_edit_bucket_fill_full(drawable, 2, 0, 100, 128, False, False, 0, x, y)
                    pdb.gimp_drawable_update(drawable,0,0,drawable.width,drawable.height)
                    pdb.gimp_displays_flush()
            pdb.gimp_selection_none(self.img)
            #return
            #TODO
            #return
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
                debug("L837 kacheln als bilder geladen")
            else:
                debug("L820 kacheln sind schon als bilder geladen")
            debug("L894 Kacheln checken")
            waar = "c:/Users/Peter/.gimp-2.8/patterns/"
            num_patterns, pattern_list = pdb.gimp_patterns_get_list('tile')
            #on 9 nov by PKHG ('alpha-tile_1', 'alpha-tile_1 #1', 'tile_1', 'tile_2', 'tile_3', 'tile_4')
            chosen_names = pattern_list[2:] #PKHG>TODO 9october 
            debug(("L910 Kacheln kacheln= ",chosen_names))
            drawable = self.img.layers[0]
            for x in vertical_guides:
                for y in horizontal_guides:
                    if x == drawable.width:
                        x = drawable.width - 1
                    if y == drawable.height:
                        y = drawable.height - 1
                    kreiseEllipse(self.img, x, y, w, h, chan = 2,
                                  chosen_form = ellipse_or_rectangle)
                    take_this_kachel = chosen_names[randint(0,len(chosen_names) - 1)]
                    pdb.gimp_context_set_pattern(take_this_kachel)
                    pdb.gimp_edit_bucket_fill_full(drawable, 2, 0, 100, 128, False, False, 0, x, y)

                    
                    pdb.gimp_drawable_update(drawable,0,0,drawable.width,drawable.height)
                    pdb.gimp_displays_flush()
                    
            pdb.gimp_selection_none(self.img)
                    

    def showDialog(self):
        self.dialog = gimpui.Dialog("PTK Übung", "rotdlg")
        self.dialog.set_position(gtk.WIN_POS_CENTER)
        self.table = gtk.Table(3, 1, False)
        self.table.set_homogeneous(False)
        #self.dialog.set_size_request(600,500)
        self.table.set_row_spacings(1)
        self.table.set_col_spacings(1)
        self.table.show()
        self.nB = gtk.Notebook()
        self.ui.addRows(self.nB, self.table, 0, 1, 0, 1)
        #DBG gdk titel layout gimp.message("L408 Anzahl tabTits %2d" % (len(self.tabTits)))
        for n in range(0, len(self.tabTits)):
            if n < 3:
                t = gtk.Table(6, 2, False)
            else:
                t = gtk.Table(7, 4, False)
            t.set_homogeneous(False)
            if n == 3 or n == 4:
                t.set_row_spacings(0)
                t.set_col_spacings(1)
            else:
                t.set_row_spacings(1)
                t.set_col_spacings(2)
            t.show()
            self.tabs.append(t)
            self.nB.append_page(self.tabs[n], gtk.Label(self.tabTits[n]))
            #hier entstand self.tabs[0] und self.tabs[1] und self.tabs[2]
        
        self.tabOne()
                
        self.tabHelp(self.tabs[1])
        self.tabHelp2(self.tabs[2])
        
        self.dialog.vbox.hbox1 = gtk.HBox(False, 1)
        self.dialog.vbox.hbox1.show()
        self.dialog.vbox.pack_start(self.dialog.vbox.hbox1, True, True, 1)
        self.dialog.vbox.hbox1.pack_start(self.table, True, True, 1)
                
        cancel_button = self.dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        cancel_button.connect("clicked", self.kobtn)
                
        self.dialog.connect("expose-event",self.expose)
        self.dialog.show()
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



