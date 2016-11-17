#http://mailman.daa.com.au/cgi-bin/pipermail/pygtk/2003-February/004454.html
import gobject
import gtk
COLUMN_TEXT=0
# initialize the ListStore.  Fom more complicated lists, see pygtk src example
# pygtk-demo/demos/list_store.py
#ORiGinal mydata = ['John', 'Miriam', 'Rahel', 'Ava', 'Baerbel']
num_patterns, mydata = pdb.gimp_patterns_get_list('')

model = gtk.ListStore(gobject.TYPE_STRING)
for item in mydata:
    iter = model.append()    
    model.set(iter, COLUMN_TEXT, item)
# set up the treeview to do multiple selection
#PKHG>INFO neline needed for Gimp Python Console

treeview = gtk.TreeView(model)
treeview.set_rules_hint(gtk.TRUE)    
column = gtk.TreeViewColumn('Name', gtk.CellRendererText(),
                            text=COLUMN_TEXT)
treeview.append_column(column)
treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
# when you click ok, call this function for each selected item
def foreach(model, path, iter, selected):
    selected.append(model.get_value(iter, COLUMN_TEXT))

def ok_clicked(event):
    selected = []
    treeview.get_selection().selected_foreach(foreach, selected)
    print 'And the winners are...', selected
    #gtk.main_quit()

def endme_clicked(event):
    gtk.main_quit()


# the rest is just window boilerplate
win = gtk.Window()
win.connect('destroy', lambda win: gtk.main_quit())
win.set_title('GtkListStore demo')
win.set_border_width(8)
vbox = gtk.VBox(gtk.FALSE, 8)
win.add(vbox)

label = gtk.Label('Select your firends and family')
vbox.pack_start(label, gtk.FALSE, gtk.FALSE)

sw = gtk.ScrolledWindow()
sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
sw.set_policy(gtk.POLICY_NEVER,
              gtk.POLICY_AUTOMATIC)
vbox.pack_start(sw)
sw.add(treeview)
win.set_default_size(280, 250)


endme = gtk.Button("END")
endme.show()
endme.connect("clicked",endme_clicked)
vbox.pack_end(endme)  #PKHG>????

button = gtk.Button('OK')
button.show()
button.connect("clicked", ok_clicked )
vbox.pack_end(button,gtk.FALSE)
    
win.show_all()
gtk.main()
	   
