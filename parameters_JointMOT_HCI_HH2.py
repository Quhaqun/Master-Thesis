"""
@author: bwahn

"""

import os
import numpy
import pygame

from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

SUB = "999" #input("Please enter participant number: ")
AGE = "99" #input("Age of participant? (in years)")
GENDER = "9" #input("Gender of participant? (f,m,o)")
HANDEDNESS = "9" #input("Handedness? (l,r,a)")
URL_Server_TRIAL = "http://localhost:5000/submit_trial"
URL_Server_EMAIL = "http://localhost:5000/submit_email"
#URL_Server_TRIAL = "http://salzburg.kke.tu-berlin.de:5000/submit_trial"
#URL_Server_EMAIL = "http://salzburg.kke.tu-berlin.de:5000/submit_email"

LOCALHOST = False
GRO = True
FULLSCREEN = 0

TESTMODE = True

# partner parameters
waitforconnect = 3000
timeperselection = 2.2 # based on earlier study

# parameter Joint MOT
# Condition parameters

SHOWTEAMSCORE = False
SHOWINDIVIDUALSCORES = False
SHOWSELECTIONS = True
EVALJOINTSELECTION = False

# Colors
BLACK = (0,0,0,1)
WHITE = (255,255,255,1)
RED = (255,0,0,1)
GRAY = (190,190,190,1)
LIGHTGRAY = (211,211,211,1)
GREEN = (34,139,34,1)



# Test
EGRAY = (125,125,125,1)

YELLOW = (255,255,0,1)
MEDYELLOW = (200,200,0,1)
DARKYELLOW = (128,128,0,1)

BLUE = (255,0,255,1)
MEDBLUE = (200,0,200,1)
DARKBLUE = (128,0,128,1)

COLORME = YELLOW
COLOROTHER = BLUE


BGCOLOR = EGRAY
FONTSIZE = 34

# Folders
EXPPATH = os.path.dirname(os.path.abspath(__file__))
DATAPATH = EXPPATH + '/Data'

(WIDTH,HEIGHT) = (1920,1080)

EXPCHOICE = "1" #input("Experiment 1 (1) or Experiment 2 (2)?")

CONDITION = 'nan'

PARTNER = "Computer"
#PARTNER = "Confederate"
#PARTNER = "Robot"

if PARTNER == "Robot":
    import requests
    import time
    from pynput import keyboard
    # Settings
    settings = {
       "FLASK_URL": "http://localhost:5000/behavior/",  # Update this with your Flask server URL
       "BUFFER_PROCESS_INTERVAL": 0.1  # Time in seconds between processing the buffer
    }

FPS = 30
MOTT = 11

SHOWTARf = int(round(3000 / (1000 / FPS)))

MOTTf = int(round(11000 / (1000 / FPS)))

NUMTAR = 6

# trials: alone condition (3 training trials), actual experiment (20 trials), joint condition (3 training trials), actual experiment (40 trials)

if TESTMODE:
    trainingsolotrials = 2#3
    solotrials = 2#20
    trainingjointtrials = 2#3
    jointtrials = 2#40
else:
    trainingsolotrials = 2
    solotrials = 10
    trainingjointtrials = 2
    jointtrials = 20


TRIALS = trainingsolotrials + solotrials + trainingjointtrials + jointtrials
TRIALS_SELECTIONSINFO = [False] * (trainingsolotrials + solotrials) + [True] * (trainingjointtrials + jointtrials)
TRIALS_TYPE_SOLO = ["SoloTrainingStart"] + (trainingsolotrials - 1) * ["SoloTraining"] + ["SoloStart"] + (solotrials - 1) * ["Solo"]
TRIALS_TYPE_Joint = ["JointTrainingStart"] + (trainingjointtrials - 1) * ["JointTraining"] + ["Jointstart"] + (jointtrials - 1) * ["Joint"]
TRIALS_TYPE = TRIALS_TYPE_SOLO + TRIALS_TYPE_Joint


if FULLSCREEN:
    SCREEN = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
    WIDTH,HEIGHT = SCREEN.get_size()
else:
    SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))


CX,CY = WIDTH//2, HEIGHT//2

DOUBLESELRAD = (WIDTH*HEIGHT)//15000
OBJTHICKNESS = 1
OBJNUM = 19

FIXCROSSSIZE = 6

if GRO == True:
    OBJRADIUS = (WIDTH*HEIGHT)//60000
    OBJSPEEDRANGE = [(WIDTH*HEIGHT)// 550000, (WIDTH*HEIGHT)// 450000] # for mark all
    OBJSPEED = numpy.mean(OBJSPEEDRANGE)

if GRO == False:
    OBJRADIUS = (WIDTH*HEIGHT)//65000
    OBJSPEEDRANGE = [(WIDTH*HEIGHT)// 400000, (WIDTH*HEIGHT)// 300000] # for mark all
    OBJSPEED = numpy.mean(OBJSPEEDRANGE)


#SCREEN.fill(BGCOLOR)
smartphone_block = ["Diese Anwendung funktioniert leider nicht auf Mobilgeräten.",
                    "Bitte verwende einen Desktop-Browser für das Experiment."]
Info_Participant = ["Teilnehmer Daten:",
                     "Bitte geben Sie Ihre Daten ein und drücken Sie die Entertaste, um zur nächsten Eingabe zu gelangen.",
                     "Alter",
                     "Geschlecht (f (Frau), m (Mann), o (Andere))",
                     "Händigkeit (l (links), r (rechts), a (Andere))"]

Introduction = ["Einfuehrung:",
"Dieses Experiment wird durchgefuehrt von der Ruhr-Universitaet Bochum.",
"Das Experiment dient der Erforschung von Wahrnehmungsprozessen beim Menschen.",
"",
"Ablauf:",
"Ihre Aufgabe ist es, mehrere sich bewegende Punkte auf dem Bildschirm zu",
"beobachten. Weitere Details zur Aufgabe folgen.",
"",
"Risiken:",
"Mit der Teilnahme an diesem Experiment sind keine bekannten Risiken verbunden.",
"",
"Um fortzufahren, druecken Sie bitte die Leertaste."]

Rights_Participant = ["Ihre Rechte als Versuchsperson:",
"Die Teilnahme an diesem Experiment ist freiwillig. Sie können das Experiment",
"jederzeit ohne Angabe von Gründen abbrechen. Kontaktieren Sie in diesem Fall die",
"Versuchsleitung.",
"",
"Datenspeicherung:",
"Es wird aufgezeichnet, welche Tasten auf der Tastatur Sie wann drücken und wie",
"Sie die Computermaus bewegen. Die aufgenommenen Daten werden streng vertraulich",
"behandelt und nicht direkt mit Ihrem Namen in Verbindung gebracht.",
"Ihre Daten werden auf Passwort-gesicherten Servern gespeichert;",
"Zugriff hat nur der verantwortliche Leiter des Experiments.",
"",
"Fragen?",
"Falls Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an die Versuchsleitung.",
"",
"Wenn Sie die vorausgehenden Informationen zur Kenntnis genommen haben und am",
"Experiment teilnehmen moechten, druecken Sie bitte die Leertaste."]

Instruction_Text_Solo = ["Es folgen nun ein paar Trainingsdurchlaeufe,",
"bei denen Ihnen die Versuchsleitung Ihre Aufgabe erklaert.",
"Um fortzufahren, druecken Sie bitte die Leertaste."]

Announce_Solo_Training = ["Um die Trainingsdurchlaeufe zu starten, druecken Sie bitte die Leertaste."]

Announce_Solo_experiment = ["Nun startet das Experiment.",
"",
"Waehlen Sie zunaechst die Punkte (0-6) aus, die Sie verfolgen moechten.",
"Verfolgen Sie dann diese Punkte waehrend sie sich bewegen.",
"Sobald alle Punkte zum Stillstand kommen, identifizieren Sie die von Ihnen zuvor ausgewaehlten Punkte.",
"Waehlen Sie dabei nur diejenigen Punkte aus, bei denen Sie sich sicher sind.",
"Ihr Ziel ist es, in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
"Die korrekt identifizierten Punkte ergeben Ihren individuellen Score.",
"Achtung: Jede inkorrekte Auswahl fuehrt zu Minuspunkten.",
"",
"Falls Sie jetzt noch eine Frage haben, wenden Sie sich sich bitte an die Versuchsleitung.",
"",
"Um fortzufahren, druecken Sie bitte die Leertaste."]

SoloEnd = ["Sie haben den ersten Teil des Experiments geschafft!",
"Bitte kontaktieren Sie jetzt die Versuchsleitung."]

EndExperiment = [
    "Das Experiment ist nun zuende.",
    "VIELEN DANK fuer Ihre Teilnahme!",
    "",
    "Wenn Sie an der Verlosung eines Amazon-Gutscheins teilnehmen möchten,",
    "geben Sie bitte unten Ihre E-Mail-Adresse ein und drücken Sie auf Senden:"
]

Announce_Joint_training = ["Es folgen nun ein paar Trainingsdurchlaeufe,",
"bei denen Ihnen die Versuchsleitung Ihre Aufgabe erklaert.",
"Um fortzufahren, druecken Sie bitte die Leertaste."]


if PARTNER == "Confederate":
    Instruction_Text_Joint = ["Im zweiten Teil des Experiments werden Sie die gleiche Aufgabe durchfuehren",
    "wie zuvor, jedoch nicht allein, sondern gemeinsam mit einer anderen Person.",
    "",
    "Wichtig: Sie bestimmen die Aufgabenteilung zwischen Ihnen und der anderen Person.",
    "D.h. Sie koennen frei entscheiden, wie viele Punkte Sie verfolgen",
    "und wie viele die Person verfolgt. Anders gesagt:",
    "Sie koennen entscheiden, wie viel Verantwortung fuer die Aufgabe Sie selbst uebernehmen",
    "und wie viel Sie der anderen Person anvertrauen.",
    "",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt die andere Person.",
    "Verfolgen Sie dann Ihre Punkte waehrend sie sich bewegen.",
    "Sobald alle Punkte zum Stillstand kommen, identifizieren Sie Ihre Punkte.",
    "Waehlen Sie dabei nur diejenigen Punkte aus, bei denen Sie sich sicher sind.",
    "Nachdem Sie Ihre Auswahl abgeschlossen haben, wird Ihnen die Auswahl der anderen Person gezeigt.",
    "Da die andere Person vielleicht laenger benötigt als Sie die Punkte auszuwählen, kann es hier zu",
    "Verzögerungen kommen bis Ihnen die Auswahl der anderen Person gezeigt wird."
    "",
    "Gemeinsam mit der anderen Person verfolgen Sie das Ziel, in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "Die korrekt identifizierten Punkte von Ihnen und der Person werden zu einem gemeinsamen Score zusammengezaehlt.",
    "Jede inkorrekte Auswahl fuehrt zu Minuspunkten.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]

    Connectingpartner = ["Verbinde andere Person mit Experiment ... bitte warten."]

    Connectingpartner_success = ["Verbindung erfolgreich!",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]

    Announce_Joint_experiment = ["Nun startet der zweite Teil des Experiments.",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt die anderen Person.",
    "Ihr gemeinsames Ziel ist es, in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "",
    "Falls Sie jetzt noch eine Frage haben, wenden Sie sich sich bitte an die Versuchsleitung.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]


if PARTNER == "Computer" and SHOWTEAMSCORE == False:
    Instruction_Text_Joint = ["Im zweiten Teil des Experiments werden Sie die gleiche Aufgabe durchfuehren",
    "wie zuvor, jedoch nicht allein, sondern gemeinsam mit einem Computerpartner.",
    "",
    "Wichtig: Sie bestimmen die Aufgabenteilung zwischen Ihnen und dem Computer.",
    "D.h. Sie koennen frei entscheiden, wie viele Punkte Sie verfolgen",
    "und wie viele der Computer verfolgt. Anders gesagt:",
    "Sie koennen entscheiden, wie viel Verantwortung fuer die Aufgabe Sie selbst uebernehmen",
    "und wie viel Sie dem Computer anvertrauen.",
    "",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt der Computer.",
    "Verfolgen Sie dann Ihre Punkte waehrend sie sich bewegen.",
    "Sobald alle Punkte zum Stillstand kommen, identifizieren Sie Ihre Punkte.",
    "Waehlen Sie dabei nur diejenigen Punkte aus, bei denen Sie sich sicher sind.",
    "Nachdem Sie Ihre Auswahl abgeschlossen haben, waehlt der Computer seine Punkte aus.",
    "",
    "Gemeinsam mit dem Computer verfolgen Sie das Ziel in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "Die korrekt identifizierten Punkte von Ihnen und dem Computer werden zu einem gemeinsamen Score zusammengezaehlt."
    "Jede inkorrekte Auswahl fuehrt zu Minuspunkten.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]

    Announce_Joint_experiment = ["Nun startet der zweite Teil des Experiments.",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt der Computer.",
    "Ihr gemeinsames Ziel ist es, in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "",
    "Falls Sie jetzt noch eine Frage haben, wenden Sie sich sich bitte an die Versuchsleitung.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]

if PARTNER == "Computer" and SHOWTEAMSCORE == True:
    Instruction_Text_Joint = ["Im zweiten Teil des Experiments werden Sie die gleiche Aufgabe durchfuehren",
    "wie zuvor, jedoch nicht allein, sondern gemeinsam mit einem Computerpartner.",
    "",
    "Wichtig: Sie bestimmen die Aufgabenteilung zwischen Ihnen und dem Computer.",
    "D.h. Sie koennen frei entscheiden, wie viele Punkte Sie verfolgen",
    "und wie viele der Computer verfolgt. Anders gesagt:",
    "Sie koennen entscheiden, wie viel Verantwortung fuer die Aufgabe Sie selbst uebernehmen",
    "und wie viel Sie dem Computer anvertrauen.",
    "",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt der Computer.",
    "Verfolgen Sie dann Ihre Punkte waehrend sie sich bewegen.",
    "Sobald alle Punkte zum Stillstand kommen, identifizieren Sie Ihre Punkte.",
    "Waehlen Sie dabei nur diejenigen Punkte aus, bei denen Sie sich sicher sind.",
    "Nachdem Sie Ihre Auswahl abgeschlossen haben, waehlt der Computer seine Punkte aus.",
    "",
    "Gemeinsam mit dem Computer verfolgen Sie das Ziel in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "Die korrekt identifizierten Punkte von Ihnen und dem Computer werden zu einem gemeinsamen Score zusammengezaehlt."
    "Jede inkorrekte Auswahl fuehrt zu Minuspunkten.",
    "Nachdem Sie die Auswahl der Computers gezeigt wurde und Sie mit der Leertaste fortfahren,",
    "sehen sie einen gemeinsamen Team Score, der einzeigt wie viele Punkte sie gemeinsam korrekt haben.",
    ""
    "Um fortzufahren, druecken Sie bitte die Leertaste."]

    Announce_Joint_experiment = ["Nun startet der zweite Teil des Experiments.",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt der Computer.",
    "Ihr gemeinsames Ziel ist es, in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "",
    "Falls Sie jetzt noch eine Frage haben, wenden Sie sich sich bitte an die Versuchsleitung.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]


if PARTNER == "Roboter":
    Instruction_Text_Joint = ["Im zweiten Teil des Experiments werden Sie die gleiche Aufgabe durchfuehren",
    "wie zuvor, jedoch nicht allein, sondern gemeinsam mit einem Roboter.",
    "",
    "Wichtig: Sie bestimmen die Aufgabenteilung zwischen Ihnen und dem Roboter.",
    "D.h. Sie koennen frei entscheiden, wie viele Punkte Sie verfolgen",
    "und wie viele der Roboter verfolgt. Anders gesagt:",
    "Sie koennen entscheiden, wie viel Verantwortung fuer die Aufgabe Sie selbst uebernehmen",
    "und wie viel Sie dem Roboter anvertrauen.",
    "",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt der Roboter.",
    "Verfolgen Sie dann Ihre Punkte waehrend sie sich bewegen.",
    "Sobald alle Punkte zum Stillstand kommen, identifizieren Sie Ihre Punkte.",
    "Waehlen Sie dabei nur diejenigen Punkte aus, bei denen Sie sich sicher sind.",
    "Nachdem Sie Ihre Auswahl abgeschlossen haben, waehlt der Roboter seine Punkte aus.",
    "",
    "Gemeinsam mit dem Roboter verfolgen Sie das Ziel in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "Die korrekt identifizierten Punkte von Ihnen und dem Roboter werden zu einem gemeinsamen Score zusammengezaehlt."
    "Jede inkorrekte Auswahl fuehrt zu Minuspunkten.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]

    Announce_Joint_experiment = ["Nun startet der zweite Teil des Experiments.",
    "Waehlen Sie zunaechst Ihre Punkte (0-6) aus. Die uebrigen Punkte uebernimmt der Roboter.",
    "Ihr gemeinsames Ziel ist es, in jedem Durchgang möglichst viele Punkte korrekt zu identifizieren.",
    "",
    "Falls Sie jetzt noch eine Frage haben, wenden Sie sich sich bitte an die Versuchsleitung.",
    "",
    "Um fortzufahren, druecken Sie bitte die Leertaste."]








# announceindi_training = ["Training Trials: Alone Condition",
# "",
# "There are two types of trials you will be performing in this condition:",
# "1) Baseline trials and 2) Tracking trials.",
# "",
# "In the baseline trials, your only task is to look at the central dot and ignore the objects.",
# "",
# "In the tracking trials, you will be performing a multiple object tracking task.",
# "In this task, you will first see several stationary objects.",
# "A subset of these objects will be displayed in white, which are the target objects.",
# "Then the objects start moving across the screen.",
# "Your task is to track the movements of the target objects.",
# "You can freely choose how many targets you track. It does not need to be all six.",
# "While tracking the targets, please continue to look at the central dot.",
# "Once the objects stop moving, select those objects that you think are the targets by left-clicking on them with the computer mouse.",
# "You can select as many objects as you want but try to be accurate with your selections.",
# "For each correct selection you get plus 1 point. For each incorrect selection, minus 1 point.",
# "Once you are done with your selections, click on the middle dot. Then a trial is completed.",
# "Note: There is no performance feedback given.",
# "",
# "Importantly: Your goal is to maximize the number of correct object selections.",
# "",
# "To become familiar with the procedure, you will first perform a baseline trial followed by two tracking trials.",
# "Before each trial, you are required to look at the central dot and press space."]


# if Experiment1 == True:
# 	announcejoint_training = ["Training Trials: Collaborative Condition",
# 	"",
# 	"In this condition, you again will be performing baseline and tracking trials.",
# 	"",
# 	"The baseline trials are the same as before.",
# 	"",
# 	"The tracking trials will now be performed together with a computer partner.",
# 	"This computer partner has been designed to behave in a human-like way.",
# 	"Specifically, we took data from human participants when they performed this tracking task together",
# 	"and used this data to model the behaviour of the computer partner.",
# 	"",
# 	"The sequence of events in the tracking trials is the same as before.",
# 	"The only change is that after you confirmed your selections by clicking on the middle dot,",
# 	"you will see the selections of the computer partner in yellow.",
# 	"If you selected the same objects, then these overlapping selections are shown in yellow and your colour.",
# 	"",
# 	"Importantly:",
# 	"Your goal is to work together with the computer partner to maximize your combined number of correct object selections.",
# 	"Mind that overlapping correct selections count only plus 1 point to the combined performance.",
# 	"Two non-overlapping correct selections, count 2 points to the combined performance.",
# 	"Hence, it is beneficial for maximizing the combined score to reduce overlapping selections.",
# 	"Note: Incorrect selections still result in minus points.",
# 	"",
# 	"To become familiar with the procedure, you first perform a baseline trial followed by two tracking trials.",
# 	"Before each trial, you are required to look at the central dot and press space.",
# 	"While tracking objects, please continue to look at the central dot."]

# if Experiment1 == False:
# 	announcejoint_training = ["Training Trials: Collaborative Condition",
# 	"",
# 	"In this condition, you again will be performing baseline and tracking trials.",
# 	"",
# 	"The baseline trials are the same as before.",
# 	"",
# 	"The tracking trials will now be performed together with a computer partner.",
# 	"",
# 	"The sequence of events in the tracking trials is the same as before.",
# 	"The only change is that when you see the target objects, 3 of them are shown in white and 3 in yellow.",
# 	"The targets shown in yellow will be tracked by the computer partner while you track the targets shown in white.",
# 	"If you cannot track all three objects shown in white, it is fine to track a lower number.",
# 	"",
# 	"Importantly:",
# 	"Your goal is to accurately track the target objects indicated in white."
# 	"You do not need to track the target objects shown in yellow.",
# 	"",
# 	"To become familiar with the procedure, you first perform a baseline trial followed by two tracking trials.",
# 	"Before each trial, you are required to look at the central dot and press space.",
# 	"While tracking objects, please continue to look at the central dot."]
