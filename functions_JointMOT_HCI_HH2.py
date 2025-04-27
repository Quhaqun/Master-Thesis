"""
@author: bwahn

"""


# functions for server

import pygame
import random
import math
import time
import sys
import numpy
import csv
import os
import pickle
import asyncio

from parameters_JointMOT_HCI_HH2 import *
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

if PARTNER == "Robot":
    def send_request(number):
        try:
            requests.post(settings["FLASK_URL"] + str(number), timeout=0.001)
        except requests.exceptions.RequestException:
            pass  # Ignore any request errors

def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None

def count_unique(keys):
    uniq_keys = numpy.unique(keys)
    bins = uniq_keys.searchsorted(keys)
    return uniq_keys, numpy.bincount(bins)

async def displayTextcenter(textlist,shiftup, fontcolor = WHITE):
    basicfont = pygame.font.SysFont(None, FONTSIZE)
    SCREEN.fill(BGCOLOR)

    for i,text in enumerate(textlist):

        line = basicfont.render(text, True, fontcolor, BGCOLOR)
        textrect = line.get_rect()
        textrect.centerx = SCREEN.get_rect().centerx
        textrect.centery = SCREEN.get_rect().centery + (i+1)*FONTSIZE - shiftup
        SCREEN.blit(line, textrect)

    pygame.mouse.set_visible(0)
    pygame.display.flip()
    await asyncio.sleep(0)

    pressnext = 0

    while pressnext == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    pressnext = 1
                    another = 1
                    return another
                    break
                if event.key == pygame.K_n:
                    another = 0
                    return another
                    break
        await asyncio.sleep(0)

async def displayTextcenterWait(textlist,waitfor,shiftup, fontcolor = WHITE):
    basicfont = pygame.font.SysFont(None, FONTSIZE)
    SCREEN.fill(BGCOLOR)

    for i,text in enumerate(textlist):

        line = basicfont.render(text, True, fontcolor, BGCOLOR)
        textrect = line.get_rect()
        textrect.centerx = SCREEN.get_rect().centerx
        textrect.centery = SCREEN.get_rect().centery + (i+1)*FONTSIZE - shiftup
        SCREEN.blit(line, textrect)

    pygame.mouse.set_visible(0)
    pygame.display.flip()
    await asyncio.sleep(0)
    pressnext = 0
    pygame.time.delay(waitfor)


def fixcross():
    fixpos = (CX,CY)
    pygame.draw.circle(SCREEN, BLACK, fixpos, FIXCROSSSIZE, 0)


def collide_points(p1,p2,selectsize):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dist = math.hypot(dx, dy)
    if dist < selectsize:
        return True
    else:
        return False

def collide_objpoint(object,fixpos,selectsize):
    CX = fixpos[0]
    CY = fixpos[1]

    dx = object.x - CX
    dy = object.y - CY
    dist = math.hypot(dx, dy)
    if dist < selectsize:
        tangent = math.atan2(dy, dx)
        angle = 0.5 * math.pi + tangent
        new_angle = 2*tangent - object.angle
        object.angle = new_angle #+ random.uniform(0, 2*math.pi)
        object.x += math.sin(angle)
        object.y -= math.cos(angle)

def calc_dist(object, fixpos,leftright,bottomup):
    CX = fixpos[0]
    CY = fixpos[1]

    dx = object.x - CX
    dy = object.y - CY
    dist = math.hypot(dx, dy)
    if leftright:
        return dx
    if bottomup:
        return dy

def calc_dist_obj(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dist = math.hypot(dx, dy)
    return dist


def collide(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y

    # measure distance between the two relative to zero
    dist = math.hypot(dx, dy)
    if dist < 1.5*(p1.size + p2.size):

        tangent = math.atan2(dy, dx)
        angle = 0.5 * math.pi + tangent

        angle1 = 2*tangent - p1.angle
        angle2 = 2*tangent - p2.angle
        speed1 = p1.speed
        speed2 = p2.speed

        (p1.angle, p1.speed) = (angle1, speed1)
        (p2.angle, p2.speed) = (angle2, speed2)

        p1.x += math.sin(angle)
        p1.y -= math.cos(angle)
        p2.x -= math.sin(angle)
        p2.y += math.cos(angle)


def convert_degrees(h,d,r,spx):
    deg_per_px = math.degrees(math.atan2(.5*h, d)) / (.5*r)
    sdeg = spx * deg_per_px
    return sdeg


async def MOT(objects, trial=999, Subnum=999, SUBDIR=999):
    # object motion
    framecount = 0
    fpsClock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(0)
    start = time.time()
    time.perf_counter()
    elapsed = 0
    framedata_collect = []
    #pygame.time.delay(200)

    while framecount < MOTTf and running:
        framedata = []
        fpsClock.tick_busy_loop(FPS)
        framecount += 1
        SCREEN.fill(BGCOLOR)
        fixcross()
        pupildata = []

        for i, object in enumerate(objects):
            if running:

                object.move()
                object.bounce()

                collide_objpoint(object,(CX,CY),OBJRADIUS+8)

                for object2 in objects[i+1:]:
                    collide(object, object2)

                object.display()

        if trial != 999:
            framedata.append(framecount)
            for object in objects:
                framedata.append(object.x)
                framedata.append(object.y)
            #cureyexy = 999#tracker.sample()
            #curpupilsize = 999#tracker.pupil_size()

            #framedata.append(curpupilsize)
            #framedata.append(cureyexy[0])
            #framedata.append(cureyexy[1])
            #pupildata.append(curpupilsize)

        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        elapsed = time.time() - start
        framedata_collect.append(framedata)

    if trial != 999:
        csvfile = "Pair%d_%d.csv" % (Subnum,trial)
        path_frame = SUBDIR + csvfile
        with open(path_frame, 'w') as f:
            wr = csv.writer(f)
            wr.writerows(framedata_collect)

        if sys.platform == "emscripten":
            output = RequestHandler()
            # Define the URL and data for the POST request
            url = "http://127.0.0.1:5000/submit_trial"
            writeheader = False
            # Send the POST request
            try:
                message = "test"
                message = await output.post(url, {
                    "writeheader": writeheader,
                    "csvfile": csvfile,
                    "Subnum": Subnum,
                    "row": framedata_collect  # `data` is your list of values (header or trial)
                })
                print(message)
            except:
                print("fail")
                pass
    #median_pupil = median(pupildata)
    return objects



async def markall(objects, selectionormark, Subnum, trial, SUBDIR, feedback=0):
    pygame.mouse.set_visible(1)

    corrident = 0
    SCREEN.fill(BGCOLOR)
    for object in objects:
        object.display()
    fixcross()
    pygame.mouse.set_pos([WIDTH/2,HEIGHT/2])

    pygame.display.flip()
    await asyncio.sleep(0)
    start = time.time()
    elapsed = time.time() - start
    mark_onset = elapsed

    selobjidx = []
    selcor_objidx = []
    selwrong_objidx = []

    notselected = 1
    selectedobj = 0
    selectorder = numpy.zeros(OBJNUM)
    rank = 1
    checkcounter = numpy.zeros(OBJNUM)

    collect_mousepos = []
    leftcenter = False
    coutmarkframe = 0
    curreactiontime = 0
    fpsClock_resp = pygame.time.Clock()

    while notselected:
        fpsClock_resp.tick_busy_loop(FPS)
        frame_mousepos = []
        coutmarkframe = coutmarkframe + 1
        curmpos = pygame.mouse.get_pos()
        # check how to record reaction time
        if ((curmpos != (CX,CY)) and leftcenter == False):
            curreactiontime = time.time() - start
            leftcenter = True
        if (coutmarkframe % 2 == 0) or coutmarkframe == 1:
            frame_mousepos.append(curmpos[0])
            frame_mousepos.append(curmpos[1])
            collect_mousepos.append(frame_mousepos)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                checkfinish = collide_points((CX,CY),pos,FIXCROSSSIZE)

                if checkfinish:
                    notselected = 0
                    break

                for i,object in enumerate(objects):
                    objpos = (object.x,object.y)
                    check = collide_points(objpos,pos,OBJRADIUS)
                    if check:
                        selectedobj = selectedobj + 1
                        object.thickness = 0
                        checkcounter[i] += 1
                        if checkcounter[i] == 1:
                            object.colour = COLORME
                            selobjidx.append(i)
                        elif checkcounter[i] == 2:
                            object.colour = COLORME
                        elif checkcounter[i] == 3:
                            object.colour = COLORME

                        object.display()
                        selectorder[i] = rank
                        rank += 1
                        pygame.display.flip()
                        notcorsel = 0
                        for t, tmp in enumerate(objects[0:NUMTAR]):
                            if t == i:
                                selcor_objidx.append(i)
                            if t != i:
                                notcorsel += 1
                                if NUMTAR == notcorsel:
                                    selwrong_objidx.append(i)
        await asyncio.sleep(0)

    if feedback == 1:
        for sel in selcor_objidx:
            objects[sel].thickness = 0
            objects[sel].colour = GREEN
            corrident += 1

        for sel in selwrong_objidx:
            objects[sel].thickness = 0
            objects[sel].colour = RED
            corrident -= 1

    if selectionormark == "selection":
        csvfile = "MposSelection_Pair%d_%d.csv" % (Subnum,trial)
        path_frame = SUBDIR + csvfile
        with open(path_frame, 'w') as f:
            wr = csv.writer(f)
            wr.writerows(collect_mousepos)

        if sys.platform == "emscripten":
            output = RequestHandler()
            # Define the URL and data for the POST request
            url = "http://127.0.0.1:5000/submit_trial"
            writeheader = False
            # Send the POST request
            try:
                message = "test"
                message = await output.post(url, {
                    "writeheader" : writeheader,
                    "csvfile": csvfile,
                    "Subnum": Subnum,
                    "row": collect_mousepos  # `data` is your list of values (header or trial)
                })
                print(message)
            except:
                print("fail")
                pass

    if selectionormark == "markall":
        csvfile = "MposMarkall_Pair%d_%d.csv" % (Subnum,trial)
        path_frame = SUBDIR + csvfile
        with open(path_frame, 'w') as f:
            wr = csv.writer(f)
            wr.writerows(collect_mousepos)

        if sys.platform == "emscripten":
            output = RequestHandler()
            # Define the URL and data for the POST request
            url = "http://127.0.0.1:5000/submit_trial"
            writeheader = False
            # Send the POST request
            try:
                message = "test"
                message = await output.post(url, {
                    "writeheader" : writeheader,
                    "csvfile": csvfile,
                    "Subnum": Subnum,
                    "row": collect_mousepos  # `data` is your list of values (header or trial)
                })
                print(message)
            except:
                print("fail")
                pass

    elapsed = time.time() - start
    mark_response = elapsed

    totalperf = numpy.zeros(2*OBJNUM)
    tarint = 0
    corint = 1


    for object in objects:
        object.display()
        await asyncio.sleep(0)
    pygame.display.flip()
    await asyncio.sleep(0)
    pygame.time.delay(1000)
    pygame.mouse.set_visible(0)
    mark_rt = mark_response - mark_onset
    return corrident, mark_rt, totalperf, selectorder, selobjidx, selcor_objidx, selwrong_objidx, objects, curreactiontime



class Object:
    def __init__(self, pos, size, objspeed):
        self.x = pos[0]
        self.y = pos[1]
        self.size = size
        self.colour = BLACK
        self.thickness = OBJTHICKNESS
        self.speed = objspeed
        # angle in radians, 1 radians = 180 degrees/pi = 57.295
        self.angle = math.pi/2 # move left to right

    def display(self):
        # draw a circle
        # arguments: surface on which it is drawn, color, (x,y) coordinates,
        # the radius, a thickness (optional)
        pygame.draw.circle(SCREEN, self.colour, (int(self.x), int(self.y)), int(self.size), self.thickness)
        pygame.draw.circle(SCREEN, BLACK, (int(self.x), int(self.y)), int(self.size), 1)


    def move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def bounce(self):
        if self.x > WIDTH - self.size:
            self.x = 2*(WIDTH - self.size) - self.x
            self.angle = - self.angle
        elif self.x < self.size:
            self.x = 2*self.size - self.x
            self.angle = - self.angle

        if self.y > HEIGHT - self.size:
            self.y = 2*(HEIGHT - self.size) - self.y
            self.angle = math.pi - self.angle

        elif self.y < self.size:
            self.y = 2*self.size - self.y
            self.angle = math.pi - self.angle

    def coord(self):
        return (self.x,self.y)

    def coordx(self):
        return self.x

    def coordy(self):
        return self.y
