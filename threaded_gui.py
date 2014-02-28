#! /usr/bin/env python

################################################
### Name: threaded_gui.py
### Description: Gui vor directory MP3 Encoder
### Author: Malte Koch
### exec: python threaded_gui.py
### Version: 0.2
### Envirnoment: Python2.7
### Operating System: Linux/GNU, Windows
#################################################


# Gui imports
from Tkinter import *
import ttk
import tkFileDialog
import tkMessageBox

# Encoder
from Encoder import Encoder

# System imports
import threading, thread
import subprocess
import time
import os

class Gui():
	root = None # Root View
	_input = None # Input Source
	_output = None # Output Source
	e = None # Encoder
	encodeFinished = False
	progressBarLength = 0 # Length of progressbar
	counter = 0 # filecounter
	def __init__(self):

		# Rootview
		self.root=Tk()

		# Set Title
		self.root.title("MP3 - Encoder - Multithreaded by Masterky")

		# 1 = VBR Preset, 2 = VBR, 3 = Bitrate
		self.options = IntVar()
		self.options.set(1)
		self.optionOld = 0

		self.qualityPreset = IntVar()
		self.qualityPreset.set(1) 

		# Input Label and Button
		self.label_input_text = StringVar()
		self.label_input_text.set("Selected Input: nothing") 
		self.label_input = Label(self.root, fg='blue', textvariable=self.label_input_text)
		self.label_input.pack(fill=X)

		button_input = Button(self.root, command=self.setInput, text="Input Directory", highlightthickness=3)
		button_input.pack(fill=X)
		
		# Output Label and Button
		self.label_output_text = StringVar()
		self.label_output_text.set("Selected Output: nothing") 
		label_output = Label(self.root,fg='blue', textvariable=self.label_output_text)
		label_output.pack(fill=X)
		button_output = Button(self.root, command=self.setOutput, text="Output Directory", highlightthickness=3)
		button_output.pack(fill=X)

		# Encoding
		EncodingLabel = Label(self.root, fg='blue', text="""Choose Encoding Method:""",justify = CENTER, pady=10).pack()

		# Encoding Methods
		Radiobutton(self.root, text="VBR Preset", padx = 20, highlightthickness=3, variable=self.options, value=1).pack(anchor=W) 
		Radiobutton(self.root, text="VBR", padx = 20, highlightthickness=3, variable=self.options, value=2).pack(anchor=W)
		Radiobutton(self.root, text="Bitrate", highlightthickness=3, padx = 20, variable=self.options, value=3).pack(anchor=W)

		PRESET_EXTREM = "extreme"
		PRESET_MEDIUM = "medium"
		PRESET_STANDARD = "standard"
		PRESET_INSANE = "insane"

		# VBR Presets
		self.presets = []

		Label(self.root, text="""VBR Preset:""",justify = CENTER, pady=10).pack()
		self.preset1 = Radiobutton(self.root, text=PRESET_STANDARD, padx = 20,variable=self.qualityPreset, value=0)
		self.preset2 = Radiobutton(self.root, text=PRESET_MEDIUM, padx = 20, variable=self.qualityPreset, value=1)
		self.preset3 = Radiobutton(self.root, text=PRESET_EXTREM, padx = 20, variable=self.qualityPreset, value=2)
		self.preset4 = Radiobutton(self.root, text=PRESET_INSANE, padx = 20, variable=self.qualityPreset, value=3)

		self.preset1.pack(anchor=W)
		self.preset2.pack(anchor=W)
		self.preset3.pack(anchor=W)
		self.preset4.pack(anchor=W)

		self.presets.append(self.preset1)
		self.presets.append(self.preset2)
		self.presets.append(self.preset3)
		self.presets.append(self.preset4)

		# VBR Quality
		Label(self.root, text="""VBR Quality:""",justify = CENTER, pady=10).pack()
		self.vbrQuality = Scale(self.root, from_=0, to_=9, orient=HORIZONTAL)
		self.vbrQuality.set(2)
		self.vbrQuality.pack(fill=X)

		# Bitrate
		Label(self.root, text="""Bitrate:""",justify = CENTER, pady=10).pack()
		self.bitrate = Scale(self.root, from_=32, to_=320, orient=HORIZONTAL)
		self.bitrate.set(120)
		self.bitrate.pack(fill=X)

		# Progressbar
		self.progressLabel = Label(self.root, text="""Progress:""",justify = CENTER, pady=10, bg='yellow')
		self.progressLabel.pack(anchor=CENTER)
		self.progressbar = ttk.Progressbar(self.root,orient=HORIZONTAL, length=0, mode="determinate")
		self.progressbar.pack(fill=X)



		# Encode Button
		self.encodeButton = Button(self.root, text="Encode", command=self.callback)
		self.encodeButton.config(bg = 'yellow')
		self.encodeButton.pack()
		self.root.geometry("480x620")

		# Binding method to gray out
		self.root.bind('<<Handler>>', self.handleOption)

		# Starting thread
		th = threading.Thread(target=self.startHandler)
		th.setDaemon(1)
		th.start()

	def showFileInputError(self):
	   tkMessageBox.showerror("Error", "Please select an input and output directory!")
	def setInput(self):
		_dir =  tkFileDialog.askdirectory(parent=self.root, title='Select Directory with MP3 Files')
		self._input = _dir
		if type(self._input) is str:
			if (self._input != ""):
				self.encodeFilePath(self._input)
				print "Anz Files: ", self.countFiles(self._input)
			else: pass
		else:
			self._input = ""
		print "Input: ", self._input
		
		self.label_input_text.set("Selected Input = "+ self._input)
	def encodeFilePath(self, path):
		return path.replace("/", os.sep)
	def setOutput(self):
		_dir =  tkFileDialog.askdirectory(parent=self.root, title='Select Directory with MP3 Files')
		self._output = _dir
		if type(self._output) is str:
			if (self._output != ""):
				self._output = self.encodeFilePath(self._output)
			else:
				pass
		print "Output: ", self._output
		self.label_output_text.set("Selected Output = " + self._output)
	def countFiles(self, dir):
		for newdir in os.listdir(dir):
			newFile = os.path.join(dir, newdir)
			if os.path.isdir(newFile):
				self.countFiles(newFile)
			else:
				self.counter += 1
		return self.counter

	def handleOption(self, event):

		# Update Views
		option = self.getSelection()
		if self.optionOld is not option:
			if option is 1:
				# Preset
				print "VBR Preset selected"
				self.enablePresets()
				self.disableVBRQuality()
				self.disableBitrate()
			elif option is 2:
				# VBR Quality
				print "VBR Quality selected"
				self.enableVBRQuality()
				self.disableBitrate()
				self.disablePresets()
			elif option is 3:
				# Bitrate
				print "Bitrate selected"
				self.enableBitrate()
				self.disablePresets()
				self.disableVBRQuality()
				#time.sleep(0.1)
			else:
				print "Something went wrong"
			#self.root.update()
			self.optionOld = option
		else:
			pass

	def startEncoder(self):
		option = self.getSelection()
		if option is 1:
			# Presets

			vbrQuality = None
			bitrate = None
			fastMode = True
			threads = 4
			print self.qualityPreset.get()

			preset = self.presets[self.qualityPreset.get()]['text']
			print "Preset = ", preset
			self._start(_preset=preset, _bitrate=bitrate, _fastMode=fastMode, _vbrQuality=vbrQuality, _threads=threads)

		elif option is 2:
			# VBR Quality

			preset = None
			bitrate = None
			fastMode = True
			threads = 4
			vbrQuality = int(self.vbrQuality.get())

			self._start(_preset=preset, _bitrate=bitrate, _fastMode=fastMode, _vbrQuality=vbrQuality, _threads=threads)
		else:
			# Option 3
			vbrQuality = None
			preset = None
			fastMode = True
			threads = 4
			print "Bitrate:",self.bitrate.get()
			bitrate = int(self.bitrate.get())

			self._start(_preset=preset, _bitrate=bitrate, _fastMode=fastMode, _vbrQuality=vbrQuality, _threads=threads)

	def _start(self, _preset=None, _bitrate=None, _fastMode=True, _vbrQuality=None, _threads=4):
		self.d = Encoder(encodePath=self._input, outputPath=self._output, preset=_preset, bitrate=_bitrate, fastMode=_fastMode, vbr=_vbrQuality, threads=_threads, guiMode=True)
		self.d.startEncoder()
		self.encodeFinished = True
		self.encodeButton.config(state=NORMAL)
		#self._showFinished()

	# This method is not Thread safe with Windows
	# Gui will freeze
	def _showFinished(self):
		tkMessageBox.showinfo("MP3 Encoder", "Finished Decoding in " + str(self.d.getDifTime()) + " Seconds")
		
	def startHandler(self):
	  	while 1:
	  		time.sleep(0.5)
	  		self.root.event_generate('<<Handler>>', when='tail')
	def runGui(self):
		guiThread = threading.Thread(target=self.root.mainloop())
		#guiThread.setDaemon(1)
		guiThread.start()

	def getSelection(self):
		return self.options.get()
	def updateProgressBar(self):

		filesDoneOld = 0

		while self.encodeFinished is not True:
			time.sleep(0.1)
			if self.d is not None:
				filesDone = self.d.getFilesDone()
				print "Files done: ", filesDone
				self.progressLabel.config(text=(str(filesDone) + " of " + str(self.progressBarLength) + " files encoded") + " | " +  "Time: " + str(self.d.getDifTime()) + " secs")
				change = filesDone - filesDoneOld
				if change is not 0:
					self.progressbar.step(amount=change)
					# print "Change Progress: ", change
					filesDoneOld = filesDone
				else:
					pass

			else:
				self.progressLabel.config(text="Encoder Object is None, something unexpected happend, please contact...")
		currentValue = int(self.progressbar["value"])
		if currentValue is not 0:
			self.progressbar.step(self.progressBarLength-currentValue)

		self.progressLabel.config(text="Finished" + "| " +  "Time: " + str(self.d.getDifTime()) + " secs")
		print
		print "Progressbar Thread terminated"
		print 
	def callback(self):

		if self._output is None or self._input is None:
			print "Please select In- or Output"
			self.showFileInputError()
		else:
			if self._output == "" or self._input == "":
				print "Please select valid In- or Output"
				self.showFileInputError()
			else:

				self.encodeButton.config(state=DISABLED)
				self.encodeFinished = False

				print "Start Decoding"
				self.counter = 0
				self.progressBarLength = self.countFiles(self._input)

				print "Setting progressbar max to amount of files"
				self.progressbar.config(maximum=self.progressBarLength)	
				print "Encoder is running now"

				progressBarThread = threading.Thread(target=self.updateProgressBar)
				progressBarThread.setDaemon(1)
				progressBarThread.start()
				
			
				EncoderThread = threading.Thread(target=self.startEncoder)
				EncoderThread.setDaemon(1)
				EncoderThread.start()
				print "Thread started"

	#########################################
	# Disable
	#########################################

	def disablePresets(self):
		print len(self.presets)
		for pre in self.presets:
			pre.config(state = DISABLED)
			pre.config(bg = 'white')
	def disableBitrate(self):
		self.bitrate.config(state = DISABLED)
		self.bitrate.config(bg = 'gray' )
	def disableVBRQuality(self):
		self.vbrQuality.config(state = DISABLED)
		self.vbrQuality.config(bg = 'gray' )

	#########################################
	# Enable
	#########################################
	def enablePresets(self):
		for pre in self.presets:
			pre.config(state = NORMAL)
			pre.config(bg = 'yellow')
	def enableVBRQuality(self):
		self.vbrQuality.config(state = NORMAL)
		self.vbrQuality.config(bg = 'yellow' )
	def enableBitrate(self):
		self.bitrate.config(state = NORMAL)
		self.bitrate.config(bg = 'yellow' )


my = Gui()
my.runGui()