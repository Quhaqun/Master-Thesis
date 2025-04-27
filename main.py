
"""
@author: bwahn

"""
#from cgitb import handler

import pygame
import asyncio
import numpy
from pyexpat.errors import messages

from parameters_JointMOT_HCI_HH2 import *
from functions_JointMOT_HCI_HH2 import *
pygame.init()



import platform

if sys.platform == "emscripten":
    import io
    import csv
    import json
    import sys
    import js

    # RequestHandler that works in both local and WASM (browser) environments
    class RequestHandler:
        """
        WASM compatible request handler
        auto-detects emscripten environment and sends requests using JavaScript Fetch API
        """

        GET = "GET"
        POST = "POST"
        _js_code = ""
        _init = False

        def __init__(self):
            self.no_identity = False
            self.is_emscripten = sys.platform == "emscripten"
            if not self._init:
                self.init()
            self.debug = True
            self.result = None

            if not self.is_emscripten:
                try:
                    import requests
                    self.requests = requests
                except ImportError:
                    pass

        def init(self):
            if self.is_emscripten:
                self._js_code = """
        window.Fetch = {}
        window.Fetch.POST = function * POST(url, data) {
            var request = new Request(url, {
                headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
                method: 'POST',
                body: data
            });
            var content = 'undefined';
            fetch(request)
            .then(resp => resp.text())
            .then((resp) => {
                content = resp;
            })
            .catch(err => {
                console.log("Error:", err);
            });
            while(content == 'undefined') { yield; }
            yield content;
        }
        """
                try:
                    platform.window.eval(self._js_code)
                except AttributeError:
                    self.is_emscripten = False

        async def post(self, url, data=None):
            if data is None:
                data = {}

            if self.is_emscripten:
                content = await platform.jsiter(platform.window.Fetch.POST(url, json.dumps(data)))
                self.result = content
            else:
                self.result = self.requests.post(url, json=data, headers={"Accept": "application/json",
                                                                          "Content-Type": "application/json"}).text
            return self.result

async def Main():
    EXPPATH = os.path.dirname(os.path.abspath(__file__))
    SUBDIR = "%s/Data/Pair%s/" %(EXPPATH,SUB)
    csvfile = "Pair%s.csv" % SUB
    path = SUBDIR + csvfile

    Subnum = int(SUB)

    header = ['objx_0','objy_0','objx_1','objy_1','objx_2','objy_2','objx_3','objy_3','objx_4','objy_4',
    'objx_5','objy_5','objx_6','objy_6','objx_7','objy_7','objx_8','objy_8','objx_9','objy_9',
    'objx_10','objy_10','objx_11','objy_11','objx_12','objy_12','objx_13','objy_13','objx_14','objy_14',
    'objx_15','objy_15','objx_16','objy_16','objx_17','objy_17','objx_18','objy_18',
    'Subnum','Trial','player1correct','player1incorrect',
    'player2correct','player2incorrect','paircorrect','pairincorrect',
    'player1total', 'player2total','pairtotal','doublesel',
    'Markalltime','AGE','GENDER','HANDEDNESS','CONDITION',
    'Experiment','ChosenHuman','ChosenAI',
    'selobj1','selobj2','selobj3','selobj4','selobj5','selobj6',
    'selobj7','selobj8','selobj9','selobj10','selobj11','selobj12',
    'selobj13','selobj14','selobj15','selobj16','selobj17','selobj18','selobj19',
    'selobjother1','selobjother2','selobjother3','selobjother4','selobjother5','selobjother6',
    'selobjother7','selobjother8','selobjother9','selobjother10','selobjother11','selobjother12',
    'selobjother13','selobjother14','selobjother15','selobjother16','selobjother17','selobjother18',
    'selobjother19','Selectiontime','ReactiontimeSelection','ReactiontimeMarkall']

    #check if subject folder exists, if not make it:
    if not os.path.exists(SUBDIR):
        os.makedirs(SUBDIR)
        with open(path, 'w') as f:
            wr = csv.writer(f)
            wr.writerow(header)

    running = True

    # XXX MAKI look straight?
    if PARTNER == "Robot":
        send_request(0)

    await displayTextcenter(Introduction, shiftup=HEIGHT/4, fontcolor = BLACK)
    await displayTextcenter(Rights_Participant, shiftup=HEIGHT/3, fontcolor = BLACK)

    for trial in range(0,TRIALS):

        SHOWSELECTIONS = TRIALS_SELECTIONSINFO[trial]
        CURTRIALTYPE = TRIALS_TYPE[trial]

        if (CURTRIALTYPE == "SoloTrainingStart"):
            await displayTextcenter(Instruction_Text_Solo, shiftup=HEIGHT/8, fontcolor = BLACK)
            await displayTextcenter(Announce_Solo_Training, shiftup=0, fontcolor = BLACK)
            CONDITION = "SoloTraining"

        if (CURTRIALTYPE == "SoloStart"):
            await displayTextcenter(Announce_Solo_experiment, shiftup=HEIGHT/8, fontcolor = BLACK)
            CONDITION = "Solo"

        if (CURTRIALTYPE == "JointTrainingStart"):
            await displayTextcenter(Instruction_Text_Joint, shiftup=HEIGHT/4, fontcolor = BLACK)

            if PARTNER == "Confederate":
                await displayTextcenterWait(Connectingpartner,waitforconnect, shiftup=HEIGHT/4, fontcolor = BLACK)
                await displayTextcenter(Connectingpartner_success, shiftup=HEIGHT/4, fontcolor = BLACK)

            await displayTextcenter(Announce_Joint_training, shiftup=0, fontcolor = BLACK)

            CONDITION = "JointTraining"

        if (CURTRIALTYPE == "Jointstart"):
            await displayTextcenter(Announce_Joint_experiment, shiftup=HEIGHT/8, fontcolor = BLACK)
            CONDITION = "Joint"

        pygame.event.clear()
        data = []
        objects = []
        initialobjpos = [(CX,CY)]

        for n in range(0,OBJNUM):
            conflict = 1
            posx = random.randint(int(OBJRADIUS), int(WIDTH - OBJRADIUS))
            posy = random.randint(int(OBJRADIUS), int(HEIGHT - OBJRADIUS))
            postmp = (posx,posy)
            while conflict:
                conflict = 0
                for checkpos in initialobjpos:
                    if collide_points(postmp,checkpos,6*OBJRADIUS):
                        conflict = 1
                        posx = random.randint(int(OBJRADIUS), int(WIDTH - OBJRADIUS))
                        posy = random.randint(int(OBJRADIUS), int(HEIGHT - OBJRADIUS))
                        postmp = (posx,posy)

            initialobjpos.append(postmp)

            object = Object((int(posx),int(posy)),OBJRADIUS,OBJSPEED)
            object.speed = int(random.uniform(OBJSPEEDRANGE[0],OBJSPEEDRANGE[1]))

            object.angle = random.uniform(0, math.pi*2)
            object.angledeg = int(float(math.degrees(object.angle)))
            object.angle = math.radians(object.angledeg)
            objects.append(object)


        collect_dist = []

        running = True

        SCREEN.fill(BGCOLOR)
        fixcross()
        for object in objects:
            object.display()
            data.append(object.x)
            data.append(object.y)

        pygame.display.flip()
        #pygame.time.delay(2000)

        SCREEN.fill(BGCOLOR)
        fixcross()

        if EXPCHOICE == "1" or EXPCHOICE == "2":
            for object in objects[0:NUMTAR]:
                object.thickness = 0
                object.colour = WHITE
            for object in objects:
                object.display()

        pygame.display.flip()

        fpsClock = pygame.time.Clock()
        framecountshowtar = 0

        # introduce selection here
        assign_corrident, assign_rt, assignperf, assignorder, assignobjidx, assigncor_objidx, assignwrong_objidx, objects, ReactiontimeSelection = await markall(objects,"selection",Subnum, trial, SUBDIR)
        # assigned to AI, complement of assignobjidx
        ai_assigned_targets = list(set([0,1,2,3,4,5]) ^ set(assignobjidx))
        print(ai_assigned_targets)

        assigned_ai_tars = []
        for a in ai_assigned_targets:
            assigned_ai_tars.append(objects[a])

        if SHOWSELECTIONS == True:
            for object in assigned_ai_tars:
                object.thickness = 0
                object.colour = COLOROTHER
                object.display()
            pygame.display.flip()
            pygame.time.delay(2000)

            if CONDITION == "JointTraining" or CONDITION == "Joint":
                pygame.time.delay(5000)

        for object in objects[0:NUMTAR]:
            object.thickness = 1
            object.colour = BLACK

        # XXX MAKI start moving eyes?
        if PARTNER == "Robot":
            send_request(1)

        objects = await MOT(objects, trial, Subnum, SUBDIR)

        # XXX MAKI stop moving eyes?
        if PARTNER == "Robot":
            send_request(0)

        corrident, mark_rt, totalperf, selectorder, selobjidx, selcor_objidx, selwrong_objidx, objects, ReactiontimeMarkall = await markall(objects,"markall",Subnum, trial, SUBDIR)


        doubleselected = []

        obspos_other = ai_assigned_targets

        if NUMTAR != 0:
            for o in obspos_other:
                objects[o].thickness = 0
                objects[o].colour = COLOROTHER
                if o in selobjidx:
                    objects[o].thickness = 0
                    objects[o].colour = COLORME
                    objects[o].size = OBJRADIUS/2
                    doublesel_object = Object((objects[o].x,objects[o].y),OBJRADIUS,OBJSPEED)
                    doublesel_object.thickness = 0
                    doublesel_object.colour = COLOROTHER
                    doubleselected.append(doublesel_object)

        if NUMTAR != 0:
            fixcross()
            for doublesel_object in doubleselected:
                doublesel_object.display()
            for object in objects:
                object.display()

        # build into delay for targets selections XXX check old data,
        # average time per selection, then substract time from mark_rt,
        # and use that as delay if positive
        partnerselectiontime = len(ai_assigned_targets) * timeperselection
        delaypartner = partnerselectiontime - mark_rt

        if PARTNER == "Confederate":
            if delaypartner > 0 and len(ai_assigned_targets) > 0:
                delaycalc = int(round(1000 * delaypartner))
                if CONDITION == "JointTraining" or CONDITION == "Joint":
                    pygame.time.delay(delaycalc)

        if SHOWSELECTIONS == True:
            pygame.display.flip()
            overlapfeedback = True
            while overlapfeedback:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_SPACE:
                            overlapfeedback = False
                await asyncio.sleep(0)
            SCREEN.fill(BGCOLOR)
            pygame.display.flip()


        SCREEN.fill(BGCOLOR)
        fixcross()

        player1correct = 0
        player1incorrect = 0
        player2correct = 0
        player2incorrect = 0

        paircorrect = 0
        pairincorrect = 0
        player1total = 0
        player2total = 0
        pairtotal = 0
        doublesel = 0

        for object in objects[0:NUMTAR]:
            if object.colour != BLACK:
                if object.size == OBJRADIUS/2:
                    doublesel += 1
                    player1correct += 1
                    player2correct += 1
                elif object.colour == COLOROTHER:
                    player2correct += 1
                elif object.colour == COLORME:
                    player1correct += 1

                object.colour = GREEN
                object.size = OBJRADIUS
                paircorrect += 1

        for object in objects[NUMTAR:]:
            if object.colour != BLACK:
                if object.size == OBJRADIUS/2:
                    doublesel += 1
                    player1incorrect += 1
                    player2incorrect += 1
                elif object.colour == COLOROTHER:
                    player2incorrect += 1
                elif object.colour == COLORME:
                    player1incorrect += 1

                object.colour = RED
                object.size = OBJRADIUS
                pairincorrect += 1

        pairtotal = paircorrect - pairincorrect
        player1total = player1correct - player1incorrect
        player2total = player2correct - player2incorrect

        if CONDITION == "JointTraining" or CONDITION == "Joint":
            if SHOWTEAMSCORE == True :
                feedbackscore = [" "," ", "Team: %d P." %pairtotal," "," "]
                readyscore = await displayTextcenter(feedbackscore,shiftup=HEIGHT/4, fontcolor = BLACK)
                SCREEN.fill(BGCOLOR)
                pygame.display.flip()

        data.append(Subnum)
        data.append(trial)
        data.append(player1correct)
        data.append(player1incorrect)
        data.append(player2correct)
        data.append(player2incorrect)
        data.append(paircorrect)

        data.append(pairincorrect)
        data.append(player1total)
        data.append(player2total)
        data.append(pairtotal)
        data.append(doublesel)

        data.append(mark_rt)
        data.append(AGE)
        data.append(GENDER)
        data.append(HANDEDNESS)
        data.append(CONDITION)
        data.append(EXPCHOICE)

        # assign_corrident, assign_rt, assignperf, assignorder, assignobjidx, assigncor_objidx, assignwrong_objidx
        data.append(assignobjidx)
        data.append(ai_assigned_targets)

        for i in range(0,len(selobjidx)):
            data.append(selobjidx[i])
        for i in range(len(selobjidx)+1,OBJNUM+1):
            data.append(float('nan'))

        for i in range(0,len(obspos_other)):
            data.append(obspos_other[i])
        for i in range(len(obspos_other)+1,OBJNUM+1):
            data.append(float('nan'))

        data.append(assign_rt)
        data.append(ReactiontimeSelection)
        data.append(ReactiontimeMarkall)

        with open(path, 'a') as f:
            wr = csv.writer(f)
            wr.writerow(data)

        if sys.platform == "emscripten":
            output = RequestHandler()
            # Define the URL and data for the POST request
            url = "http://127.0.0.1:5000/submit_trial"
            writeheader = True
            # Send the POST request
            try:
                message = "test"
                message = await output.post(url, {
                                                "writeheader" : writeheader,
                                                "csvfile" : csvfile,
                                                "Subnum" : Subnum,
                                                "row": data          # `data` is your list of values (header or trial)
                                            })
                print(message)
            except:
                print("fail")
                pass

    await displayTextcenter(EndExperiment, shiftup=0, fontcolor = BLACK)
    await asyncio.sleep(0)
    pygame.quit()
    sys.exit()

asyncio.run(Main())