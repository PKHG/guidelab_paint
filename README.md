# Gimp window as checker bord (Dammen-bord) 
You need dammenblack.pat, dammenwhite.pat (put them in you local pattern directory from Gimp)
the Startpage (*.xcf) an empty bord but with the numbering (for starters ;-) )
the plugin: Dam28oct2019.py the plugin (put in into the Gimp readable plug-ins directory)

After loading the startpage (xcf for Gimp) there shoul be a TAB: GTK ==> TEST ==> Dam30oct19 
stat will start the GTK checker interface.
First of all activate the setup-mode an ad black stones (click black) inputline 1-20 and insert
white (click white) 31-50 in the input line and insert

That should deliver a standard checker bord filled with all stones

Now goto game-mode and and find out if I made all things ok or if errors, let me know!

Look in the Dam*.py which directories you may have to create to use save pictures resp. save
your moves ..
## More explanations will be made ...

# guidelab_paint
A repository for my guidelab extended with paint methods
Reason: the very nice Arakne guidelab was for me not complete: missed to create several guides at once.
Next: a wish at gimpchat was to make vectors inside a selections on the included guides, I created a bit different way 
linear in timeconsumtion with respect to number of guides.

Got the idea to use intersections of guides to do some 'painting', because changing guides is so easy to use
the guidelab.
Realized: elliptic or rectangle selections: pure, or painted with colors, patterns or ... either one or random.

Next: intruiged by the Pygtk Menu I tried to learn about it and used it for tests to to make better UI of my
additions. Espescially needed: get several selections out of a list, e.g. patternlist.

MareroQ (gimpchat) created a plugin "Simple path shapes" , which is used to 'paint' at the intersectionpoints 
of guides, one type or random. Needs too a selection of them, e.g. playing-cards only (clubs, hearts, spades, diamonds)

So I need help from people knowing to use Pygtk in gimp ... ;-) 

In my newest Version , after a week trial and error, a lot of things became clear: e.g. how to select several
items of a list at once ...
Layout of the UI is and will be changed.

On the way ... 22 nov 2016

a lot is done ;-) 4 dec 2015 . A sort of usermanual will be added soon.

27 dec. 2016, a lot of work has been done, latest addition is managing the history of guides: save, view, delete

A lot of work still waits ... (e.g. sometimes the plugin seems not to work, reason yet unknown: remedy: save picture and restart Gimp)
Help of use is a TODO@
