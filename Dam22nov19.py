#!/usr/bin/env python
# -*- coding: utf-8 -*-

#31 mrt, looks good for now, showMyMessage stays on  top!
#2 apr, make debugs invisible ... Ver 4apr 4.4
# 4 apr make a def for black and white stones, sorted  def blackAndWhiteStones L 680
# 5 apr with open(filenaam) as f: lines = [line.rstrip('\n') for line in f] for reading movements
# 5 apr
# 6 apr. make irrelevant stone-choice invisible done
# 7apr better order TODO of maininteraction!
# 7 apr normal stone ending on prolongation-line now become a DAM ;-)
# 7 apr single or dubble jumps ending on prolongation-line now become a Dam ;-)
#  7 apr trying normalThireOrderJumpsDict via allJumpDicts (normal and dam) and normalThireOrderJumpsDict
# 9 apr (fouten zoeken)
# 12 apr DamNew.py andere dam dict?!
# 17 apr algemene dam sprong gerealiseerd ?checknodig
# 17 apr sprong fout zoeken met 3dams1cannotjump_4fout.xcf verbeterd 04-19 09:32OK
# 19 april check normal jumps TODO done  looks good
# repair normal dam movement done
#20 apr round jump normal stone, start stone error
#21 apr OK,
#22 apr try replacing right and left by possible places or non
#25 apr damjump allows to use place of starting dam
# ==== the real UI
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
import json

#TODO ftp://ftp.univ-fcomte.fr/_Pour_Les_Etudiants_/Outils_Bureautiques_2009-2010/fscommand/Gimp/gimp_2_6_6/lib/gimp/2.0/python/gimpfu.py

damClass = None #to be replaced by the called class
jsonDone = None
black_piece_list= []
white_piece_list = []
jumpsAvailable = False

####test install a bord out of a list made by blackAndWhiteStones(both)
bordDone = True

sys.path.append(gimp.directory + "\\python_gtk")
#print(sys.path[-1])

from time import time, sleep
from datetime import datetime
'''
>>> from datetime import datetime
>>> datetime.now().strftime("%y-%m-%d %H:%M")
'17-04-05 08:48'
'''
from random import random
from random import randint
#global???!!!


multipleJumpPossible = False
singleJumpPossible = False
stoneBoxDBG = False

fromPlaceToCoord = {}
fromCoordToPlace = {}

simpleDiffs       = {"SE":[100, 100],"NE":[100, -100],"SW":[-100, 100],"NW":[-100, -100]}
simpleDiffsInvers = {(100, 100):"SE",(100, -100):"NE",(-100, 100):"SW",(-100, -100):"NW"}

def deleteValueFromDict(myD, myValue):
    nkey = [tuple(el) for el in myD.values()]
    inversD = dict(zip(nkey, myD.keys()))
    delKey = tuple(myValue)
    remKey = inversD[delKey]
    myD.pop(remKey)
    return myD


def findJumpToRemove(Fjump): #Fjump a list of jumps
    if len(Fjump) < 15:
        return
    fj = [ [Fjump[i],Fjump[i+1]] for i in range(1,len(Fjump),3)]
    tes = fj.index(fj[-1]) #only last element may be wrong!
    tmp = len(fj) - tes
    return ( tmp > 4)
    return (fj, tes)

def myDir(x, y):    #to find from two stones on a diagonal the direction!
    def mySign(x):
        tmp = 100 if x > 0 else -100
        return tmp
    xx = fromPlaceToCoord[x]
    yy = fromPlaceToCoord[y]
    di = [yy[0] - xx[0], yy[1] - xx[1]]
    tt  = (mySign(di[0]), mySign(di[1]))
    return simpleDiffsInvers[tt]

def roundPossible(L):
    richtingen = [myDir(L[i],L[i+1]) for i in range(1, len(L), 3)]
    return richtingen

randNr = [1, 2, 3, 4, 5, 15, 25, 35, 45 , 6, 16, 26, 36, 46, 47, 48, 49, 50]

def makeDictsInfo():
    global fromCoordToPlace, fromPlaceToCoord
    #debug(("L109 makedictsinfo"),1);
    black = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    white = [31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
    #for 1000x1000 board
    if False: #len(fromPlaceToCoord) == 50 :
        return
    lin_col = [ i*100 for i in range(10)]
    #a list of rownumber from 0 to 9 of the board
    rowindex = [ [i, i, i, i, i] for i in[el for el in range(10)]]
    #debug(rowindex,1)
    #to be converted to list of ints  only
    takefromrow = []
    for el in rowindex:
        takefromrow.extend(el)
    #STANDARD notation into coords of for guides (1000 x 1000 board!!!)
    start2rows = [1, 3, 5, 7, 9 , 0, 2, 4, 6, 8]*5
    fptc = {}
    for el in range(50):
        fptc[el + 1] = (lin_col[start2rows[el]] , lin_col[takefromrow[el]] )
    for i in range(1,51):
        fromPlaceToCoord[i] = ( fptc[i])
    fromCoordToPlace = dict([[tuple(v), k] for k, v in fromPlaceToCoord.items()])

makeDictsInfo()


def showMyMessage( msg = "Hallo die Enten"):
    """
    Helper for popup message screens
    """
    #PKHG>TODO gtk.Window.set_transient_for()
    dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK)
    dialog.set_keep_above(True)
    dialog.set_markup(msg)
    dialog.format_secondary_text("\n\nRemove me  test ;-)")
    dialog.run()
    dialog.destroy()


#for debugging needed info:
debug_output = False
def fdebug(val, withStones = False):
    def blackAndWhiteStones():
        #self.inititializeTheBord()
        image = gimp.image_list()[0]
        all_stone_layers = [el for el in image.layers if el.name.startswith("black") or el.name.startswith('white')]
        black_stone_layers = [el for el in all_stone_layers if el.name[:5] == 'black']
        white_stone_layers =  [el for el in all_stone_layers if el.name[:5] == 'white']
        black_stone_coords = [eval(el.name[7:]) for el in black_stone_layers]
        white_stone_coords = [eval(el.name[7:]) for el in white_stone_layers]
        whiteStones = [fromCoordToPlace[tuple(el)] for el in white_stone_coords]
        blackStones = [fromCoordToPlace[tuple(el)] for el in black_stone_coords]
        whiteStones.sort()
        blackStones.sort()
        blackDams = [el for el in blackStones if bord[el]['layer'].name[5] == 'D']
        whiteDams = [el for el in whiteStones if bord[el]['layer'].name[5] == 'D']
        return (whiteStones, blackStones, whiteDams, blackDams)

    fp = open(gimp.directory + "\\dammen\\Devellopment\\dbg\\DamNewDBG.txt", "a") #for DamNew ;-)
    image = gimp.image_list()[0]
    image_name = image.name
    buildDateTime =  datetime.now().strftime("%y_%m_%d %H:%M")
    allStones = None
    if withStones:
        layers = image.layers
        allStones = blackAndWhiteStones()
    json.dump(buildDateTime,fp)
    json.dump(image_name, fp)
    if allStones:
        fp.write(str(allStones))
    fp.write('\n')
    json.dump(str(val),fp)
    fp.write('\n')
    fp.write('\n')
    fp.close()

def debugOLD(val, urgent = 0 ):
    global debug_output
    #gimp.message(" debug called")
    """
    if urgent > 0 :
        gimp.message(str(val))
    if not debug_output :
        return
    """
    gimp.message(str(val))
def showMyMessage( msg = "Hallo die Enten"):
    """
    Helper for popup message screens
    """
    #PKHG>TODO gtk.Window.set_transient_for()
    dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK)
    dialog.set_keep_above(True)
    dialog.set_markup(msg)
    dialog.format_secondary_text("\n\nRemove me ;-)")
    dialog.run()
    dialog.destroy()
#for debugging needed info:
debug_output = False
def debug(val, urgent = 0 ):
    global debug_output
    #gimp.message(" debug called")
    if urgent > 1 :
        showMyMessage(str(val))
    if debug_output == False :
        return
    showMyMessage(str(val))
def debugErr(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    debug(fname+'\n'+str(exc_tb.tb_lineno)+'\n'+str(e), urgent = 1)

def debugErr(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    debug(fname+'\n'+str(exc_tb.tb_lineno)+'\n'+str(e), urgent = 1)

#PKHG>?
def diagonalDirections():
    diagonalStone = {'SE':'NW','SW':'NE','NE':'SW','NW':'SE'}
    return diagonalStone
diag = diagonalDirections()

def allowedCoord(coord):
    result = (coord[0] >=0 and coord[0] <= 900) and (coord[1] >=0 and coord[1] <= 900)
    return result

def burenOf(nr):
    result ={}
    if nr == 5 :
        result['SW'] = 10
    elif nr == 46 :
        result['NE'] = 41
    elif nr in [15, 25, 35, 45]:
        result['NW'] = nr - 5
        result['SW'] = nr + 5
    elif nr in [1, 2, 3, 4]:
        result['SW'] = nr + 5
        result['SE'] = nr + 6
    elif nr in [6, 16, 26, 36]:
        result['SE'] = nr + 5
        result['NE'] = nr - 5
    elif nr in [47, 48, 49, 50]:
        result['NW'] = nr - 6
        result['NE'] = nr - 5
    else:
        line = (nr - 1)/ 5
        even = (line % 2) == 0
        if even:
            result['SW'] = nr + 5
            result['SE'] = nr + 6
            result['NE'] = nr - 4
            result['NW'] = nr - 5
        else:
            result['SW'] = nr + 4
            result['SE'] = nr + 5
            result['NE'] = nr - 5
            result['NW'] = nr - 6
    return result

def makeDiag(van, richting):
    coordVan = list(fromPlaceToCoord[van])
    diff = simpleDiffs[richting]
    result = [van]
    val = coordVan
    OK = True
    while OK:
        val[0] += diff[0]
        val[1] += diff[1]
        if allowedCoord(val):
            nextNr = fromCoordToPlace[tuple(val)]
            result.append(nextNr)
        else:
            OK = False
    return result

buren = {}
for i in range(1,51):
    buren[i] = burenOf(i).keys()
    newDictBuren = {}
    for direction in buren[i]:
        newDictBuren[direction] = makeDiag(i, direction)
    buren[i] = newDictBuren

#global, because only ONE
bord = {}
for i in range(1, 51):
    bord[i] = {'layer':None,'buren':buren[i]}


damGeneralOrderDict = {}
damZeroOrderJumpsDict = {}
'''
damFirstOrderJumpsDict = {}
damSecondOrderJumpsDict = {}
'''
normalZeroOrderJumpsDict = {}

'''
normalFirstOrderJumpsDict = {}
normalSecondOrderJumpsDict = {}
normalThireOrderJumpsDict = {}
normalDictsList = [normalZeroOrderJumpsDict, normalFirstOrderJumpsDict, normalSecondOrderJumpsDict, normalThireOrderJumpsDict]
#PKHG>?allJumpDicts = {'normal':normalDictsList, 'dam':None}
'''


def listOfFollowingEmpties(inputList, damPlace = 0):
    #PKHG>OK04-21 fdebug(("L292 inputList", inputList))
    res = []
    if damPlace:         #a value given!
        res = [damPlace]
    for p in inputList[1:]:
        if bord[p]['layer'] == None:
            res.append(p)
            continue
        else:
            break
    #PKHG>OK
    #PKHG>OK04-21 fdebug(("L303 res ", res))
    return res

def searchNormalGeneralOrderJumps(normalStartList, forColor):
    if not normalStartList:
        return []
    #PKHG>04-20
    #PKHG>OK04-21 fdebug(("L310  normalStartList", normalStartList))
    """ "17_04_20 12:02""checkNormalRound.xcf" OK
    "('L312  normalStartList', [[23, 19, 14], [23, 29, 34], [23, 18, 12]])"
    """

    allTocheck = []
    nextNormalList = []
    for el in normalStartList:
        #PKHG>OK fdebug(("L318 el", el))
        """ "17_04_20 12:18""checkNormalRound.xcf" OK
        "('L320 el', [23, 19, 14])"
        """
        tmp = myDir(el[-2],el[-1])
        diag = {'SE':'NW','SW':'NE','NE':'SW','NW':'SE'}
        wrongDir = diag[tmp]
        #PKHG>04-20 12:02
        #PKHG>OK fdebug( ("L326  el,  wrongDir", el ,wrongDir))
        """ "17_04_20 12:18""checkNormalRound.xcf"
"('L328  el,  wrongDir', [23, 19, 14], 'SW')"
        """
        directions =  bord[el[-1]]['buren'].keys() # jumpgoal
        #PKHG>OK fdebug(("L331 before removing! directions from", el, directions))
        """ "17_04_20 12:21""checkNormalRound.xcf" OK
        "('L333 before removing! directions from', [23, 19, 14], ['SW', 'NE', 'SE', 'NW'])"
        """

        directions.remove(wrongDir) # inverse where onc came from
        #PKHG>OK         fdebug(("L337 directions from", el, directions))
        """ "17_04_20 12:21""checkNormalRound.xcf"
        "('L339 directions from', [23, 19, 14], ['NE', 'SE', 'NW'])"
        """

        tmp =  el + [directions]
        allTocheck.append(tmp)
        #PKHG>OK

    #PKHG>OK fdebug(("L346 RETURN allTocheck", allTocheck)) ;return
    """ "17_04_20 13:29""checkNormalRound.xcf"
"('L348 RETURN allTocheck', [[23, 19, 14, ['NE', 'SE', 'NW']], [23, 29, 34, ['SW', 'NE', 'SE']], [23, 18, 12, ['SW', 'NE', 'NW']]])"
    """
    """ 17_04_20 12:25""checkNormalRound.xcf""('L350 RETURN allTocheck', [
    [23, 19, 14, ['NE', 'SE', 'NW']],
    [23, 29, 34, ['SW', 'NE', 'SE']],
    [23, 18, 12, ['SW', 'NE', 'NW']]])"
    """

    for check in allTocheck:
        #PKHG>OK04-21 fdebug(("L357 check ", check))
        oldjump = check[:-1]
        startToJump = oldjump[-1]
        directions = check[-1]
        #PKHG>04-19        fdebug(("L361  oldjump startToJump directions", oldjump, startToJump, directions))
        """ "17_04_19 11:50""normal3dubbelesprongen.xcf"
"('L363  oldjump startToJump directions', [23, 29, 34], 34, ['SW', 'NE', 'SE'])"
"('L364  oldjump startToJump directions', [23, 18, 12], 12, ['SW', 'NE', 'NW'])"
"('L365  oldjump startToJump directions', [38, 42, 47], 47, ['NW'])"
"('L366  oldjump startToJump directions', [43, 39, 34], 34, ['NE', 'SE', 'NW'])"
        """
        for dire in directions:
            inputDiagonal = bord[startToJump]['buren'][dire]
            #PKHG>OK
            #PKHG>OK04-21 fdebug(("L371 startToJump dire inputDiagonal", startToJump, dire, inputDiagonal))
            if len(inputDiagonal) < 3:  #diagonal not long enough
                continue
            if bord[inputDiagonal[1]]['layer'] == None: #no stone to capture?
                continue
            if bord[inputDiagonal[1]]['layer'].name[:5] == forColor: # color?
                continue
            goodStone = inputDiagonal[1]
            #PKHG>OK04-21 fdebug(("L379 goodStone before check of done", goodStone))

            if goodStone in oldjump:
                continue
            #PKHG>OK
            #PKHG>OK04-21 fdebug(("L384 goodStone not in oldjump inputDiagonal", goodStone, inputDiagonal))
            """ "17_04_20 12:31""checkNormalRound.xcf"
            "('L386 goodStone not in oldjump inputDiagonal', 9, [14, 9, 3])"
            "17_04_20 12:31""checkNormalRound.xcf"
            "('L388 goodStone not in oldjump inputDiagonal', 40, [34, 40, 45])"
            "17_04_20 12:31""checkNormalRound.xcf"
            "('L390 goodStone not in oldjump inputDiagonal', 8, [12, 8, 3])"

            """

            """
            if goodStone == 7:
                #PKHG>OK04-21 fdebug(("L396  bord[inputDiagonal[2]]['layer']", bord[inputDiagonal[2]]['layer']))
            """

            if bord[inputDiagonal[2]]['layer'] == None or inputDiagonal[2] == oldjump[0]:
                newJump = oldjump + [goodStone, inputDiagonal[2]]
                nextNormalList.append(newJump)
    #PKHG>OK

    #PKHG>OK fdebug(("L404 RETURN  nextNormalList", nextNormalList)); return
    """ "17_04_20 13:31""checkNormalRound.xcf"
"('L406 RETURN  nextNormalList', [[23, 19, 14, 9, 3], [23, 29, 34, 40, 45], [23, 18, 12, 8, 3]])"
    """

    """ "17_04_20 12:36""checkNormalRound.xcf""('L409 RETURN  nextNormalList', [
    OK
    [23, 19, 14, 9, 3],
    [23, 29, 34, 40, 45],
    [23, 18, 12, 8, 3]])"
    """
    #PKHG>OK fdebug(("L 406 returning nextNormalList", nextNormalList))
    """ "17_04_20 12:39""checkNormalRound.xcf" "('L416 RETURN  nextNormalList', [
    [23, 19, 14, 9, 3],
    [23, 29, 34, 40, 45],
    [23, 18, 12, 8, 3]])"
    """
    return nextNormalList

    #################### ????????????????
    result = nextNormalList
    '''
    for el in nextNormalList:
        #PKHG>OK04-21 fdebug(("L427 return el", el))

        if len(el) == 3:
            result.append(el)
        else:
            tmp = el[:3]
            tmp2 = [[el[i] ,el[i + 1]] for el in  range(3, len(el), 2)]
            tmp.append(tmp2)
            result.append(tmp)
            continue
    #PKHG>OK04-21 fdebug(("L437 result", result))
    '''
    return result

def searchDamGeneralOrderJumps(damStartList, forColor):
    #PKHG>OK debug(("L442 forced return"));return
    if not damStartList:
        return []
    jteller = 0
    nextDamList = []
    order = -1
    order = len(damStartList[0]) - 1
    debug(("L449 jump-level ", order/2 ))

    allTocheck = []
    for el in damStartList:
        dirWrong = "I came from"
        if len(el) > 2:
            dirWrong = diag[myDir(el[-2],el[-1])]

        #PKHG>OK04-21 fdebug(("L457 dirWrong", dirWrong))
        directions = bord[el[-1]]['buren'].keys() #Last elemen either dam or jumpgoal
        if len(dirWrong) == 2:
            directions.remove(dirWrong)
        #PKHG>OK fdebug(("307 el, directions",el, directions))
        tmp = el + [directions]
        allTocheck.append(tmp)

    #PKHG>OK
    #PKHG>OK04-21 fdebug(("L466 allTocheck", allTocheck))

    """
    "17_04_16 16:01""3dams1cannotjump_2.xcf"
    "('L470 allTocheck', [[2, ['SW', 'SE']], [3, ['SW', 'SE']], [46, ['NE']]])"

    "17_04_18 15:40""3dams1cannotjump_4foutzonderD3.xcf"
    "('L473 allTocheck', [[2, ['SW', 'SE']], dam 46 no jump possible OK [46, ['NE']]])"

    "17_04_18 16:10""3dams1cannotjump_4foutzonderD3.xcf"
    "('L476 allTocheck', [[2, 7, 11, ['SW', 'NE', 'SE', 'NW']]])"

    """
    allJumpsInfo = []
    for check in allTocheck:
        oldjump = check[:-1]
        damStoneAllowed = oldjump[0]
        #PKHF>OK fdebug(("L483 RETRUN, damStoneAllowed", damStoneAllowed));return
        startToJump = oldjump[-1]
        directions = check[-1]
        #PKHG>OK
        #PKHG>OK04-21
        #if startToJump == [28, 23, 19, 13, 8, 12, 17]:
        #PKHF>OK fdebug(("L489 oldjump,startToJump, directions", oldjump, startToJump, directions))

        """ "17_04_18 15:40""3dams1cannotjump_4foutzonderD3.xcf"
        "('L492 oldjump,startToJump, directions', [2], 2, ['SW', 'SE'])"  OK
        "('L493 oldjump,startToJump, directions', [46], 46, ['NE'])"      ok

        "17_04_18 16:10""3dams1cannotjump_4foutzonderD3.xcf"
        "('L496 oldjump,startToJump, directions', [2, 7, 11], 11, ['SW', 'NE', 'SE', 'NW'])"

        """

        for dire in directions:
            inputDiagonal = bord[startToJump]['buren'][dire]
            #PKHG>OK
            #PKHG>OK04-21 fdebug(("L503 dire, inputDiagonal", dire, inputDiagonal))
            empties = listOfFollowingEmpties(inputDiagonal, startToJump )
            #empties = listOfFollowingEmpties(inputDiagonal, damStoneAllowed )

            #PKHG>OK
            #PKHG>OK04-21             fdebug(("L508 startToJump, empties" ,startToJump, empties))
            """ "17_04_16 17:59""3dams1cannotjump_2.xcf"
"('L510 startToJump, empties', 2, [2])"
"('L511 startToJump, empties', 2, [2, 8, 13])"
"('L512 startToJump, empties', 3, [3, 8, 12])"
"('L513 startToJump, empties', 3, [3])"
"('L514 startToJump, empties', 46, [46, 41, 37])"

            "17_04_18 16:05""3dams1cannotjump_4foutzonderD3.xcf"
            "('L517 startToJump, empties', 2, [2, 8, 13, 19, 24, 30, 35])" fout!

            "17_04_18 16:10""3dams1cannotjump_4foutzonderD3.xcf"
            "('L520 startToJump, empties', 11, [11])"

            """
            if len(empties) < len(inputDiagonal):
                captureStone = inputDiagonal[len(empties)]
                #PKHG>OK
                #PKHG>OK04-21 fdebug(("L526, captureStone", captureStone))
                """ "17_04_16 18:09""3dams1cannotjump_2.xcf"
"('L528, captureStone', 7)"
"('L529, captureStone', 19)"
"('L530, captureStone', 17)"
"('L531, captureStone', 9)"
"('L532, captureStone', 32)"
                """
                if bord[captureStone]['layer'].name[:5] == forColor:
                    fdebug(("L535 wrong color stone at ", captureStone))
                    continue
                goodStone = captureStone
                if goodStone in oldjump:
                    continue
                #PKHG>OK
                #PKHG>OK04-21 fdebug(("L541 goodStone ", goodStone))
                """
                "17_04_16 18:15""3dams1cannotjump_2.xcf"
"('L544 goodStone ', 7)"
"('L545 goodStone ', 19)"
"('L546 goodStone ', 17)"
"('L547 goodStone ', 9)"
                "17_04_18 15:40""3dams1cannotjump_4foutzonderD3.xcf"
                "('L549 goodStone ', 16)"
                "('L550 goodStone ', 17)"

                """
                whereInInput = inputDiagonal.index(goodStone)
                #PKHG>OK fdebug(("L554 inputDiagonal, whereInInput", inputDiagonal, whereInInput))
                nextInds = inputDiagonal[whereInInput:]
                #PKHG>OK fdebug(("L556 nextInds", nextInds))

                if len(nextInds) > 1:
                    for emptyQ in nextInds[1:]:
                        #emptyQ = nextInds[1]
                        if bord[emptyQ]['layer'] == None or emptyQ == damStoneAllowed:
                            #PKHG>OK fdebug(("L562 jump found TODO", emptyQ))
                            #NEWjump = oldjump + nextInds[:2]
                            NEWjump = oldjump + [goodStone, emptyQ]
                            nextDamList.append(NEWjump)
                            #PKHG>OK04-21 fdebug(("L566 new jump start order", NEWjump, oldjump[0], order/2))
                            """ "17_04_16 19:52""3dams1cannotjump_2.xcf" OK
"('new jump', [2, 7, 11])"
"('new jump', [2, 19, 24])"
"('new jump', [3, 17, 21])"
"('new jump', [3, 9, 14])"
                            """
                        else:
                            #PKHG>OK fdebug(("L574 following place not empty", emptyQ))
                            #PKHG>OK debug(("L575 break follows", emptyQ))
                            break
                else:
                    #PKHG>OK fdebug(("L578 diagonal too short", nextInds))
                    TODO = '???'

    #PKHG>OK04-21 fdebug(("L581 nextDamList", nextDamList))
    """
"17_04_17 17:53""[Untitled]" start !!!
"('L584 nextDamList', [[2, 7, 11], [2, 19, 24], [2, 19, 30], [2, 19, 35], [3, 17, 21], [3, 9, 14], [3, 9, 20], [3, 9, 25]])"

"17_04_17 17:20""[Untitled]"
"('L587 nextDamList', [[2, 7, 11, 17, 22, 18, 13, 19, 24, 29, 33, 39, 44], [2, 7, 11, 17, 33, 29, 24, 19, 13, 18, 22, 39, 44]])"

    """

    return nextDamList
###################newdam start
def stopPlaceNextDiags(bordStone, wrongDir, forColor):
    directionsThisPlacePossible = bord[bordStone]['buren'].keys()
    diag = {'SE':'NW','SW':'NE','NE':'SW','NW':'SE'}
    notLookBack = diag[wrongDir]
    directionsThisPlacePossible.remove(notLookBack)
    #PKHG>OK04-21 fdebug(("L598  new bordstone, directionsP", bordStone, directionsThisPlacePossible))
    """ "17_04_14 16:26""3dams1cannotjump.xcf" first of dam at 2
"('L600  new bordstone, directionsP', 11, ['SW', 'SE', 'NW'])"
    """
    newDictValues = []
    for thisDirection in directionsThisPlacePossible:
        diagonal = bord[bordStone]['buren'][thisDirection]
        lenDiagonal = len(diagonal)
        if lenDiagonal < 3:   #too few places for a jump?
            #PKHG>OK
            #PKHG>OK04-21 fdebug(("l560 diagonal too short", diagonal))
            continue                #diagonal not long enough
        empties = listOfFollowingEmpties(diagonal[1:])
        #not  starstone is EMPTY or assumed damStoneFromZeroJump
        lenEmpties = len(empties) + 1
        #stopPlaceNextDiags
        if lenEmpties + 1 < lenDiagonal:
            #PKHG>OK
            #PKHG>OK04-21 fdebug(("L616 diag too short", diagonal))
            continue
        else:
            newDictValues.append(  diagonal + [thisDirection])
    #PKHG>OK04-21 fdebug(("L620 stopPlaceNextDiags called and finished", newDictValues))
    return newDictValues

def searchDamZeroOrderJumps(stoneStartPlaces, forColor):
    global damZeroOrderJumpsDict
    #PKHG>OK     fdebug(("L625 sDZOJ stoneStartPlaces", stoneStartPlaces))
    """ "17_04_14 15:41""3dams1cannotjump.xcf" ok
"('L627 stoneStartPlaces', [2, 3, 46])"
    """
    damZeroOrderJumpsDict = {'order': 1}
    if stoneStartPlaces == []:
        return {}
    allPossibilities = []
    otherColor = 'black' if forColor == 'white' else 'white'
    jteller = 0
    for stone in stoneStartPlaces:
        directionsThisStonePossible = bord[stone]['buren'].keys()
        for thisDirection in directionsThisStonePossible:
            diagonal = bord[stone]['buren'][thisDirection]
            lenDiagonal = len(diagonal)
            if lenDiagonal < 3:   #too few places for a jump?
                #PKHG>OK04-21 fdebug(("L641 sDZOJ stopped diagonal too short ", diagonal))
                continue
            empties = listOfFollowingEmpties(diagonal[1:])   # 0th element = forColor stone!
            #PKHF>OK fdebug(("L644 sDZOJ empties" , empties))
            """ "17_04_14 15:55""3dams1cannotjump.xcf" OK  dam 2
            "('L646 sDZOJ empties', [])"
            """
            lenEmpties = len(empties)
            if lenEmpties + 1  <  lenDiagonal:     #at least two other places available?!
                rest = diagonal[lenEmpties + 1:]  #0th element of diagonal is a capturing (forColor) stone
                if bord[rest[0]]['layer'].name[:5] == otherColor:
                    if len(rest) > 1: #jump possible?
                        if bord[rest[1]]['layer'] != None:
                            continue  #no a second stone following
                    #PKHG>OK fdebug(("L655 rest", rest))
                    """ "17_04_14 15:55""3dams1cannotjump.xcf" dam 2 OK
"('L657 rest', [7, 11, 16])"
                    """
                    #check the following places?!
                    jumpFoundRestplaces = listOfFollowingEmpties(rest[1:])  # 0th one is otherColor
                    tmp = [stone, rest[0]] + jumpFoundRestplaces + [thisDirection]
                    allPossibilities.append(tmp)
                    continue
            else:
                continue
    #PKHG>OK    fdebug(("L666 allPossibilities order 1 dict", allPossibilities))
    """ "17_04_14 15:55""3dams1cannotjump.xcf" OK einde found jumps
"('L668 allPossibilities order 1 dict', [[2, 7, 11, 'SW'], [2, 19, 24, 'SE'], [3, 17, 21, 'SW'], [3, 9, 14, 20, 25, 'SE']])"
    """
    #allPossibilities = [[2, 7, 11, 'SW'], [2, 19, 24, 'SE'], [3, 17, 21, 'SW'], [3, 9, 14, 20, 25, 'SE']]
    #results as could be keys possible all are different!
    for el in allPossibilities:
        for stopPlace in el[2:-1]:
            #now generate new keys using empty surplus places!
            key = (el[0],el[1], stopPlace, el[-1])  #a tuple as key!

            #PKHG>TODO 14apr 16:25
            jteller += 1
            tmp = stopPlaceNextDiags(stopPlace, el[-1], forColor)[0] + [jteller]
            stmp = tuple(tmp)
            #PKHG>OK             fdebug(("L681 result of stopPlaceNextDiags", stmp))
            """ "17_04_15 07:43""3dams1cannotjump.xcf"
"('L683 result of stopPlaceNextDiags', (25, 30, 34, 39, 43, 48, 'SW', 6))"
            "17_04_14 16:41""3dams1cannotjump.xcf"
            "('L685 result of stopPlaceNextDiags', [25, 30, 34, 39, 43, 48, 'SW'])"
            """
            #PKHG>??? tmp = stmp[1:] + [stmp[0]]
            damZeroOrderJumpsDict[key] = stmp #OLD [el[0],el[1], stopPlace]
    #PKHG>OK
    #PKHG>OK04-21 fdebug(("L690 new values in dict", damZeroOrderJumpsDict)) #True save lists of all stones too!
    """ "17_04_14 16:45""3dams1cannotjump.xcf"
"('L692 new values in dict', {
(3, 9, 25, 'SE'): [25, 30, 34, 39, 43, 48, 'SW'],
(3, 17, 21, 'SW'): [21, 27, 32, 38, 43, 49, 'SE'],
(3, 9, 20, 'SE'): [20, 24, 29, 33, 38, 42, 47, 'SW'],
(2, 19, 24, 'SE'): [24, 29, 33, 38, 42, 47, 'SW'],
(2, 7, 11, 'SW'): [11, 17, 22, 28, 33, 39, 44, 50, 'SE'],
(3, 9, 14, 'SE'): [14, 19, 23, 28, 32, 37, 41, 46, 'SW'],
'order': 1
})"
    """
    return damZeroOrderJumpsDict


######################### normal stones jumps till order 2 20mrt17

normalZeroOrderJumpsDict = {}
normalFirstOrderJumpsDict = {}
normalSecondOrderJumpsDict = {}

def searchNormalFirstOrderJumps(zeroOrderDict, forColor):
    global normalFirstOrderJumpsDict
    allZeroOrderJumpsKeys = zeroOrderDict.keys()
    otherColor = 'black' if forColor == 'white' else 'white'
    nextChecks = []
    allPossibilities = []
    for jumpFoundKey in allZeroOrderJumpsKeys:
        theJump = zeroOrderDict[jumpFoundKey]
        nextChecks.append([jumpFoundKey[1],theJump[2]] + [jumpFoundKey])
    diag = {'SE':'NW','SW':'NE','NE':'SW','NW':'SE'}
    for toCheck in nextChecks:
        bordStone = toCheck[1]
        notLookBack = diag[toCheck[0]]
        directionsThisPlacePossible = bord[bordStone]['buren'].keys()
        directionsThisPlacePossible.remove(notLookBack) #remove back direction
        for thisDirection in directionsThisPlacePossible:
            diagonal = bord[bordStone]['buren'][thisDirection]
            lenDiagonal = len(diagonal)
            if lenDiagonal < 3:   #too few places for a jump?
                continue                #diagonal not long enough
            if bord[diagonal[1]]['layer'] == None:
                continue
            if bord[diagonal[1]]['layer'].name[:5] == forColor:
                continue
            if  bord[diagonal[2]]['layer'] == None:
                jumpFound = normalZeroOrderJumpsDict[toCheck[2]] + [diagonal[0], diagonal[1], diagonal[2], thisDirection]
                allPossibilities.append(jumpFound)
            continue
    if allPossibilities:
        for el in allPossibilities:
            key = (el[2],el[-1])
            normalFirstOrderJumpsDict[key] = el[:6]
    return normalFirstOrderJumpsDict

###12aprHIER
def searchNormalZeroOrderJumps(stoneStartPlaces, forColor):
    if stoneStartPlaces == []:
        return []            #no normal stones given
    normalJumpList = []
    #PKHG>OK    fdebug(("L750 return stoneStartPlaces", stoneStartPlaces)); return
    for stoneLi  in stoneStartPlaces:
        stone = stoneLi[0]
        directionsThisStonePossible = bord[stone]['buren'].keys()
        for thisDirection in directionsThisStonePossible:
            diagonal = bord[stone]['buren'][thisDirection]
            lenDiagonal = len(diagonal)
            if lenDiagonal < 3:   #too few places for a jump?
                continue
            if bord[diagonal[1]]['layer'] == None:
                continue
            if bord[diagonal[1]]['layer'].name[:5] == forColor:
                continue
            if bord[diagonal[2]]['layer'] == None:
                jumpFound = [stone] + diagonal[1:3]
                normalJumpList.append(jumpFound)
    #PKHG>OK04-21 fdebug(("L766  searchNormalZeroOrderJumps normalJumpList", normalJumpList))
    """"17_04_19 11:42""normal3dubbelesprongen.xcf""('L767 normalJumpList, damJumpList', [
    [23, 29, 34],
    [23, 18, 12],
    [38, 42, 47],
    [43, 39, 34]], [])"
    """
    return normalJumpList


def allNormalJumpsUptoOrder2(layerList, forColor):
    global normalZeroOrderJumpsDict, normalFirstOrderJumpsDict, normalSecondOrderJumpsDict
    normalZeroOrderJumpsDict = {}
    normalFirstOrderJumpsDict = {}
    normalSecondOrderJumpsDict = {}
    global jumpsAvailable
    stoneList = []
    for layer in layerList:
        place = fromCoordToPlace[tuple(eval(layer.name[7:]))]
        stoneList.append(place)
    normalZeroOrderJumpsDict = searchNormalZeroOrderJumps(stoneList, forColor)
    tmp ="no first order normalJumps"
    if normalZeroOrderJumpsDict:
        jumpsAvailable = True
        normalFirstOrderJumpsDict = searchNormalFirstOrderJumps(normalZeroOrderJumpsDict, forColor)
    if normalFirstOrderJumpsDict:
        normalSecondOrderJumpsDict = searchNormalSecondOrderJumps(normalFirstOrderJumpsDict,
    forColor)
    return

###################start class dam spel

class Damdevellop28apr0(object):
    """
    Dame = checker UI...
    """
    doDubbelJump = None
    dbJumpLen    = None
    dbJumpChosen = 1
    dbJumpPossibilities = None
    def __init__(self, runmode, img):
        self.img = img
        self.image_start_name = img.name
        backgroundlayer = self.img.layers[-1]
        pdb.gimp_image_set_active_layer(self.img, backgroundlayer)
        if not backgroundlayer.name.startswith("Background"):
            backgroundlayer.name = "Background orig= " + backgroundlayer.name
        #has_alpha = pdb.gimp_drawable_has_alpha(self.img.layers[-1])
        if runmode == RUN_INTERACTIVE:
            self.showDialog()
            #self.showDialog.default_width(50)
        elif runmode == RUN_WITH_LAST_VALS:
            self.showDialog()


    def makeBord(self, info):
        debug(("L822 makeBord called examplebord info local!"))
        info = [[2, 12, 34, 48, 49], [4, 6, 15, 16, 19, 33, 42], [12], []]
        info = [[3, 11, 27, 28, 43, 48, 49], [1, 4, 7, 14, 15, 16, 18, 19, 30, 31, 39, 42], [3, 27, 28], []]
        info = [[49, 43, 39],[35], [49, 43 ,39], [35]] #bp39
        whiteStones = info[0]
        blackStones = info[1]
        whiteDams = info[2]
        blackDams = info[3]
        self.insertTheseStones(whiteStones,'white', whiteDams)
        self.insertTheseStones(blackStones,'black', blackDams)

    def insertTheseStones(self, stoneList, color, damsList):
        image = gimp.image_list()[0]
        self.inititializeTheBord()
        if color == 'black':
            use_pattern = 'dammen_black'
        else:
            use_pattern = 'dammen_white'
        for stone in stoneList:
            occupiedAlready = bord[stone]['layer'] != None
            if False:
                showMyMessage( str(stone) + ", already occupied \n\
                inform PKHG ")
            else:
                x,y = fromPlaceToCoord[stone]
                pdb.gimp_context_set_pattern(use_pattern)
                drawable = image.layers[0]
                s = 32 # the rectangle shape!!!
                pattern_fill_choice = True
                take_this_pattern = pdb.gimp_context_get_pattern()
                #x,y = (100,100)
                pdb.gimp_image_select_ellipse(image, 2, x, y, 100, 100)
                pdb.python_fu_plugin_simple_shapes_centered(image,
                        image.layers[0], True, s, False,0,0,0,0,False,
                        0, 0, 0, 0, pattern_fill_choice,
                        take_this_pattern, False, (255,0,0), 10)
                drawable = image.layers[0]
                pdb.gimp_layer_set_name(drawable, color + " ;" + str([x , y ]))
                pdb.plug_in_autocrop_layer(image, drawable)
                pdb.gimp_selection_clear(image)
        self.inititializeTheBord()
        for dam in damsList:
            if color == 'white':
                pdb.gimp_context_set_foreground((0, 0, 0))
            else:
                pdb.gimp_context_set_foreground((255, 255, 255))
            tmp = bord[dam]['layer']
            self.makeStoneDam(tmp.name)

    def blackAndWhiteStones(self, color='black'):
        self.inititializeTheBord()
        image = gimp.image_list()[0]
        if color == 'black':
            black_stone_layers = [el for el in image.layers if el.name.startswith("black")]
            black_stone_coords = [eval(el.name[7:]) for el in black_stone_layers]
            blackStones = [fromCoordToPlace[tuple(el)] for el in black_stone_coords]
            blackStones.sort()
            return blackStones
        elif color == 'white':
            white_stone_layers = [el for el in image.layers if el.name.startswith("white")]
            white_stone_coords = [eval(el.name[7:]) for el in white_stone_layers]
            whiteStones = [fromCoordToPlace[tuple(el)] for el in white_stone_coords]
            whiteStones.sort()
            return whiteStones
        elif color == 'blackandwhite' or color == 'both':
            all_stone_layers = [el for el in image.layers if el.name.startswith("black") or el.name.startswith('white')]
            black_stone_layers = [el for el in all_stone_layers if el.name[:5] == 'black']
            white_stone_layers =  [el for el in all_stone_layers if el.name[:5] == 'white']
            black_stone_coords = [eval(el.name[7:]) for el in black_stone_layers]
            white_stone_coords = [eval(el.name[7:]) for el in white_stone_layers]
            whiteStones = [fromCoordToPlace[tuple(el)] for el in white_stone_coords]
            blackStones = [fromCoordToPlace[tuple(el)] for el in black_stone_coords]
            whiteStones.sort()
            blackStones.sort()
            blackDams = [el for el in blackStones if bord[el]['layer'].name[5] == 'D']
            whiteDams = [el for el in whiteStones if bord[el]['layer'].name[5] == 'D']
            return (whiteStones, blackStones, whiteDams, blackDams)
        return []

    def makeScreenshot(self, widget):
        import os
        allDammenPngs = []
        nrNow = 0
        for file in os.listdir(gimp.directory + '/dammen/steps/'):
            if file.startswith("dammenstep"):
                allDammenPngs.append(file)
                nrNow += 1
        result = self.saveThisStep(gimp.directory + '/dammen/steps/dammenstep', str(nrNow).zfill(2))
        automaticPic = self.automaticPicture.get_active() == 1
        if not automaticPic:
            showMyMessage(result + " is now available")
        else:
            notauto = True
        return

    def saveThisStep(self, picturePrefix, Step):
        image = gimp.image_list()[0]
        layer = pdb.gimp_layer_new_from_visible(image, image, "foo")
        thisName = picturePrefix + Step + ".png"
        pdb.file_png_save_defaults(image, layer, thisName, thisName )
        gimp.delete(layer)
        result =  "This Picture " + thisName + " created"
        return result

    ##SHOW and HIDE
    def showOrHideSetups(self, widget):
        activeWish = self.check_alternating.get_active() == 1 #setup ==> True
        if activeWish:
            self.makeDamLabel.show()
            self.makeDamEntry.show()
            self.makeTheDam.show()
            self.makeTheDam.show()
            self.removeStone.show()
            self.insertStoneAt.show()
            self.automaticPicture.hide()
        else:
            self.makeDamLabel.hide()
            self.makeDamEntry.hide()
            self.makeTheDam.hide()
            self.makeTheDam.hide()
            self.removeStone.hide()
            self.insertStoneAt.hide()
            self.automaticPicture.show()


    def setupDeleteStone(self, widget):
        showMyMessage("use for a while the Gimp layer menu\n\
        copy a normal black or white stone \n\
        and adjust layers name!\n\
        color?;[x,y]\n\
        where color either black or white\n\
        where ? ONE space x and y hundreds in range 0 ... 900 ")
        return

    def aStoneToRemove(self):
        image = gimp.image_list()[0]
        self.inititializeTheBord()
        stoneRemoveLocation = self.makeDamEntry.get_text()
        if stoneRemoveLocation.isdigit():
            stoneRemoveLocation = int(stoneRemoveLocation)
            if stoneRemoveLocation in range(1,51):
                layerToRemove = bord[stoneRemoveLocation]['layer']
                if layerToRemove:
                    #image = gimp.image_list()[0]
                    image.remove_layer(layerToRemove)
                    pdb.gimp_displays_flush()


    def removeOneStone(self, widget):
        self.aStoneToRemove()

    def insertANewStone(self, widget , *data ):
        where, color = data
        tmp = color.get_active()
        if tmp:
            self.activeColorValue = 'white'
        else:
            self.activeColorValue = 'black'
        where = where.get_text()
        color = self.activeColorValue
        stoneList = []
        if where.find(','):
            try:
                res = where.split(",")
                for el in res :
                    delen = el.split('-')
                    if len(delen) == 1:
                        tmp = int(delen[0])
                        stoneList.append(tmp)
                    elif len(delen) == 2:
                        v,t = [int(el) for el in delen]
                        tmp = [el for el in range(v, t + 1)]
                        stoneList.extend(tmp)
            except:
                showMyMessage("Sorry, input error only integer, or w,x-y,z or the like\n\
                example: 3-5,7,9,11-15")
        else:
            if where.isdigit():
                stoneList = int(where)
            else:
                showMyMessage("something wrong with " + where + " the inputvalue")
                return
        check1 = [el for el in stoneList if el < 1 or el > 50]
        if len(check1) > 0:
            showMyMessage("Wrong choices generated:" + str(check1) + "\n\
            repair please")
            return
        image = gimp.image_list()[0]
        self.inititializeTheBord()
        if color == 'black':
            use_pattern = 'dammen_black'
        else:
            use_pattern = 'dammen_white'
        for stone in stoneList:
            occupiedAlready = bord[stone]['layer'] != None
            if occupiedAlready:
                showMyMessage( str(where) + ", already occupied \n\
                try something else please ;-) ")
                return
            x,y = fromPlaceToCoord[stone]
            pdb.gimp_context_set_pattern(use_pattern)
            #drawable = self.image.layers[0]
            drawable = image.layers[0]
            s = 32 # the rectangle shape!!!
            pattern_fill_choice = True
            take_this_pattern = pdb.gimp_context_get_pattern()
            #x,y = (100,100)
            pdb.gimp_image_select_ellipse(image, 2, x, y, 100, 100)
            pdb.python_fu_plugin_simple_shapes_centered(image,
                        image.layers[0], True, s, False,0,0,0,0,False,
                        0, 0, 0, 0, pattern_fill_choice,
                        take_this_pattern, False, (255,0,0), 10)
            drawable = image.layers[0]
            pdb.gimp_layer_set_name(drawable, color + " ;" + str([x , y ]))
            pdb.plug_in_autocrop_layer(image, drawable)
            pdb.gimp_selection_clear(image)


    def radioCallback(self, widget, data=None):
        tmp =  "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        tmp2 = (data, ("OFF", "ON")[widget.get_active()])
        if tmp2 == ('white','ON'):
            self.activeColorValue = 'white'
        elif tmp2 == ('black','ON'):
            self.activeColorValue = 'black'
        elif tmp2 == ('left','ON'):
            self.rightOrLeftValue = 'left'
        elif tmp2 == ('right','ON'):
            self.rightOrLeftValue = 'right'
        elif tmp2 == ('SE','ON'):
            self.damDirectionChoice = 'SE'
        elif tmp2 == ('NE','ON'):
            self.damDirectionChoice = 'NE'
        elif tmp2 == ('SW','ON'):
            self.damDirectionChoice = 'SW'
        elif tmp2 == ('NW','ON'):
            self.damDirectionChoice = 'NW'
        theModeNow = self.check_alternating.get_active()
        self.setTexten()


    def changed_cb(self, combobox):
        self.setTexten()
        return
        self.inititializeTheBord()
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1: #and stoneBoxDBG:
            where = int(model[index][0])
            #PKHG>04-22 17:25 TODO            fdebug(("L1071 clicked is where color = ", where, self.activeColorValue))
            bordLayer = bord[where]['layer']
            if bordLayer == None:
                self.windChoices.hide()
                self.rlHbox.hide()
                self.textEntryHbox.hide() #09-23
                self.damInfo.hide()
            else:
                isNormalStone = bordLayer.name[5] == ' '
                if isNormalStone:
                    stoneColor = bordLayer.name[:5]
                    direction1 = '??'
                    direction2 = '??'
                    if stoneColor == self.activeColorValue:
                        if stoneColor == 'black':
                            direction1 = 'SE'
                            direction2 = 'SW'
                        else:
                            direction1 = 'NE'
                            direction2 = 'NW'

                        #PKHG>OK
                        #fdebug(("L1093 active c. stones color is  ",self.activeColorValue, stoneColor))
                        directions = bord[where]['buren'].keys()
                        #PKHG>TODO funktion!
                        if direction1 in directions:
                            seDiagonal = bord[where]['buren'][direction1]
                            #pkhg>ok fdebug(("L1098 SE or  NE diag", seDiagonal))
                            emptyQ = bord[seDiagonal[1]]['layer'] == None
                            if emptyQ:
                                self.rightTextEntry.set_text(str(seDiagonal[1]))
                            else:
                                self.rightTextEntry.set_text('occupied')
                        else:
                            self.rightTextEntry.set_text('impossible')
                        if direction2 in directions:
                            swDiagonal = bord[where]['buren'][direction2]
                            #PKHG>OK fdebug(("L1108 SW or NW diag", swDiagonal))
                            emptyQ = bord[swDiagonal[1]]['layer'] == None
                            if emptyQ:
                                self.leftTextEntry.set_text(str(swDiagonal[1]))
                            else:
                                self.leftTextEntry.set_text('occupied')
                        else:
                            self.leftTextEntry.set_text('impossible')
                    else:
                        showMyMessage("stones color and active color are different\n\
       please chose differen stone and/or then color then stone ;-)")
                    self.windChoices.hide()
                    self.rlHbox.show()
                    self.textEntryHbox.show()
                    self.damInfo.hide()
                else:
                    self.windChoices.show()
                    self.rlHbox.hide()
                    self.damInfo.show()
        return

    def setTexten(self):
        #PKHG>OK fdebug("********* setTexten called")
        self.inititializeTheBord()
        model = self.stoneBox.get_model()
        index = self.stoneBox.get_active()
        if index > -1: #and stoneBoxDBG:
            where = int(model[index][0])
            #PKHG>04-22 17:25 TODO            fdebug(("L1136 clicked is where color = ", where, self.activeColorValue))
            bordLayer = bord[where]['layer']
            if bordLayer == None:
                self.windChoices.hide()
                self.rlHbox.hide()
                self.textEntryHbox.hide() #09-23
                self.damInfo.hide()
            else:
                isNormalStone = bordLayer.name[5] == ' '
                if isNormalStone:
                    stoneColor = bordLayer.name[:5]
                    direction1 = '??'
                    direction2 = '??'
                    if stoneColor == self.activeColorValue:
                        if stoneColor == 'black':
                            direction1 = 'SE'
                            direction2 = 'SW'
                        else:
                            direction1 = 'NE'
                            direction2 = 'NW'

                        #PKHG>OK
                        #fdebug(("L1158 active c. stones color is  ",self.activeColorValue, stoneColor))
                        directions = bord[where]['buren'].keys()
                        #PKHG>TODO funktion!
                        if direction1 in directions:
                            seDiagonal = bord[where]['buren'][direction1]
                            debug(("L1163 SE or  NE diag", seDiagonal))
                            emptyQ = bord[seDiagonal[1]]['layer'] == None
                            if emptyQ:
                                self.rightTextEntry.set_text(str(seDiagonal[1]))
                            else:
                                self.rightTextEntry.set_text('occupied')
                        else:
                            self.rightTextEntry.set_text('impossible')
                        if direction2 in directions:
                            swDiagonal = bord[where]['buren'][direction2]
                            #PKHG>OK fdebug(("L1173 SW or NW diag", swDiagonal))
                            emptyQ = bord[swDiagonal[1]]['layer'] == None
                            if emptyQ:
                                self.leftTextEntry.set_text(str(swDiagonal[1]))
                            else:
                                self.leftTextEntry.set_text('occupied')
                        else:
                            self.leftTextEntry.set_text('impossible')
                    else:
                        showMyMessage("stones color and active color are different\n\
       please chose differen stone and/or then color then stone ;-)")
                    self.windChoices.hide()
                    self.rlHbox.show()
                    self.textEntryHbox.show()
                    self.damInfo.hide()
                else:
                    self.windChoices.show()
                    self.rlHbox.hide()
                    self.damInfo.show()
        return

    def getStoneNumber(self):
        model = self.stoneBox.get_model()
        index = self.stoneBox.get_active()
        if index > -1 :
            if stoneBoxDBG: showMyMessage( model[index][0] + ' selected')
            return model[index][0]
        else:
            showMyMessage("Yet no stone is selected; '' returned")
            return ''


    def showDialog(self):
        global fromCoordToPlace, fromPlaceToCoord
        self.dubbelJumps = False
        dialog = gtk.Dialog("Checker UI",
                   None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   ( gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)) #,
                    #gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.set_keep_above(True);

        label = gtk.Label("Dame V6.1, \nclick to choose a stone!:")
        label.show()
        dialog.vbox.add(label)
        self.stoneBox = gtk.ComboBox()
        liststore = gtk.ListStore(str)
        cell = gtk.CellRendererText()
        self.stoneBox.pack_start(cell)
        self.stoneBox.add_attribute(cell, 'text', 0)
        dialog.vbox.add(self.stoneBox)
        self.stoneBox.set_wrap_width(5)
        for n in range(1, 51):
            liststore.append(['%d'%n])
        self.stoneBox.set_model(liststore)
        self.stoneBox.connect('changed', self.changed_cb)
        #####???? self.stoneBox.connect('focus', self.changed_cb)
        #####????self.stoneBox.connect('focus'
        self.stoneBox.set_active(-1)
        self.stoneBox.show()

        self.rightOrLeft = gtk.CheckButton("move to right, default left!")
        #self.rightOrLeft.show()
        dialog.vbox.add(self.rightOrLeft)

        bwHbox = gtk.HBox(False, 10)
        bwHbox.show()
        dialog.vbox.add(bwHbox)
        self.whiteRadio = gtk.RadioButton(None,'white')
        self.activeColorValue = 'white'
        self.whiteRadio.connect("toggled", self.radioCallback, 'white')
        bwHbox.pack_start(self.whiteRadio, True, True, 0)
        self.whiteRadio.show()
        self.blackRadio = gtk.RadioButton(self.whiteRadio, 'black')
        self.blackRadio.connect("toggled", self.radioCallback, 'black')
        bwHbox.pack_start(self.blackRadio, True, True, 0)
        self.blackRadio.show()

        self.rlHbox = gtk.HBox(False, 10)
        self.rlHbox.show()
        dialog.vbox.add(self.rlHbox)
        self.leftRadio = gtk.RadioButton(None,'left')
        self.leftRadio.connect("toggled", self.radioCallback, 'left')
        self.rlHbox.pack_start(self.leftRadio, True, True, 0)
        self.leftRadio.show()
        self.rightOrLeftValue = 'left' #default value
        self.rightRadio = gtk.RadioButton(self.leftRadio, 'right')
        self.rightRadio.connect("toggled", self.radioCallback, 'right')
        self.rlHbox.pack_start(self.rightRadio, True, True, 0)
        self.rightRadio.show()

        #PKHG>04-23 TODO numberwindows OK
        self.leftTextEntry = gtk.Entry(max = 10)
        self.leftTextEntry.set_text('??')
        self.leftTextEntry.show()
        self.rightTextEntry = gtk.Entry(max = 10)
        self.rightTextEntry.set_text('??')
        self.rightTextEntry.show()
        self.textEntryHbox = gtk.HBox(False,10)
        self.textEntryHbox.pack_start(self.leftTextEntry, True, True, 0)
        self.textEntryHbox.pack_start(self.rightTextEntry, True, True, 0)
        self.textEntryHbox.show()
        dialog.vbox.add(self.textEntryHbox)

        self.which_jump = self.makeCombo([['first',0],['second',1]])
        #self.which_jump.show()
        dialog.vbox.add(self.which_jump)
        self.which_jump.hide()

        self.damInfo = gtk.Label("Dam-movement needs direction!")
        self.damInfo.show()
        dialog.vbox.add(self.damInfo)

        self.four_directions = self.makeCombo([['SE',0],['SW',1],['NE',2],['NW',3]])
        #PKHG>NOGNIET???
        self.four_directions.hide()
        dialog.vbox.add(self.four_directions)

        self.windChoices = gtk.VBox(False, 10)
        self.windChoices.show()
        dialog.vbox.add(self.windChoices)

        row1Wind = gtk.HBox(False, 10)
        row1Wind.show()
        self.windChoices.pack_start(row1Wind)
        row2Wind = gtk.HBox(False, 10)
        row2Wind.show()
        self.windChoices.pack_start(row2Wind)

        self.damDirectionChoice = 'SE' #default damchoice

        self.seChoice = gtk.RadioButton(None,'SE')
        self.seChoice.show()
        self.seChoice.connect('toggled', self.radioCallback, 'SE')
        row1Wind.pack_start(self.seChoice)

        self.neChoice = gtk.RadioButton(self.seChoice,'NE') #connect se
        self.neChoice.show()
        self.neChoice.connect('toggled', self.radioCallback, 'NE')
        row1Wind.pack_start(self.neChoice)

        self.swChoice = gtk.RadioButton(self.neChoice,'SW') #attention to connect the 4 buttons!
        self.swChoice.show()
        self.swChoice.connect('toggled', self.radioCallback, 'SW')
        row2Wind.pack_start(self.swChoice)

        self.nwChoice = gtk.RadioButton(self.swChoice,'NW') #connect to sw
        self.nwChoice.connect('toggled', self.radioCallback, 'NW')
        self.nwChoice.show()
        row2Wind.pack_start(self.nwChoice)

        self.label_notations = gtk.Label("notations: yet no")
        self.label_notations.show()
        dialog.vbox.add(self.label_notations)
        self.which_notation_entry = gtk.Entry(2)
        dialog.vbox.add(self.which_notation_entry)
        self.execute_the_choice = gtk.Button("execute your choice")
        self.execute_the_choice.connect('clicked', self.chooseYourJump)
        dialog.vbox.add(self.execute_the_choice)

        #choices for the player
        self.tryMove = gtk.Button("(try) \nMOVE me!")
        map = self.tryMove.get_colormap()
        colorTryMove = map.alloc_color("#3f3")
        #copy the current style and replace the background
        style = self.tryMove.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = colorTryMove
        style.bg[gtk.STATE_ACTIVE] = colorTryMove
        style.bg[gtk.STATE_PRELIGHT] = colorTryMove
        #set the button's style to the one you created
        self.tryMove.set_style(style)

        self.tryMove.show()
        dialog.vbox.add(self.tryMove)
        self.tryMove.connect("clicked", self.mainInteraction) #moveOneStep)

        self.check_alternating = self.makeCombo([['game mode',0],
                                                 ['setup mode',1]])
        self.check_alternating.connect('changed',self.showOrHideSetups)
        self.check_alternating.show()
        dialog.vbox.add(self.check_alternating)
        #run at least and show the UI
        self.makeDamLabel = gtk.Label("setup location to use:")
        #self.makeDamLabel.show()
        dialog.vbox.add(self.makeDamLabel)
        self.makeDamEntry = gtk.Entry(100)
        #self.makeDamEntry.show()
        dialog.vbox.add(self.makeDamEntry)
        self.makeTheDam = gtk.Button("OK make the stone a Dam")
        self.makeTheDam.connect("clicked", self.makeThisStoneADam)
        #self.makeTheDam.show()
        dialog.vbox.add(self.makeTheDam)

        self.screenshotButton = gtk.Button('make a Screenshot at\n\
        gimp.directory/dammen/steps/')
        self.screenshotButton.show()
        map = self.screenshotButton.get_colormap()
        colorScreenshot = map.alloc_color("#6ff")
        #copy the current style and replace the background
        style = self.screenshotButton.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = colorScreenshot
        #set the button's style to the one you created
        self.screenshotButton.set_style(style)
        self.screenshotButton.connect('clicked', self.makeScreenshot)
        dialog.vbox.add(self.screenshotButton)

        self.saveMoves = self.makeCombo([['do not save  movements',0],
                                         ['save movements',1]])

        movesMap = self.saveMoves.get_colormap()
        colorMoveMap = movesMap.alloc_color("#2e2")
        styleMoveMap = self.saveMoves.get_style().copy()
        styleMoveMap.bg[gtk.STATE_NORMAL] = colorMoveMap

        self.saveMoves.show()
        dialog.vbox.add(self.saveMoves)
        self.removeStone = gtk.Button("remove a Stone")
        mapRS = self.removeStone.get_colormap()
        colorRemoveStone = mapRS.alloc_color("#f00")
        styleCR = self.removeStone.get_style().copy()
        styleCR.bg[gtk.STATE_NORMAL] = colorRemoveStone

        self.removeStone.connect("clicked", self.removeOneStone)
        self.removeStone.set_style(styleCR)
        dialog.vbox.add(self.removeStone)

        self.insertStoneAt = gtk.Button("insert stone or stones")
        self.insertStoneAt.connect("clicked", self.insertANewStone,
                                   self.makeDamEntry,
                                   self.whiteRadio)
        mapIS = self.insertStoneAt.get_colormap()
        colorIS = mapIS.alloc_color('#88f')
        styleIS = self.insertStoneAt.get_style().copy()
        styleIS.bg[0] = colorIS
        self.insertStoneAt.set_style(styleIS)
        #self.insertStoneAt.show()
        dialog.vbox.add(self.insertStoneAt)
        self.automaticPicture = gtk.CheckButton("automatic Picture?!")
        #self.automaticPicture.connect('clicked', self.makeScreenshot)
        self.automaticPicture.show()
        dialog.vbox.add(self.automaticPicture)
        response = dialog.run()
        dialog.destroy()
        return

    def do_the_jump(self, widget):
        which_jump = self.notation_chpoices.get_active() - 1
        if (which_jump < 0) or which_jump > len(self.take_info):
            showMyMessage("wrong choice done.")
            return #PKHG>7feb  ok???
        self.do_simple_jump([self.take_info[which_jump]]) #expecting a list
        self.label_notations.set_text("notations: yet no")
        self.execute_the_choice.hide()
        self.hide_notation_execute()

    def makeStoneDam(self, piece_as_layer_name, is_good_layer = False):
        if piece_as_layer_name[5] == "D": #it is already a Dam ;-)
            showMyMessage("this Stone is already a Dam")
            return
        image = gimp.image_list()[0]
        drawable = pdb.gimp_layer_new(image, 10, 10, 1, "dambackground", 100, NORMAL_MODE)
        pdb.gimp_image_add_layer(image, drawable, 0)
        theText = text_layer = pdb.gimp_text_fontname(image, drawable, 0, 0, 'Dam', 0, True, 32, 0, 'Segoe print')
        pdb.gimp_floating_sel_to_layer(theText)
        widthNew = pdb.gimp_drawable_width(theText)
        heightNew = pdb.gimp_drawable_height(theText)
        name, place = piece_as_layer_name.split(';')
        x, y = eval(place)
        pdb.gimp_layer_set_offsets(theText, x + 10 , y + 20)
        new_piece_layer_dam = pdb.gimp_image_merge_down(image, text_layer, 1)
        pdb.plug_in_autocrop_layer(image,image.layers[0])
        names = [el.name for el in image.layers]
        layer_order = names.index(piece_as_layer_name)
        piece_layer = image.layers[layer_order]
        pdb.gimp_image_reorder_item(image, piece_layer, None, 1)
        new_piece_layer_dam = pdb.gimp_image_merge_down(image, image.layers[0], 1)
        new_piece_layer_dam.name = piece_as_layer_name[:5] + 'D;' + piece_as_layer_name[7:]
        #debug(("L1450 renamed piece",new_piece_layer_dam),1)
        pdb.gimp_displays_flush()
        return new_piece_layer_dam

    def hide_notation_execute(self):
        self.notation_choices.hide()
        self.execute_the_choice.hide()

    def get_layer_from_place(self, stone_layers, place):
        """
        result: the layer with place in coord or number
        otherwise None
        """
        global fromPlaceToCoord
        coord_of_place = place;
        if place.isdigit():
            coord_of_place = str(list(fromPlaceToCoord[int(place)]))
        used_coords = [el.name[7:] for el in stone_layers]
        result = None
        try:
            index = used_coords.index(coord_of_place)
            result = stone_layers[index]
        except:
            result = None
        return result


    #PKHG> start each time with THIS image stones
    def search_jumps(self, condition = 'black'):
        image = gimp.image_list()[0]
        all_stone_layers = [el for el in image.layers if el.name.startswith("black") or
                          el.name.startswith('white')]
        black_stone_layers = [el for el in all_stone_layers if el.name[:5] == 'black']
        white_stone_layers =  [el for el in all_stone_layers if el.name[:5] == 'white']
        black_stone_coords = [eval(el.name[7:]) for el in black_stone_layers]
        white_stone_coords = [eval(el.name[7:]) for el in white_stone_layers]
        all_stones_coords = [eval(el.name[7:]) for el in all_stone_layers]
        result = []
        jumps = []
        meerslag_extra = []
        for i, whitestone in enumerate(white_stone_layers):
            wx, wy = eval(whitestone.name[7:])
            tmp = []
            for j, blackstone in enumerate(black_stone_coords):
                bx, by = blackstone
                diff = [wx - bx, wy - by]
                if (abs(wx - bx) <= 100) and (abs(wy - by) <= 100) :
                    #candidat found, check which possibilty now:
                    #white black empty or black white empty!
                    #b w e first
                    ex , ey = [wx + diff[0], wy + diff[1]]
                    if ((ex >= 0) and (ex <= 900)) and ((ey >= 0) and (ey <= 900)) :
                        #debug(("L1502 ex ey bwe ", ex, ey), 1)
                        te = [ex, ey] not in all_stones_coords #check if empty, no stone?!
                        #debug(("L1504 in try", te),1)
                        if te:
                            a_jump_from_to = [black_stone_layers[j], whitestone, [ex, ey]]
                            jumps.append(a_jump_from_to)
                            if condition == 'black':
                                meerslag_extra.append(a_jump_from_to)
                    #w b e now
                    ex, ey = [bx - diff[0], by - diff[1]]
                    if ((ex >= 0) and (ex <= 900)) and ((ey >= 0) and (ey <= 900)) :
                        #debug(("L1513 ex ey wbe ", ex, ey), 1)
                        te = [ex, ey] not in all_stones_coords
                        #debug(("L1515 in try", te),1)
                        if te:
                            a_jump_from_to = [whitestone, black_stone_layers[j], [ex, ey]]
                            jumps.append(a_jump_from_to)
                            if condition == 'white':
                                meerslag_extra.append(a_jump_from_to)
        lme = len(meerslag_extra)
        notation = ""
        if lme == 1:
            check_start  = meerslag_extra.pop(0)
            start = eval(check_start[0].name[7:])
            where = check_start[2] #eval(check_start[1].name[7:])
            check_colors_of = self.three_directions(start,  where)
            if condition == 'black':
                check_me = [el for el in check_colors_of if el in white_stone_coords]
            else:
                check_me = [el for el in check_colors_of if el in black_stone_coords]
            if len(check_me) == 1:
                ch = check_me.pop(0)
                tmp = [2 * ch[0] - where[0], 2 * ch[1] - where[1]]
                start_str = str(fromCoordToPlace[tuple(start)])
                end_str = str(fromCoordToPlace[tuple(tmp)])
                notation = start_str + " x " + end_str
        #PKHG>??? 12apr
        elif lme > 1:
            pass
        elif lme == 0:
            pass
        else:
            pass
        return (notation, jumps)

    def three_directions(self, start, where):
        not_this = [(start[0] - where[0]), (start[1] - where[1])]
        four_possibilities = [[200, 200 ], [200 , -200  ], [-200 , 200 ], [-200 , -200 ]]
        index = four_possibilities.index(not_this)
        four_possibilities.pop(index)
        three_diffs = [[el[0]/2, el[1]/2] for el in four_possibilities]
        tmp = [ [where[0] + el[0], where[1] + el[1]] for el in three_diffs]
        tmp_OK = [ el for el in tmp if self.allowed_coord(el)]
        return  tmp_OK #name should be three_possibilities ;-)

    def do_simple_jump(self, info):
        image = gimp.image_list()[0]
        info = info[0]
        moving_layer = info[0]
        mx, my = eval(moving_layer.name[7:])
        offx, offy = [info[2][0] - mx, info[2][1] - my]
        to_delete_layer = info[1]
        new_destination = str(info[2])
        pdb.gimp_layer_translate(moving_layer, offx, offy)
        new_name = moving_layer.name[:7] + new_destination
        moving_layer.name = new_name
        image.remove_layer(to_delete_layer)
        pdb.gimp_displays_flush()

    def neighbOtherColor(self, whoAndNeighbourKeys, inputColor, kandidaten,  otherColor = 'black'):
        #whoAndNeighbourKeys a list of tuples: bordnr, all directions of this board)
        nr, dirs = whoAndNeighbourKeys
        result = [el for el in kandidaten]
        #debug(("L1575",nr,dirs))
        Found = False
        for dire in dirs:
            tmp = bord[nr]['neighbours'][dire]
            if (tmp in randNr) and (not nr in randNr):
                debug(("810 afgewezen = ", tmp))
                continue
            if (bord[tmp] == None) or (bord[tmp]['color'] == inputColor)  :
                debug(("L1583 afgewezen tmp", tmp))
                kannweg = 0 #removeme
            else:
                result.append((nr, tmp, dire))
                debug(("L1587", nr, tmp, dire, result))
                Found = True
            if not Found:
                continue
            else:
                #check if jumpgoal is free!
                checkToDo = [el for el in result]
                for el in checkToDo:
                    stoneNumber, otherStone, direction = el
                    if direction not in bord[otherStone]['neighbours'].keys():
                        continue
                    else:
                        thisDambordPlace = bord[otherStone]['neighbours'][direction]
                        if bord[thisDambordPlace] == None:
                            result.append(thisDambordPlace)
        return result

#next two def's to addd checkboxes
    def fillCombo(self, Store, combobox):
        st = combobox.get_model()
        st.clear()
        for n in Store: st.append(n)
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

    def makeThisStoneADam(self, widget):
        self.inititializeTheBord()
        stoneToDam = self.makeDamEntry.get_text()
        if stoneToDam.isdigit():
            stoneToDam = eval(stoneToDam)
            if stoneToDam in range(1,51):
                bordInfo = bord[stoneToDam]
                stoneExists = bordInfo['layer'] != None
                if stoneExists:
                    debug("L1631 new DAM at " + str(stoneToDam))
                    self.makeStoneDam(bordInfo['layer'].name, True)
                else:
                    showMyMessage("No stone at that place\nTry again please ;-)")
            else:
                showMyMessage("either typing ERROR or no stone at that place\nTry again please ;-)")
        else:
            showMyMessage("wrong Input: A stone on 1..51.\nTry again please")

    def makeStoneDam(self, piece_as_layer_name, is_good_layer = False):
        #PKHG>OK         debug(("L1641 makeStoneDam called with",piece_as_layer_name[7:]))
        if piece_as_layer_name[5] == "D": #it is already a Dam ;-)
            debug(("L1643 makeStoneDam called, already Dam"))
            return
        color = piece_as_layer_name[:5]
        debug(("L1671 color = " , color), 1)
        if color == 'white':
            pdb.gimp_context_set_foreground((0, 0, 0))
        else:
            pdb.gimp_context_set_foreground((255, 255, 255))
        image = gimp.image_list()[0]
        drawable = pdb.gimp_layer_new(image, 10, 10, 1, "dambackground", 100, NORMAL_MODE)
        pdb.gimp_image_add_layer(image, drawable, 0)
        theText = text_layer = pdb.gimp_text_fontname(image, drawable, 0, 0, 'Dam', 0, True, 32, 0, 'Segoe print')
        pdb.gimp_floating_sel_to_layer(theText)
        widthNew = pdb.gimp_drawable_width(theText)
        heightNew = pdb.gimp_drawable_height(theText)
        name, place = piece_as_layer_name.split(';')
        x, y = eval(place)
        pdb.gimp_layer_set_offsets(theText, x + 10 , y + 20)
        new_piece_layer_dam = pdb.gimp_image_merge_down(image, text_layer, 1)
        pdb.plug_in_autocrop_layer(image,image.layers[0])
        names = [el.name for el in image.layers]
        layer_order = names.index(piece_as_layer_name)
        piece_layer = image.layers[layer_order]
        pdb.gimp_image_reorder_item(image, piece_layer, None, 1)
        new_piece_layer_dam = pdb.gimp_image_merge_down(image, image.layers[0], 1)
        new_piece_layer_dam.name = piece_as_layer_name[:5] + 'D;' + piece_as_layer_name[7:]
        pdb.gimp_displays_flush()
        #debug(("L1664 renamed piece",piece_layer))
        #stoneNbr = fromCoordToPlace[piece_layer.name[7:]]
        #debug(("L1666 you got a new DAM at ", stoneNbr))



        return new_piece_layer_dam

    def moveStone(self, fromTo):
        saveQuestion = self.saveMoves.get_active() == 1
        #PKHF>OK 2apr debug(("L1674 START moveStone fromTo", fromTo)) #PKHG>TODO WRONG with black stone but white active!
        toMoove , naar = fromTo #all numbers!
        toMoove = toMoove #PKHG>??? 19feb int(toMoove)
        moveLayer = bord[toMoove]['layer']
        nameToChange = moveLayer.name
        forColor = nameToChange[:5]
        if saveQuestion:
            debug(("L1681 save picture by moveStone"))
            fp = open(gimp.directory + "\\dammen\\steps\\movements", "a")
            tmp = ""
            if len(fromTo) == 2:
                #tmp = str(fromTo[0]) + "-" + str(fromTo[1]) + ' '
                tmp = '{d[0]:2} - {d[1]:2} '.format(d=fromTo)
                fdebug(("L1685 stonenotatie", tmp))

            #PKHG>OLD???             json.dump(fromTo, fp)
            json.dump(tmp, fp)
            #json.dump(forColor[0], fp)  #PKHG>CHANGE [0] 04-24 15:20
            fp.write('\n')
            fp.close()
        nx, ny = fromPlaceToCoord[naar]
        mx, my = eval(nameToChange[7:])
        offx = nx - mx
        offy = ny - my
        pdb.gimp_layer_translate(moveLayer, offx, offy)
        changedName = nameToChange[:7] + str([nx, ny])
        moveLayer.name = changedName
        bord[toMoove]['layer'] = None

        theModeNow = self.check_alternating.get_active()
        whiteActive = self.whiteRadio.get_active()
        blackActive  = self.blackRadio.get_active()

        #PKHG>TODO 30mrtactiveColor = self.blackOrWhite.get_active()
        if theModeNow == 0:   #game-mode"
            if whiteActive:
                self.whiteRadio.set_active(False)
                self.blackRadio.set_active(True)
            else:
                self.whiteRadio.set_active(True)
                self.blackRadio.set_active(False)
        else:
            self.stoneEntry.set_text(str(naar))
            if changedName[:5] == 'black':
                self.whiteRadio.set_active(False)
                self.blackRadio.set_active(True)
                #self.blackOrWhiteValue = 'black'
            else:
                self.whiteRadio.set_active(True)
                self.blackRadio.set_active(False)
                #self.blackOrWhiteValue = 'white'

        pdb.gimp_displays_flush()
        automaticPic = self.automaticPicture.get_active() == 1
        if automaticPic:
            here = "PKHGTODO"  #PKHG>??? 7apr
            self.makeScreenshot(None)
        debug(("L1724 end of normal moving a stone to ", naar))
    def executeDamJumpsSeries(self, fromOverNaar):
        #PKHG>OK04-21 fdebug(("L1726  fromOverNaar", fromOverNaar))
        jumps = [[fromOverNaar[i],fromOverNaar[i + 1], fromOverNaar[i + 2]] for i in\
                 range(0, len(fromOverNaar), 3)]
        lenJumps = len(jumps)
        nrOfJumps = len(jumps)
        saveQuestion = self.saveMoves.get_active() == 1
        forColor = ""
        automaticPic = self.automaticPicture.get_active() == 1
        for jump in jumps:
            nrOfJumps -= 1
            jumper, toDelete, naar = jump
            jumpLayer = bord[jumper]['layer']
            deleteLayer = bord[toDelete]['layer']
            nameToChange = jumpLayer.name
            nx, ny = fromPlaceToCoord[naar]
            changedName = nameToChange[:7] + str([nx, ny])
            mx, my = eval(nameToChange[7:])
            offx = nx - mx
            offy = ny - my
            pdb.gimp_layer_translate(jumpLayer, offx, offy)
            forColor = jumpLayer.name[:5]
            #PKHG>NOTUSED??? otherColorNr = 1 if forColor == 'white' else 0
            jumpLayer.name = changedName
            bord[naar]['layer'] = jumpLayer
            bord[jumper]['layer'] = None
            image = gimp.image_list()[0]  #PKHG>NEW zie old boven
            image.remove_layer(deleteLayer)
            bord[toDelete]['layer'] = None
            pdb.gimp_displays_flush()
            if nrOfJumps:
                sleep(1)
            if automaticPic:
                here = "PKHG>TODO" #PKHG>??? 7apr
                self.makeScreenshot(None)
        if saveQuestion:
            debug(("L1761 save picture by executeDamJumpsSeries"))
            fp = open(gimp.directory + "\\dammen\\steps\\movements", "a")

            #PKHG>TODO waarom gaat dit niet 04-28

            #fromOverNaar = [1,3,4,89,6]
            tmp = [el for el in fromOverNaar]

            sprongLength = len(fromOverNaar)
            indsDel = [el for el in range(sprongLength,0,-3)]
            for i in indsDel[1:]: tmp.pop(i)
            #debug(("L1778 insDel", indsDel))
            #debug(("L1780 tmp now", tmp))
            sprongLength = len(tmp)
            start = "{d[0]:2}x{d[1]:2}"
            for i in range(2, sprongLength):
                tt =  "x{d[" + str(i) + "]}"
                start = start + tt
            debug(("L1786 start", start))
            tmpn = start.format(d=tmp)
            #tmp = start.format(d=indsDel)
            #debug(("L1781 sprong", tmpn))

            #print(tmp)
            #tmp = start.format(d=fromOverNaar)
            #json.dump(tmp)
            json.dump(tmpn, fp)
            #old json.dump(fromOverNaar, fp)
            #PKHG>OLD json.dump(forColor[0], fp)
            fp.write('\n')
            fp.close()

        automaticPic = self.automaticPicture.get_active() == 1
        self.execute_the_choice.hide()
        self.which_notation_entry.hide()
        self.label_notations.hide()
        self.tryMove.show()
        theModeNow = self.check_alternating.get_active()
        whiteActive = self.whiteRadio.get_active()
        blackActive  = self.blackRadio.get_active()

        if theModeNow == 0:   #game-mode"
            if whiteActive:
                self.whiteRadio.set_active(False)
                self.blackRadio.set_active(True)
            else:
                self.whiteRadio.set_active(True)
                self.blackRadio.set_active(False)
        #PKHG>OK debug(("L1784 returning from jumpsSeries"))
        lenFromOverNaar = len(fromOverNaar)
        #as long as there ar no loooon jumps
        #PKHG>OK debug(("L1787 check making a dam"))
        stonePosition = 0
        if lenFromOverNaar == 1 or lenFromOverNaar == 2:
            stonePosition = lenFromOverNaar[-1]
            color = bord[stonePosition]['layer'].name[:6]
            if color == 'white ' and stonePosition in range(1,6):
                #see the trailing blank!
                debug(("L1794 make " + str(stonePosition) + " a dam1"))
                self.makeThisStoneADam(None)
            elif color == 'black ' and stonePosition in range(46,51):
                debug(("L1797 make" +  str(stonePosition) + " dam!"))
                self.makeThisStoneADam(None)
        debug(("L1799 jumps done to ", stonePosition))
        return

    def executeThisJump(self, fromOverNaar): #NY jump OR Dam movement!
        #PKHG>TODO 27mrt forColor = 'black' if self.blackOrWhite.get_active() else 'white'
        if len(fromOverNaar) > 2:
            self.executeDamJumpsSeries(fromOverNaar)
        elif len(fromOverNaar) == 2: #not a jump but a move
            saveQuestion = self.saveMoves.get_active() == 1
            van, naar = fromOverNaar
            self.moveStone([van,naar])
            self.execute_the_choice.hide()
            self.which_notation_entry.hide()
            self.label_notations.hide()
            self.tryMove.show()
            return
        lenFromOverNaar = len(fromOverNaar)
        #as long as there ar no loooon jumps
        self.inititializeTheBord()
        if lenFromOverNaar == 3 or lenFromOverNaar == 6: #single or double jump
            stonePosition = fromOverNaar[-1]
            #PKHG>OK debug(("L1820 stonePosition", stonePosition))
            color = bord[stonePosition]['layer'].name[:6]
            if color == 'white ' and stonePosition in range(1,6):
                #see the trailing blank!
                self.makeDamEntry.set_text(str(stonePosition))
                self.makeThisStoneADam(None)
            elif color == 'black ' and stonePosition in range(46,51):
                self.makeDamEntry.set_text(str(stonePosition))
                self.makeThisStoneADam(None)


    def chooseYourJump(self, widget):
        #PKHG>TODO 27mrt self.followOnly = -1
        """ PKHG>???
        if self.damFirstOrderJumpsDict:
            multipleJumpPossible = True
        """
        #PKHG>ToDO 14mrt
        chooseFrom = self.jumpPossibilities
        #PKHG>OK debug(("L1839 chooseFrom", chooseFrom))
        self.jumpPossibilities = []
        which_jump = self.which_notation_entry.get_text()
        if which_jump.isdigit():
            which_jump = int(which_jump) - 1 #zero list start!
            if which_jump > len(chooseFrom):
                showMyMessage("not possible digit is TOO big!\nTry again")
                return
        else:
            showMyMessage(str(which_jump) + " is not a possible value")
            return
        yourChoice = chooseFrom[which_jump]
        if len(yourChoice) > 3 :
            startJump = yourChoice[:3]
            followPairs = [ [yourChoice[i-1],yourChoice[i], yourChoice[i+1]] for i in range(3, len(yourChoice),2)]
            #PKHG>OK fdebug(("L1854 startjump, followPairs", startJump, followPairs))
            for el in followPairs:
                startJump.extend(el)
            yourChoice = startJump
            debug(("L1858 yourChoice", yourChoice))
        self.executeThisJump(yourChoice)

    def nextStoneOtherColorToCaptureWithPossibilities(self, inputList, otherColor, direction):
        """
    inputList never empty list!
    eventually starting with empties
    Result: either None or [place of stone
        followed by emty places and direction}
        """
        result = None
        indexGoodStone = -1
        aStoneInDir = -1
        empties = listOfFollowingEmpties(inputList)
        if empties:
            if len(empties) < len(inputList):
                index  = inputList.index(empties[-1])
                #inputList = [inputList[index + 1]]  #existing stone!
                aStoneInDir = inputList[index + 1]
                indexGoodStone = index + 1
            else:
                return result #only empty diagonal following
        if bord[aStoneInDir]['layer'].name[:5] == otherColor:
            result = aStoneInDir
            empties = listOfFollowingEmpties(inputList[index +1 :]) #check!
            if empties: #succes!
                result = [inputList[0], indexGoodStone] + empties + [direction]
        return result

    def nextStoneOtherColor(self, inputList, otherColor):
        """
        inputList never empty list!
        eventually starting with empties
        """
        result = None
        empties = listOfFollowingEmpties(inputList)
        if empties:
            if len(empties) < len(inputList):
                index  = inputList.index(empties[-1])
                #inputList = [inputList[index + 1]]  #existing stone!
                aStoneInDir = inputList[index + 1]
            else:
                return result
        if bord[aStoneInDir]['layer'].name[:5] == otherColor:
            result = aStoneInDir
        return result
    '''
    def listOfFollowingEmpties(self, inputList):
        result = []
        for p in inputList:
            if bord[p]['layer'] == None:
                result.append(p)
                continue
            else:
                break
        return result
    '''

    def nextStoneOtherColorToCaptureWithPossibilities(self, inputList, otherColor, direction):
        """
        inputList never empty list!
        eventually starting with empties
        Result: either None or [place of stone
            followed by emty places and direction}
        """

        result = None
        indexGoodStone = -1
        aStoneInDir = -1
        empties = self.listOfFollowingEmpties(inputList)
        if empties:
            if len(empties) + 1  < len(inputList):
                index  = inputList.index(empties[-1])
                #inputList = [inputList[index + 1]]  #existing stone!
                aStoneInDir = inputList[index + 1]
                indexGoodStone = index + 1
            else:
                return result #only empty diagonal following
        if aStoneInDir == -1:
            return []
        if bord[aStoneInDir]['layer'].name[:5] == otherColor:
            result = aStoneInDir
            empties = self.listOfFollowingEmpties(inputList[index +1 :]) #check!
            if empties: #succes!
                result = [inputList[0], indexGoodStone] + empties + [direction]
        return result



    def  nextOtherColorStonePlusOneFree(self, places, otherColor):
        found = [places[0]]

        for i, place in enumerate(places[1:-1]):
            placeOfBoard = bord[place]['layer']
            if placeOfBoard == None:
                continue
            else:
                goodColor = placeOfBoard.name[:5] == otherColor
                if goodColor:
                    found.append(place)

                    for j, checkThisEmpty in enumerate(places[i + 2:]):

                        if bord[checkThisEmpty]['layer'] == None:
                            found.append(checkThisEmpty)
                        else:
                            break
        if len(found) > 1:
            return found
        else:
            return None
    def checkDiagonal(self, possiblePlaces, otherColor, direction):
        result = [direction, possiblePlaces[0]]
        possiblePlaces.pop(0)
        otherStoneFound = False
        emptiesStart = True
        emptiesAfter = False
        lenPossiblePlaces = len(possiblePlaces) - 1 #end i in loop below?!
        for i, place in enumerate(possiblePlaces):
            tmp = bord[place]
            if emptiesStart:
                if i == lenPossiblePlaces:
                    result = []
                else:
                    if tmp['layer'] == None:
                        if result[-1] != True:
                            result.append[True]
                        continue
                    elif tmp['layers'].name[:5] == otherColor:
                       otherStoneFound = True
                       result.append[place]
                       emptiesStart = False
                       continue
                    else:
                        result = []
                        break
            elif not emptiesAfter:
                if i == lenPossiblePlaces:
                    result = []
                else:
                    if bord[place]['layer'] == None:
                        result.append(place)
                        emptiesAfter = True
                        continue
            else:
                if bord[place]['layer'] == None:
                    result.append(place)
                    continue
                else:
                    result.append(direction)
                    break

        return result

    def damSprongDirection(self, damColor, start, direction):
        """
        result either empty = []
        or [direction, start , True or False (dep. empties), otherColorSton empties(if availabel)]
        """
        result = []
        otherColor = 'white' if damColor == 'black' else 'black'
        startBuren = bord[start]['buren']
        directionsStart = startBuren.keys()
        if direction in directionsStart:
            possiblePlaces = startBuren[direction]
            if len(possiblePlaces) > 2:
                #where =  self.nextStoneOtherColor(possiblePlaces[1:], otherColor)
                tmp = self.checkDiagonal(possiblePlaces, otherColor, direction)

    def nextDamJumpsOverOnePossibilities(self, damColor, start, direction):
        result = []
        otherColor = 'white' if damColor == 'black' else 'black'
        startBuren = bord[start]['buren']
        directionsStart = startBuren.keys()
        if direction in directionsStart:
            possiblePlaces = startBuren[direction]
            if len(possiblePlaces) > 2:
                where =  self.nextStoneOtherColor(possiblePlaces[1:], otherColor)
                if where and not possiblePlaces[-1] == where:
                    index = possiblePlaces.index(where)
                    inputList = possiblePlaces[index + 1:]
                    followingEmpties = self.listOfFollowingEmpties( inputList)
                    if followingEmpties:
                        #tmp = [start, where]
                        result = [ [start, where, el] for el in followingEmpties]
                        #tmp.extend(followingEmpties)
                        #debug(("L2044 tmp", tmp))
                        #result.append(tmp)
                        #return
                else:
                    return None
        if len(result) > 0:
            return result
        else:
            return None


    def thirdOrderJumps(self, secondOnes, forColor):
        result = []
        allpossibilities = []
        #example :('L2058 jump to check', [9, 14, 20, 25, 'SE', 27])
        reminder = []
        for jump in secondOnes:
            notThisDir = diag[jump[-2]] #Do not look back!
            newStarts = jump[2:-2]
            for startNew in newStarts:
                oneFound = 0
                emptiesDirections = bord[startNew]['buren'].keys()
                emptiesDirections.remove(notThisDir)
                for restDirect in emptiesDirections:
                    tmp = self.controlleDammen(forColor,
                                               bord[startNew]['buren'][restDirect], restDirect)
                    if tmp:
                        allpossibilities.append(tmp)
                        oneFound += 1
            if oneFound == 0:
                reminder.append(jump)
        return reminder

    """ EXAMPLE WITH damJumpMet2landingen.xcf white stones:
          ('L2078 jumpCheck', [[3, ['SW', 'SE'], 'D'], [36, ['NE', 'SE'], ' '],
                             [49, ['NE', 'NW'], ' '], [43, ['SW', 'NE', 'SE', 'NW'], ' '],
                             [48, ['NE', 'NW'], ' ']])
    """

    def secondOrderDamJumpCheck(self, stonesInGivenDir, forColor):
        found = False
        goodStone = -1
        result = [stonesInGivenDir[0]]
        for stone in stonesInGivenDir[1:]:
            stonelayer = bord[stone]['layer']
            if stonelayer == None:
                if goodStone > 0:
                    result.append(stone)
                continue
            colorWrong = stonelayer.name[:5] == forColor
            if colorWrong:
                break
            else:
                if goodStone > 0:
                    break
                else:
                    goodStone = stone
                    result.append(goodStone)
        if len(result) < 3:
            result = []
        return result


    def startDamJumpCheck(self, damStoneList, forColor):
        damJumpPossible = []
        for checkStone  in damStoneList:
            stoneNumber = checkStone[0]
            for thisDir in checkStone[1]:

                tmp = self.controlleDammen(forColor,
                                         bord[stoneNumber]['buren'][thisDir], thisDir)
                if tmp:
                    damJumpPossible.append(tmp)

        if damJumpPossible:
            """
            ('L2120 damJumpPossible now = ', [
            [27, 31, 36, 'SW'],
            [27, 18, 13, 9, 'NE'],
            [28, 39, 44, 50, 'SE'],
            [3, 14, 20, 25, 'SE']])
            """
            tel = 0
            jumpDictionary = {}
            for possible in damJumpPossible:
                tel += 1
                startStone = possible[0]
                captureStone = possible[1]
                startDirection = possible[-1]
                thisJumpEnds = possible[2:-1]
                jumpsThisCase = []
                for el in thisJumpEnds:
                    jumpsThisCase.append([startStone, captureStone, el])
                jumpDictionary[(startStone, startDirection)] = jumpsThisCase
                if tel == -11:
                    return jumpDictionary
            """
            ('L2141 damJumpPossible',
            {(27, 'SW'): [[27, 31, 36]],
            (28, 'SE'): [[28, 39, 44], [28, 39, 50]],
            (3, 'SE'): [[3, 14, 20], [3, 14, 25]],
            (27, 'NE'): [[27, 18, 13], [27, 18, 9]]})
            """
        return jumpDictionary

    def stopPlacesDamJumpInThisDiagonal(self, diagonal, forColor):
        lenDiagonal = len(diagonal)
        if lenDiagonal < 3:  #diag to short
            return []
        i = 1
        while (i < lenDiagonal) and (bord[diagonal[i]]['layer'] == None):
            i += 1
        if i == lenDiagonal:  #only empties
            return []
        if bord[diagonal[i]]['layer'].name[:5] == forColor: #stopping stone?
            return []
        result = [diagonal[0], diagonal[i]]   #now a empty MUST follow otherwise result = []
        for damStone in diagonal[i + 1:]: #check the rest
            if bord[damStone]['layer'] == None:
                result.append(damStone)   #solution at least one found
            else:
                break           #stone followed at once by a stone
        if len(result) > 2:
            return result       #deliver succeslist
        return []               # nothing possible



    def searchDamFirstOrderjumps(self, zeroOrderDict, forColor):
        damFirstOrderJumpsDict = {}
        possibilities = [el for el in zeroOrderDict.keys()]
        possibilities.sort()
        allFirstOrderJumps = []
        allHelpers = []
        for checkThis in possibilities:
            zeroJump = zeroOrderDict[checkThis]

            oldStart = zeroJump[0]
            startBordPlace = zeroJump[-1]
            forbiddenDir = diag[checkThis[1]] #do not look back!
            directions = bord[startBordPlace]['buren'].keys()
            directions.remove(forbiddenDir)

            helperForDirections = []
            for theDirection in directions:
                theDiagonal = bord[startBordPlace]['buren'][theDirection]
                tmp = self.stopPlacesDamJumpInThisDiagonal(theDiagonal, forColor)
                if tmp:
                    helperForDirections = [checkThis] #[oldStart, startBordPlace, theDirection]
                    for el in tmp:
                        helperForDirections.append(el)
                    helperForDirections.append(theDirection)
                    #debug(("L2196 helperForDirections = " , helperForDirections))
                    allHelpers.append(helperForDirections)
                #continue


        """
('L2202 allHelpers', [[(3, 'SE', 0), 20, 42, 47, 'SW'], [(3, 'SE', 1), 25, 30, 34, 'SW'], [(27, 'NE', 0), 13, 19, 24, 'SE'], [(27, 'NE', 1), 9, 14, 20, 25, 'SE']])

('L2204 zero order dam jumps', {(3, 'SE', 0): [3, 14, 20], (3, 'SE', 1): [3, 14, 25], (27, 'NE', 1): [27, 18, 9], (28, 'SE', 1): [28, 39, 50], (27, 'NE', 0): [27, 18, 13], (28, 'SE', 0): [28, 39, 44], (27, 'SW', 0): [27, 31, 36]})
        """

        for helper in allHelpers:

            #debug(("L2209 allHelpers = " , allHelpers))
            listOfZeroOrderJumpsAllowed = [el[0] for el in allHelpers]
            """
('L2212 listOfZeroOrderJumpsAllowed', [(3, 'SE', 0), (3, 'SE', 1), (27, 'NE', 0), (27, 'NE', 1)])
            """
            #newKey = helper[0] + (helper[-1])
            listOfPossibilities = helper[1:-1]
            jumpstart = [listOfPossibilities[0], listOfPossibilities[1]]
            rest = listOfPossibilities[2:]
            teller = 0
            for restPoint in rest:
                tmp = [el for el in jumpstart]
                tmp.append(restPoint)
                newKey = helper[0] + (helper[-1], teller)
                damFirstOrderJumpsDict[newKey] = tmp
                teller += 1
        """
        ('L2226 damFirstOrderJumpsDict', {
        (3, 'SE', 0, 'SW', 0): [20, 42, 47]
        (3, 'SE', 1, 'SW', 0): [25, 30, 34],
        (27, 'NE', 0, 'SE', 0): [13, 19, 24],
        (27, 'NE', 1, 'SE', 0): [9, 14, 20],
        (27, 'NE', 1, 'SE', 1): [9, 14, 25] })
        """

        return [listOfZeroOrderJumpsAllowed, self.damFirstOrderJumpsDict]

    def searchZeroOrderDamjumps(self, damStones, forColor):
        global damZeroOrderJumpsDict

        if damStones:
            tijdelijkResult = []
            damZeroOrderJumpsDict = {}
            for stoneWithDirs in damStones:
                thisStoneResult = []
                thisStone = stoneWithDirs[0]
                theseDirections = stoneWithDirs[1]
                for thisDirection in theseDirections:
                    diagToCheck = bord[thisStone]['buren'][thisDirection]
                    tmp = self.stopPlacesDamJumpInThisDiagonal(diagToCheck, forColor)
                    if tmp:
                        thisStoneResult.append([tmp, thisDirection])
                    continue
                if thisStoneResult:
                    for info in thisStoneResult:
                        stoneList = info[0]
                        direction = info[1]
                        lenstoneList = len(stoneList)
                        for i in range(0,lenstoneList - 2):
                            tmp = [el for el in stoneList[:2]]
                            key = (stoneList[0], direction, i)
                            jumpinfo = [stoneList[0], stoneList[1], stoneList[i+2]]
                            damZeroOrderJumpsDict[key] = jumpinfo
                continue


            if damZeroOrderJumpsDict:
                listOfZeroOrderJumpsAllowed, damFirstOrderJumpsDict = self.searchDamFirstOrderjumps(damZeroOrderJumpsDict, forColor)

                """
 ('L2269 damFirstJumpDict (nog wrong)', [(3, 'SE', 0), (3, 'SE', 1), (27, 'NE', 0), (27, 'NE', 1)])
                """
                showMyMessage("dubbel dam jumps available!")
                result = [damZeroOrderJumpsDict[el] for el in listOfZeroOrderJumpsAllowed]
            return result


    def searchPossibleJumps(self, image, stoneNumbers, forColor):
        otherColor = 'white' if forColor == 'black' else 'black'
        colorPiecesLayers = [bord[nr]['layer'] for nr in stoneNumbers if  bord[nr]['layer'].name[:5].startswith(forColor)]
        layerListDams = [el for el in colorPiecesLayers if el.name[5]  == 'D']
        if layerListDams:
            todo = 1
        layerListNormal = [el for el in colorPiecesLayers if el.name[5]  == ' ']
        if layerListNormal:
            todo = 2


        #allNormalJumpsUptoOrder2(layerListNormal, forColor)
        return "not yet"


        ######### to check which normal jamps are not allowed because of dubbel jumps (or more)
        zeroOrderDamJumps = []
        self.secondDamJumps = []
        #PKHF>OK 12mrt
        """
        ('L 1625 damJumpPossibleDict', {
        (27, 'SW'): [[27, 31, 36]],
        (27, 'NE'): [[27, 18, 13], [27, 18, 9]]})
        (28, 'SE'): [[28, 39, 44], [28, 39, 50]],
        (3, 'SE'): [[3, 14, 20], [3, 14, 25]],
        """
        return []

        if damJumpPossibleDict:
            ######### second dam jumps search
            possibleDubbelJumpStart = []
            jumpsWithoutSecond = []
            allReminders = []
            directionsToCheck = damJumpPossibleDict.keys()
            for thisDirection in directionsToCheck:

                for jump in damJumpPossibleDict[thisDirection]:
                    original = thisDirection[0]
                    notThisDir = diag[thisDirection[1]] #not looking back!
                    startNew = jump[-1]
                    oneFound = 0
                    emptiesDirections = bord[startNew]['buren'].keys()
                    emptiesDirections.remove(notThisDir)
                    for restDirect in emptiesDirections:
                        reminder = [original, startNew, restDirect]
                        maybeSecondDamJump = self.controlleDammen(forColor, bord[startNew]['buren'][restDirect], restDirect)

                        if maybeSecondDamJump:
                            if original not in possibleDubbelJumpStart:
                                possibleDubbelJumpStart.append(original)
                            maybeSecondDamJump.append(original)
                            self.secondDamJumps.append(maybeSecondDamJump)
                            oneFound += 1
                        if oneFound == 0:
                            allReminders.append(jump)


            #debug(("L2333 return"))
            #return [] #11mrt TODO


            """
            ('L 1686 self.secondDamJumps,', [
            [20, 42, 47, 'SW', 3],
            [25, 30, 34, 'SW', 3],
            [13, 19, 24, 'SE', 27],
            [9, 14, 20, 25, 'SE', 27]
                                          ]) looks good 12 mrt 0957
            """

            #('L2346  possibleDubbelJumpStart', [3, 27]) OK
            #return [] #12mrt TODO
            #PKHg>OK debug(("L2348 zeroOrderDamJumps", zeroOrderDamJumps ))
            zeroOrderDamJumps = [el[:-1] for el in zeroOrderDamJumps if el[0] in possibleDubbelJumpStart]
            """
            ('L2351 ZeroOrderJumps = ', [[3, 14, 25], [27, 18, 13], [27, 18, 9]]) er ontbreek 3 14 20???
            """
        ############ damJumps handeld now info available
        return []
        """
        ('L2356 jumpNormalCheck', [
        [11, ['SW', 'NE', 'SE', 'NW']],
        [49, ['NE', 'NW']],
        [43, ['SW', 'NE', 'SE', 'NW']],
        [48, ['NE', 'NW']]])
        """
        zeroNormalJumps = []
        if jumpNormalCheck:   #a list of forColor
            """ 3dammentestdubbelsprong7mrt.xcf
            ('L2365 normals ', [
            [11, ['SW', 'NE', 'SE', 'NW']],
            [43, ['SW', 'NE', 'SE', 'NW']],
            [48, ['NE', 'NW']]])
            """

            for possibleNormalJump in jumpNormalCheck:
                for thisDir in possibleNormalJump[1]:
                    """
                    ('L2374 dambord ', {'layer': <gimp.Layer 'white ;[100, 200]'>,
                    'buren': {'SW': [11, 16], 'NE': [11, 7, 2], 'SE': [11, 17, 22, 28, 33, 39, 44, 50],
                    'NW': [11, 6]}})
                    """

                    tmp = self.controlleNormal(forColor, bord[possibleNormalJump[0]]['buren'][thisDir],
                                               thisDir)

                    """
                    ('L2383 list thisdir: ', [11, 7, 2], 'NE') thisDir set to NE
                    """
                    if tmp:
                        zeroNormalJumps.append(tmp)


            """
            ('L2390 zeroNormalJumps now=',
            [[11, 7, 2, 'NE'],
            [43, 39, 34, 'NE'],
            [48, 42, 37, 'NW']])
            """

        secondNormalJumps = []
        secondOrderNormalStart = []
        if zeroNormalJumps:
            for jump in zeroNormalJumps:
                original = jump[0]
                notThisDir = jump[-1]
                startNew = jump[2]
                emptiesDirections = bord[startNew]['buren'].keys()
                emptiesDirections.remove(diag[notThisDir])  #remove where we came from (invers!)
                for thisDir in emptiesDirections:
                    tmp = self.controlleNormal(forColor, bord[startNew]['buren'][thisDir], thisDir)
                    if tmp:
                        if original not in secondOrderNormalStart:
                            secondOrderNormalStart.append(original)
                        tmp.append(original)
                        secondNormalJumps.append(tmp)
            zeroOrderJumpsDict = {}
            if secondNormalJumps:
                for el in secondNormalJumps:
                    zeroOrderJumpsDict[(el[-1],el[-2])] = el[:3]
            if secondNormalJumps:
                zeroNormalJumps = [el for el in zeroNormalJumps if el[0] in secondOrderNormalStart]
        zeroOrderNormalDict = {}
        for el in zeroNormalJumps:
            zeroOrderNormalDict[(el[0], el[-1])] = el[:-1]
        allZeroOrderJumpsDict = {}

        #zeroorder jumps shortened to what may be used!
        tmp = [el for el in zeroNormalJumps]
        tmp.extend(zeroOrderDamJumps)
        return tmp

    def inititializeTheBord(self):
        image = gimp.image_list()[0]
        allStoneLayers = [el for el in image.layers \
                      if el.name.startswith("black") or
                      el.name.startswith('white')]
        allAvailableStoneNumbers = []
        for layer  in allStoneLayers:
            tmp =  tuple(eval(layer.name[7:]))
            stoneNumber = fromCoordToPlace[tmp]
            bord[stoneNumber]['layer'] = layer
            allAvailableStoneNumbers.append(stoneNumber)
        for i in range(1,51):
            if i not in allAvailableStoneNumbers:
                bord[i]['layer'] = None
        return

    def controlleNormal(self, forColor, places, direction):
        otherColor = 'white' if forColor == 'black' else 'black'
        result = None
        if len(places) < 3:
            result = None
        else:
            start, toCapture, free = places[:3]
            toCLayer = bord[toCapture]['layer']
            if toCLayer == None:
                result = None
            elif toCLayer.name[:5] == forColor:
                result = None
            elif bord[free]['layer'] != None:
                result = None
            else:

                result = [start, toCapture, free, direction]

        return result



    def controlleDammen(self, forColor, places, direction):
        otherColor = 'white' if forColor == 'black' else 'black'
        res = []
        result = 'possible'
        for i in places:
            if bord[i]['layer'] == None:
                res.append(-1)
            else:
                res.append(bord[i]['layer'].name[:5])
        #length too short?
        if len(res) < 3 :
            result = []
        else:
            otherColorCount = res.count(otherColor)
            if otherColorCount == 0:
                result = []
            else:
                #stone to capture not at last place? and next one empty
                otherColorIndex = res.index(otherColor)
                if otherColorIndex == len(res) - 1:
                    result = []
                elif res[otherColorIndex + 1] != -1:
                    result = []
                else:
                    #is there a wrong stone before the to capture stone?
                    secforStone = res[1:].count(forColor)
                    result = 'possible'
                    if secforStone != 0:
                        forColorIndex = res.index(forColor, 1) #second otherColor stone
                        if forColorIndex < otherColorIndex:
                            result = [] #stone in the way
        if result != []:
            result = [places[0], places[otherColorIndex], places[otherColorIndex + 1]]
            rest = res[otherColorIndex + 2:]

            for i, el in enumerate(rest):
                if el == -1:
                    result.append(places[otherColorIndex + 2 + i])
                else:
                    break
            result.append(direction)
        return result

    def mainInteraction(self, widget):
        global bordDone
        """
        using the base UI
nextOtherColorStonePlusOneFree'
        """

        ''' tests
        tmp = self.img.layers
        self.inititializeTheBord()
        return
        '''

        if not bordDone:
            self.makeBord([])
            bordDone = True
        global jsonDone
        global allJumpDicts
        global damSecondOrderJumpsDict, damFirstOrderJumpsDict, damZeroOrderJumpsDict
        global normalSecondOrderJumpsDict, normalFirstOrderJumpsDict, normalZeroOrderJumpsDict
        try:
            saveQuestion = self.saveMoves.get_active() == 1
            if saveQuestion and not jsonDone:
                image = gimp.image_list()[0]
                image_name = image.name
                fp = open(gimp.directory + "\\dammen\\steps\\movements", "a")
                buildDateTime =  datetime.now().strftime("%y_%m_%d %H:%M")
                debug(("L2536 ",buildDateTime))
                json.dump(buildDateTime,fp)
                res = self.blackAndWhiteStones('both')
                json.dump(image_name, fp)
                json.dump(";;;",fp)
                json.dump(res,fp)
                fp.write('\n')
                fp.close()
                jsonDone = True
        except IOError as e:
            debugErr(e)
            showMyMessage(gimp.directory + '/dammen/steps/movements does not exist,\n\
            please create it ;-)\n\
            if you want to save steps!')
        self.inititializeTheBord()
        self.stoneInputValue = self.getStoneNumber() #PKHG 4apr self.stoneEntry.get_text()
        if not self.stoneInputValue.isdigit():
            showMyMessage("give a stone via its position on the bord (1 .. 50)")
            return

        self.setupMode = self.check_alternating.get_active()
        if self.setupMode:  #tijdelijk3maart
            self.tryMove.show()
        image = gimp.image_list()[0]
        allStoneLayers = [el for el in image.layers \
                      if el.name.startswith('black') or
                      el.name.startswith('white')]
        allAvailableStoneNumbers = []
        for layer  in allStoneLayers:
            tmp =  tuple(eval(layer.name[7:]))
            stoneNumber = fromCoordToPlace[tmp]
            bord[stoneNumber]['layer'] = layer
            allAvailableStoneNumbers.append(stoneNumber)
        for i in range(1,51):
            if i not in allAvailableStoneNumbers:
                bord[i]['layer'] = None

        self.stoneInputValue = self.getStoneNumber() #PKHG>4apr self.stoneEntry.getStoneNumber_text()
        if self.stoneInputValue == "0":
            showMyMessage("Please choose a bord-number from: 1 .. 50")
            return

        whiteColorQ = self.whiteRadio.get_active()
        if whiteColorQ:
            self.activeColorValue = 'white'
        else:
            self.activeColorValue = 'black'
        # in mainInteraction


        res = self.searchPossibleJumps(image,
                                 allAvailableStoneNumbers,
                                 self.activeColorValue)
        self.inititializeTheBord()
        forColor = self.activeColorValue

        forColorStones = self.blackAndWhiteStones(forColor)
        forColorDamStones = [el for el in forColorStones if bord[el]['layer'].name[5] == 'D']
        forColorNormalStones = [el for el in forColorStones if bord[el]['layer'].name[5] == ' ']

        normalJumpList = []
        for el in forColorNormalStones:
            normalJumpList.append([el])
        #PKHG>OK
        #PKHG>OK04-21 fdebug(("L2599 04-21  normalJumpList", normalJumpList))
        """ "17_04_20 11:53""checkNormalRound.xcf" OK
        "('L2601 RETURN normalJumpList', [[23]])"
        """
        normalJumpList = searchNormalZeroOrderJumps(normalJumpList, forColor)
        #PKHG>DBG         fdebug(("L2604  04-21  wit  normalJumpList", normalJumpList))
        """ "17_04_20 11:54""checkNormalRound.xcf"
        "('L2606  RETURN  wit  normalJumpList', [
        [23, 19, 14],
        [23, 29, 34],
        [23, 18, 12]])"
        """

        #if there are dams, make starting list
        damJumpList = []
        for el in forColorDamStones:
            damJumpList.append([el])

        #PKHG>DBG 04-18 15:30 debug(("L2617 damJumpList", damJumpList))
        #('L2618 damJumpList', [[2], [3], [46]])

        #set starting value for later while loop
        if damJumpList:
            damJumpList = searchDamGeneralOrderJumps(damJumpList, forColor)
        #PKHG>OK         fdebug(("L2623 damJumpList", damJumpList))
        # "17_04_20 11:57""checkNormalRound.xcf" "('L2624 damJumpList', [])" OK
        #debug(("L2625 forced return")); return
        oldDamJumpList = [] #if there is a real damjump, oldDamJumpList
        #will be set in the while loop

        #''' DBG 04-18 15:31
        #OK 17apr 0813 debug("forced return") ; return
        counter = 0
        #PKHG>???TODO
        #PKHG>OK04-21 fdebug(("L2633 normalJumpList, damJumpList", normalJumpList, damJumpList))
        """
        "17_04_20 11:59""checkNormalRound.xcf"
        "('L2636 normalJumpList, damJumpList', [
        [23, 19, 14], [23, 29, 34], [23, 18, 12]], [])"
        OK
        """

        while damJumpList and counter < 10:
            counter += 1
            oldDamJumpList = damJumpList[:]
            damJumpList = searchDamGeneralOrderJumps(damJumpList, forColor)
            #PKHG>OK04-21 fdebug(("L2645 damJumpList", damJumpList))

            #PKHG>DBG fdebug(("L2647 RETURN 10:26 damJumpList, oldDamJumpList", damJumpList, oldDamJumpList)) ; return
        damJumpDepth = 0
        if oldDamJumpList:
            damJumpDepth = len(oldDamJumpList[0])
            #PKHG>OK debug(("REURN damJumpDepth =",damJumpDepth/2)); return
        #PKHG>OK04-21
        #PKHG>OK04-21 fdebug(("L2653 11:04 normalJumpList", normalJumpList))
        """ "17_04_20 11:41""checkNormalRound.xcf"
        "('L2655 11:04 normalJumpList', [ OK
        [23, 19, 14],
        [23, 29, 34],
        [23, 18, 12]])"
        """

        oldNormalJumpList = []
        #PKHG>OK         fdebug(("L2662 RETURN normalJumpList", normalJumpList)); return
        """ "17_04_20 12:50""checkNormalRound.xcf" "('L2663 RETURN normalJumpList',
        [[23, 19, 14], [23, 29, 34], [23, 18, 12]])"OK

        """
        counter = 0 #finishing at least (maybe higher needed?)
        while (normalJumpList != []) and (counter < 10):
            #PKHG>OK fdebug(("L2669 RETURN normalJumpList", normalJumpList)); return
            """ "17_04_20 12:52""checkNormalRound.xcf"
"('L2671 RETURN normalJumpList', [[23, 19, 14], [23, 29, 34], [23, 18, 12]])"
            """
            counter += 1
            oldNormalJumpList = [el for el in normalJumpList]
            tmp = [el for el in normalJumpList]
            #PKHG>OK fdebug(("L2676 oldNormalJumpList", oldNormalJumpList, tmp, tmp == oldNormalJumpList))
            """ "17_04_20 12:56""checkNormalRound.xcf"
"('L2678 oldNormalJumpList', [[23, 19, 14], [23, 29, 34], [23, 18, 12]], [[23, 19, 14], [23, 29, 34], [23, 18, 12]], True)" OK
            """

            normalJumpList = searchNormalGeneralOrderJumps(normalJumpList, forColor)
            #PKHG>OK04-21 fdebug(("L2682 counter normalJumpList oldNormalJumpList ",counter, normalJumpList, oldNormalJumpList, normalJumpList))


            """"17_04_20 12:39""checkNormalRound.xcf"
"('L2686 counter normalJumpList oldNormalJumpList ', 1, None, [[23, 19, 14], [23, 29, 34], [23, 18, 12]])"
            """

            """ "17_04_19 11:28""[Untitled]""('L2689 counter normalJumpList oldNormalJumpList ', 2, [],
            [[23, 18, 12, 17, 21]])"
            """

        #PKHG>DBGOK
        #PPKHG>OK fdebug(("L2694  after while normalJumpList",normalJumpList))
        normalJumpDepth = 0

        if oldNormalJumpList:
            normalJumpDepth = len(oldNormalJumpList[0])
            if normalJumpDepth < damJumpDepth:
                oldNormalJumpList = []
            elif damJumpDepth < normalJumpDepth:
                oldDamJumpList = []
        #PKHG>OK debug(("RETURNnormalJumpDepth", normalJumpDepth)); return


        #PKHG>OK04-21 fdebug(("L2706 ",oldNormalJumpList, oldDamJumpList))
        """ "17_04_20 07:48""3dams1cannotjump_3xcERRORf.xcf"
"('L2708 RETURN oldies', [], [])"
        """

        if damJumpList:
            damJumpList = searchDamGeneralOrderJumps(damJumpList, forColor)
            #PKHG>OK04-21 fdebug(("L2713 damJumpList", damJumpList))
        ''' TEST STEPWISE
        oldDamJumpList = damJumpList
        if damJumpList:
            oldDamJumpList = damJumpList
        if damJumpList:
            damJumpList = searchDamGeneralOrderJumps(damJumpList, forColor)
            #PKHG>OK04-21 fdebug(("L2720 damJumpList", damJumpList))
            if damJumpList:
                oldDamJumpList = damJumpList
        if damJumpList:
            damJumpList = searchDamGeneralOrderJumps(damJumpList, forColor)
            #PKHG>OK04-21 fdebug(("L2725 damJumpList", damJumpList))
            if damJumpList:
                oldDamJumpList = damJumpList

        if damJumpList:
            damJumpList = searchDamGeneralOrderJumps(damJumpList, forColor)
            #PKHG>OK04-21 fdebug(("L2731 RETURN!!!!!!!! damJumpList", damJumpList))
            if damJumpList:
                oldDamJumpList = damJumpList
        '''
        #debug(("L2735 forced RETURN damJumpList", damJumpList));return
        #debug(("L2736 RETURN  oldNormalJumpList , oldDamJumpList", oldNormalJumpList, oldDamJumpList)) ; return
        """ ('L2737 40-20 08:56 return  oldNormalJumpList , oldDamJumpList', [], [])
        """
        jumpList = []

        ''' see below
        for el in oldDamJumpList:
            debug(("L2743 el", el))
            jumpList.append(el)
        for el in oldNormalJumpList:
            debug(("L2746 el", el))
            jumpList.append(el)
        '''

        #PKHG>OK 04-20 09:44 debug(("L2750 RETURN normalJumpList", oldNormalJumpList)); return
        #06-24 08:0('L2751 return  oldNormalJumpList , oldDamJumpList', [], [])

        """ 04-19 10:36 ('L2753 return normalJumpList', [[23, 18, 12], [38, 42, 47]])
        ('L2754 return normalJumpList', [[26, 31, 37, 32, 28, 23, 19]]) OK
        """
        jumpList = oldDamJumpList
        if oldNormalJumpList:
            jumpList.extend(oldNormalJumpList)
        jumpListDams = []
        jumpListNormal = []

        #PKHG>OK        debug(("L2762 RETURN jumpList", jumpList)); return
        #PKHG>OK 17apr -8:15 ;return
        if 'notation' not in locals():
            notation = ""
        else:
            notation = ""

        #OLD if jumpList:
        #        debug(("L2770 RETURN jumpList", jumpList)); return
        """ 04-19 11:30
        ('L2772 RETURN jumpList', [[26, 31, 37, 32, 28, 23, 19]])

        ('L2774 RETURN jumpList', [[23, 18, 12, 17, 21]])
        ('L2775 RETURN jumpList', [])
        """
        if jumpList:
            for i, jump in enumerate(jumpList):
                notation += str(i + 1) + ": " + str(jump) + str('\n')
            #PKHG>OK04-21 fdebug(("L2780 notation", notation))
            self.label_notations.show()
            self.label_notations.set_text(notation)
            self.tryMove.hide()
            self.which_notation_entry.show()
            self.which_notation_entry.set_text(str(i + 1))
            self.jumpPossibilities = jumpList #PKHG>23mrt????
            self.execute_the_choice.show()
        else:  #NORMAL move ment
            #PKHG>OK
            #PKHG>OK04-21 f
            debug(("L2791 04-20 09:45  no capture jump"))
            van = int(self.stoneInputValue)
            vanEmpty = bord[van]['layer'] == None
            if vanEmpty:
                showMyMessage("no stone at " + str(van) + "\ntry again please")
                return
            infoColor = bord[van]['layer'].name[:5]
            color = self.activeColorValue #self.blackOrWhiteValue
            if color != infoColor:
                showMyMessage("activeColor unequal to stone color\nchange either color or stone please")
                return

            direction = self.rightOrLeftValue
            damDirection = self.damDirectionChoice #self.four_directions.get_active()
            #tmp = [['SE',0],['SW',1],['NE',2],['NW',3]])
            #tmp = ['SE','SW','NE','NW']
            #damDirection = tmp[damDirection]

            self.stoneInputValue = int(self.stoneInputValue)
            if self.stoneInputValue in range(1, 51):
                layer = bord[self.stoneInputValue]['layer']
            else:
                showMyMessage("wrong place! A stone on 1..51.\nTry again please")
                return
            if layer == None:
                showMyMessage("no stone at " + str(self.stoneInputValue) + "\n Try again")
                return
            aDam = layer.name[5] == 'D'

            dirsOfStone = bord[self.stoneInputValue]['buren']
            #PKHG>TODO??? yet not? fdebug(("L2821 04-20 09:45  dirsOfStone",dirsOfStone))
            """ "17_04_20 10:06""3dams1cannotjump_3xcERRORf.xcf"

            dam rom 46 to 41 placed setupmode!!!!

            "('L2826 04-20 09:45  dirsOfStone', this is OK
            {'SW': [41, 46],
            'NE': [41, 37, 32, 28, 23, 19, 14, 10, 5],
            'SE': [41, 47],
            'NW': [41, 36]})"
            """
            #PKHG>OK             debug("L2832 RETURN"); return
            if aDam:
                tmpdir = ['SE','SW','NE','NW']
                #new 04-20 10:13
                #NOOOO dirsOfStone = bord[self.stoneInputValue]['buren']
                #NO   fdebug(("L2837 04-20 10:15  dirsOfStone",dirsOfStone))
                direction = self.damDirectionChoice #tmpdir[self.four_directions.get_active()]

                if direction not in dirsOfStone.keys():
                    showMyMessage("direction " + direction + " is not possible\
                    \nTry different (move) please")
                    return
                possibleOnes = bord[self.stoneInputValue]['buren'][direction]
                if len(possibleOnes) == 2:
                    #minimum length is 2 now length is excluded above!
                    #only ONE possibility
                    naarD = possibleOnes[1]
                    move1 = naarD if (bord[possibleOnes[1]]['layer'] == None)\
                        else None
                    if move1:
                        fromTo = [van, naarD]
                        self.moveStone(fromTo)
                        return
                    else:
                        showMyMessage(str(naarD) + " is not empty\nTry differently")
                        return
                else: #diagonal contains more then 2 possibilities now
                    tmp = []
                    tmp = listOfFollowingEmpties(possibleOnes)
                    #PKHG>OK fdebug(("L2861 RETURN tmp", tmp)); return
                    """
                    for place in possibleOnes[1:]:
                        #PKHG>TODO???04-20 08:48 call function
                        tmp = listOfFollowingEmpties(possibleOnes)
                        debug(tmp)
                        '''
                        move1 = place if (bord[place]['layer'] == None)\
                        else None
                        if move1:
                            tmp.append(move1)
                        else:
                            break
                        '''
                    #PKHG>OK fdebug(("L2875 RETURN two versions secondTmp, tmp", secondTmp, tmp)); return
                    """

                    if len(tmp) == 1:
                        fromTo = [van, tmp[0]]
                        self.moveStone(fromTo)
                        return
                    else: #more places ...

                        choices = [[van, el] for el in tmp]
                        #PKHG>OK fdebug(("L2885 RETURN tmp and choices",tmp, choices)) ; return
                        """"17_04_20 09:34""3dams1cannotjump_3xcERRORf.xcf"
                        "('L2887 RETURN tmp and choices',
                        [41, 37], [[46, 41], [46, 37]])"
                        """


                        self.jumpPossibilities = choices
                        #not real jumps but choosYourJump checks on length, 2!
                        #PKHG>OK fdebug(("L2894 forced RETURN choices",choices)) ; return
                        """ "17_04_20 09:38""3dams1cannotjump_3xcERRORf.xcf"
                        "('L2896 forced RETURN choices', [[46, 41], [46, 37]])"
                        """
                        self.execute_the_choice.show() #==> chooseYourJump
                        for i, pair  in enumerate(choices):
                            #PKHG>OK fdebug(("2666 RETURN i sprongList", i , choices)) ; return
                            tmpPair = str(pair)
                            notation += str(i + 1) + ": " + tmpPair + str('\n')
                            #PKHG>OK debug(("L2903 notation = ", notation))
                        self.label_notations.show()
                        self.label_notations.set_text(notation)
                        self.tryMove.hide()
                        self.which_notation_entry.show()
                        self.which_notation_entry.set_text('1')
                        self.execute_the_choice.show() #==> chooseYourJump
                        return
                return
            else: #normal stone to move
                dirsOfStone = bord[self.stoneInputValue]['buren']
                fromTo = None
                if color == 'black':
                    if direction == 'right':
                        direction = 'SE'
                    else:
                        direction = 'SW'
                    if direction in dirsOfStone.keys():
                        ttcheckmp = dirsOfStone[direction]

                        if bord[ttcheckmp[1]]['layer'] == None:
                            fromTo = ttcheckmp[:2] #[van, ttcheckmp[1]]
                        else:
                            showMyMessage("occupied!\nTry differently please!")
                            return
                    else:
                        showMyMessage( direction + " is impossible\nTry different move plaese!")
                        return
                    if fromTo:
                        self.moveStone(fromTo)

                elif color == 'white':
                    if direction == 'right':
                        direction = 'NE'
                    else:
                        direction = 'NW'
                    if direction in dirsOfStone:
                        ttcheckmp = dirsOfStone[direction]
                        if bord[ttcheckmp[1]]['layer'] == None:
                            fromTo = ttcheckmp[:2] #[van, ttcheckmp[1]]
                        else:
                            showMyMessage("occupied!\nTry differently please!")
                            return
                    if fromTo:
                        self.moveStone(fromTo)
            stonePosition = fromTo[-1]
            #pdb.gimp_displays_flush()
            self.inititializeTheBord()
            ###PKHG>TODO wh is this a layer == None?
            color = bord[stonePosition]['layer'].name[:6]
            if color == 'white ' and stonePosition in range(1,6):
                self.makeDamEntry.set_text(str(stonePosition))
                self.makeThisStoneADam(None)
            elif color == 'black ' and stonePosition in range(46,51):
                self.makeDamEntry.set_text(str(stonePosition))
                self.makeThisStoneADam(None)
            debug(("L2959 end of normal moving a stone to ", stonePosition))
            return

class Damdevellop28apr0StarterClass(gimpplugin.plugin):
    def start(self):
        print("\n------------------Damdevellop28apr0StarterClass called\n")
        gimp.main(self.init, self.quit, self.query, self._run)
    def init(self):
        pass
    def quit(self):
        print("\n------------------Damdevellop28apr0StarterClass ended\n")
        pass
    def query(self):
        cright = "PeterPKHG "
        date = "1feb2017"
        plug_descr = ("gtk start a mini Dialog")
        plug_params = [(PDB_INT32, "run_mode", "Run mode"), (PDB_IMAGE, "image", "Input image"),]
        gimp.install_procedure("damdevellop_DamNew", plug_descr, plug_descr, "PeterPKHG", cright, date,
                               "<Image>/GTK/Dam22nov19", "RGB*, GRAY*", #
                               PLUGIN, plug_params,[]) #

    def damdevellop_DamNew(self, runmode, img):
        Damdevellop28apr0(runmode, img)


if __name__ == '__main__':
    damClass = Damdevellop28apr0StarterClass().start()

"""
for Emacs-Users to rename labels Lxxx -> Lyyy  yyy = number of THIS line
Command: last-kbd-macro
Key: none

Macro:

ESC
C-s 			;; isearch-forward
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


(fset 'renumberLlabels'
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ([escape 19 76 91 48 45 57 93 43 return escape 58 40 105 110 115 101 114 116 32 42 119 104 97 116 45 108 105 110 101 41 backspace backspace backspace backspace backspace backspace backspace backspace backspace backspace backspace 40 119 104 97 116 45 108 105 110 101 41 41 return 18 76 18 return escape 100 4 76] 0 "%d")) arg)))

copy the list (fset ...) then esc : Ctr y to set the name then make a macro using cltr x renumberLlabels then
to to the top and execute (thereafter e suffeces)
(fset 'renumberLlabels'
   (lambda (&optional arg) "Keyboard macro." (interactive "p") (kmacro-exec-ring-item (quote ([escape 19 76 91 48 45 57 93 43 return escape 58 40 105 110 115 101 114 116 32 42 119 104 97 116 45 108 105 110 101 41 backspace backspace backspace backspace backspace backspace backspace backspace backspace backspace backspace 40 119 104 97 116 45 108 105 110 101 41 41 return 18 76 18 return escape 100 4 76] 0 "%d")) arg)))

"""
#http://www.ericsdamsite.com/problemen1-10.htm
#http://toernooibase.kndb.nl/applet/oerterpapplet2.0/themes/pieceimages/ plaatjes
#http://damweb.nl/hdewaard/rubriek50a.html
#http://laatste.info/bb3/viewtopic.php?t=3819
#turbodambase tbd+PTR75 spamPTR+tbd7517
#http://windames.free.fr/page3_e.html how programs think
