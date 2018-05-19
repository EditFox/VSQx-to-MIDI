import re                                     #used to find info from vocaloid file, regex
from pyknon.genmidi import Midi               #midi related things
from pyknon.music import NoteSeq, Note, Rest  #midi related things

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
playtStr = re.compile("<playTime>[\s\S]*?</playTime>")
# PianoKey = ["C", "C#", "D", "D#", 'E', 'F', 'G#','A','A#','B']
def NotefromNum(num):
	a = Note(num-84)
	return str(a).strip("<").strip(">") + str(a.verbose).split(", ")[1]

#ask user for info
print("Please put in the file path to your VSQx file.")
print("Examples:")
print("C:/Users/USERNAME/Desktop/x.vsqx")
print("x.vsqx (if it's in the same folder)")
#load file, make it readable
filename = input("> ")
file = open(filename).read().replace("\n", "")

#get more info
tempo = int(otherStr.findall(tempoStr.findall(file)[0])[0])
tracks = trackStr.findall(file)
parts = partRStr.findall(file)
print("Tempo: {}".format(tempo/100))
print("Tracks: {}".format(len(tracks)))
print("Parts: {}".format(len(parts)))

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
	print("Track {}".format(cur))
	print("--------")
	notes = notesStr.findall(tracks[cur-1])
	PARTS = partRStr.findall(x)
	print("Note Count: {}".format(len(notes)))
	print("Part Count: {}".format(len(PARTS)))
	if len(notes) == 0:
		print("h")
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
midi.write("{}.mid".format(filename.strip(".vsqx")))