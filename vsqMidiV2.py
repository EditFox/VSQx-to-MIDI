#! /usr/bin/env python
#  -*- coding: utf-8 -*-
# pylint: disable=W,C,R
# python hates me

import sys
import re                                     #used to find info from vocaloid file, regex
from pyknon.genmidi import Midi               #midi related things
from pyknon.music import NoteSeq, Note, Rest  #midi related things

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    from tkinter import filedialog
    py3 = True

import vsqMidiV2_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    top = VSQx_To_Midi (root)
    vsqMidiV2_support.init(root, top)
    root.mainloop()

w = None
def create_VSQx_To_Midi(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = VSQx_To_Midi (w)
    vsqMidiV2_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_VSQx_To_Midi():
    global w
    w.destroy()
    w = None

def NewPrint(arg, label):
    label['text'] += "\n" + arg

def dothething(label):
    print("Starting...")
    #track info#
    tempoStr = re.compile("<tempo>(.*)<\/tempo>")
    trackStr = re.compile("<vsTrack>[\s\S]*?<\/vsTrack>")
    otherStr = re.compile("<v>(.*)<\/v>")
    #note info#
    notesStr = re.compile("<note>[\s\S]*?</note>")
    pitchStr = re.compile("<n>[\s\S]*?</n>")
    startStr = re.compile("<t>[\s\S]*?</t>")
    duratStr = re.compile("<dur>[\s\S]*?</dur>")
    partRStr = re.compile("<vsPart>[\s\S]*?</vsPart>")
    #playtStr = re.compile("<playTime>[\s\S]*?</playTime>")
    # PianoKey = ["C", "C#", "D", "D#", 'E', 'F', 'G#','A','A#','B']
    def NotefromNum(num):
        a = Note(num-84)
        return str(a).strip("<").strip(">") + str(a.verbose).split(", ")[1]

    #ask user for info
    #load file, make it readable
    file_path = filedialog.askopenfilename()
    file = open(file_path).read().replace("\n", "")

    #get more info
    tempo = int(otherStr.findall(tempoStr.findall(file)[0])[0])
    tracks = trackStr.findall(file)
    parts = partRStr.findall(file)
    NewPrint("Tempo: {}".format(tempo/100), label)
    NewPrint("Tracks: {}".format(len(tracks)), label)
    NewPrint("Parts: {}".format(len(parts)), label)

    #NOW for the important stuff
    '''
    For some reason, vocaloid stores note data as numbers.
    And also for some reason, the number 0 is equal to C-2, As in C negative 2
    what
    the fuck
    '''

    cur = 1
    midi = Midi(len(tracks), tempo=tempo/100)
    for x in tracks:
        NewPrint("Track {}".format(cur), label)
        NewPrint("--------", label)
        notes = notesStr.findall(tracks[cur-1])
        PARTS = partRStr.findall(x)
        NewPrint("Note Count: {}".format(len(notes)), label)
        NewPrint("Part Count: {}".format(len(PARTS)), label)
        if len(notes) == 0:
            NewPrint("empty track, skipping", label)
            continue
        for N in PARTS:
            notes = notesStr.findall(N)
            firstNote = notes[0]
            firstNoteStart = int(startStr.findall(firstNote)[0].strip("<t>").strip("</t>"))
            noteinfo = []
            if firstNoteStart != 0:
                noteinfo.append( Rest( firstNoteStart / 1920 ) )
            noteinfo.append( Rest( int(startStr.findall( N )[0].strip("<t>").strip("</t>"))/1920 ) )
            lastOn = None
            lastOff = None
            for b in notes:
                sta = startStr.findall(b)[0].strip("<t>").strip("</t>")
                dur = duratStr.findall(b)[0].strip("<dur>").strip("</dur>")
                pit = pitchStr.findall(b)[0].strip("<n>").strip("</n>")
                if lastOn:
                    if sta == lastOff:
                        noteinfo.append(Note( int(pit)+12, -2, int(dur) / 1920))
                    else:
                        noteinfo.append(Rest( (((int(dur) + int(sta)) - lastOff)-int(dur)) / 1920))
                        noteinfo.append(Note( int(pit)+12, -2, int(dur) / 1920))
                else:
                    noteinfo.append(Note( int(pit)+12, -2, int(dur) / 1920))
                lastOn = int(sta)
                lastOff = int(sta) + int(dur)
            seq = NoteSeq(noteinfo)
            midi.seq_notes(seq, track=cur-1)
        cur += 1
    midi.write("{}.mid".format(file_path.strip(".vsqx")))
    NewPrint("Saved to {}".format("{}.mid".format(file_path.strip(".vsqx"))), label)

class VSQx_To_Midi:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 

        top.geometry("640x480+616+198")
        top.title("VSQx To Midi")
        top.configure(background="#dbcced")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")



        self.Label1 = Label(top)
        self.Label1.place(relx=0.02, rely=0.94, height=21, width=619)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="#b7a8d8")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Developed by EditFox''')

        self.Label2 = Label(top)
        self.Label2.place(relx=0.03, rely=0.17, height=361, width=594)
        self.Label2.configure(activeforeground="#c9c9dd")
        self.Label2.configure(anchor=NW)
        self.Label2.configure(background="#2d2d2d")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#c2eac2")
        self.Label2.configure(justify=LEFT)
        self.Label2.configure(text='''Console''')
        self.Label2.configure(width=594)

        self.Button2 = Button(top)
        self.Button2.place(relx=0.03, rely=0.04, height=54, width=537+60)
        self.Button2.configure(command=lambda:dothething(self.Label2))
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#abcdd8")
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(overrelief="groove")
        self.Button2.configure(pady="0")
        self.Button2.configure(relief=GROOVE)
        self.Button2.configure(text='''Open File''')






if __name__ == '__main__':
    vp_start_gui()



