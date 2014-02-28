#! /usr/bin/env python

################################################
### Name: Encoder.py
### Description: encoder for encoding all mp3's with lame in a directory recursivly
### Author: Malte Koch
### exec: python threaded_gui.py
### Version: 0.2
### Envirnoment: Python2.7
### Operating System: Linux/GNU, Windows
#################################################


import subprocess
import sys, os
import time
import threading 
import shutil # copy funtion 
from datetime import datetime
import platform

class Encoder:

	q = []
	MAX_THREADS = 4
	preset = None
	bitrate = None
	vbr = None
	fast_mode = None
	filesDone = 0

	def __init__(self, encodePath="", outputPath="", preset=None, bitrate=None, fastMode=True, vbr=None, threads=4, guiMode=False):

		if (os.path.exists(encodePath)) is False:
			print "The given path does not exist!, Exit 0"
			sys.exit(0)
		else:
			if os.path.isdir(encodePath) is False:
				print "The given is not a directory!, Exit 0"
				sys.exit(0)

		if (os.path.exists(outputPath)) is False:
			print "The given output-path does not exist!"
			if os.path.isdir(outputPath) is False:
				print ""
				
				_input= raw_input("Do you want to create it?[yes]")
				if self.checkInput(_input) is True:
					os.makedirs(outputPath)
				else:
					print "Exit 0"
					sys.exit(0)
		
		### Make System Check
		check = SystemCheck()
		if check.isWindows() is True:
			print "System: Windows"
			self.lamePath = os.path.join(self.getWorkingDirectory(), "lame.exe")
			print "lame: ", self.lamePath
		else:

			if check.isX64() is True:
				print "System: Unit/Linux 64 Bit"
				self.lamePath = os.path.join(self.getWorkingDirectory(), "lame_64")
			else:
				print "System: Unit/Linux 32 Bit"
				self.lamePath = os.path.join(self.getWorkingDirectory(), "lame")
		print "Lame Path: ", self.lamePath

		if guiMode:

			self.start_time = time.clock()
			r = RestoreDirectoryStructure(encodePath, outputPath)
			l = LameCommandCreator(self.lamePath)
			if preset:
				l.addPreset(preset)
			if vbr:
				l.addVBR(vbr)
			if bitrate:
				l.setBitrate(bitrate)
			if fastMode:
				l.setFastMode()

			self.encodePath = encodePath
			self.outputPath = outputPath
			self.MAX_THREADS = threads
			self.guiMode = guiMode
			self.l = l

		else:


			_preset = raw_input("Want to set a Preset for quality? e.g. Extreme, Medium...[YES]")

			if self.checkInput(_preset) is True:
				_selc_preset = raw_input("What preset do you choose? [I]nsane, [E]xtreme, [M]edium, [S]tandard")
				if len(_selc_preset) != 1:
					print "Wrong Input, please try again!"
					sys.exit(0) 
				else: 
					_selc_preset = _selc_preset.lower()
					if _selc_preset == "i":
						self.preset = LameCommandCreator.PRESET_INSANE
					elif _selc_preset == "e":
						self.preset = LameCommandCreator.PRESET_EXTREM
					elif _selc_preset == "m":
						self.preset = LameCommandCreator.PRESET_MEDIUM
					elif _selc_preset == "s":
						self.preset = LameCommandCreator.PRESET_STANDARD
					else:
						print "Wrong Input, no preset set!"
						sys.exit(0)
			else: 
				#Individual Quality
				print ""
				print "You must select VBR (Variable bitrate) or Constant Bitrate!"
				print "If you dont select any of it the program will terminate."
				print "" 
				_vbr = raw_input("Do you want to set a VBR?[No]")
				print _vbr, self.checkInput(_vbr)
				if self.checkInput(_vbr) is True and (not _vbr==''):
					_vbr_num = raw_input("Please type in the VBR-Quality.[0-9] (0=high quality,bigger files. 9=smaller files)")
					if _vbr_num.isdigit() is True:
						if int(_vbr_num >= 0) and int(_vbr_num) < 10:
							self.vbr = int(_vbr_num)
						else:
							print "Not a valid constant bitrate, please set it between 0 to 9 next time :) . Program will terminate."
							sys.exit(0)
					else:
						print "This is not a digit, program will terminate."
						sys.exit(0)

				else:
					_bitrate = raw_input("What Constant Bitrate do you want?[32-320]")
					if _bitrate.isdigit() is True:
						if int(_bitrate) > 31 and int(_bitrate) < 321:
							self.bitrate = int(_bitrate)
						else:
							print "Not a valid constant bitrate, please set it between 32 to 320 next time. Program will terminate."
							sys.exit(0)
					else:
						print "This is not a digit, program will terminate."
						sys.exit(0)

			_fast_mode = raw_input("Enable Fast Mode?[YES] (Faster, but less quality)")
			if self.checkInput(_fast_mode):
				self.fast_mode = True
			else:
				self.fast_mode = False


			_threads = raw_input("How many instances of \"lame\" do you want to run simultaneously(How many Threads)?[4]")
			if _threads.isdigit() is True:
				if int(_threads) > 0:
					self.MAX_THREADS = int(_threads)
				else: 
					print "Number must be larger than 0"
					print ""
					print "Continuing with 4 Threads"
			else:
				pass

			start_now = raw_input("Do you want to start encoding your tracks now?[Yes]")
			if self.checkInput(start_now) is True: 

				r = RestoreDirectoryStructure(encodePath, outputPath)
				l = LameCommandCreator(self.lamePath)
				if self.preset:
					l.addPreset(self.preset)
				if self.vbr:
					l.addVBR(self.vbr)
				if self.bitrate:
					l.setBitrate(self.bitrate)
				if self.fast_mode:
					l.setFastMode()

				self.l = l
				self.encodePath = encodePath
				self.outputPath = outputPath
				self.guiMode = False
			else:
				print "Abort!"
				sys.exit(0)
	def startEncoder(self):
		try:
			self.encode(self.encodePath, self.outputPath, self.l, self.MAX_THREADS, self.guiMode)
			self.printFinish(self.guiMode)
		except:
			print "An Unexpected Error occured !"
			raise


	def checkInput(self, r_input):
		r_input = r_input.lower() #to lower case
		print r_input
		if (r_input == '') or (r_input == 'yes') or (r_input == "y"):
			return True
		else:
			return False

	def encode(self, _input, _output, _LameCommandCreator, _maxThreads, guiMode):
		
		self.tStart = datetime.now()
	

		for _file in os.listdir(_input):
			_file = os.path.join(_input, _file)

			if os.path.isdir(_file) is True:
				print "analyse: " , _file
				self.encode(_file, os.path.join(_output, os.path.basename(_file)), _LameCommandCreator, _maxThreads, guiMode)
			else:

				out_file = os.path.join(_output, os.path.basename(_file))
				
				if os.path.splitext(_file)[1] == ".mp3" or os.path.splitext(_file)[1] == ".wav":
					
					
					# start encoding
					_LameCommandCreator.setFileIn(_file)
					_LameCommandCreator.setFileOut(out_file)

					print "Exec: ", _LameCommandCreator.getCommand()
					if guiMode:
						currentRunningInstances = 4
					else:
						currentRunningInstances = 1

					if threading.activeCount() is (_maxThreads+currentRunningInstances):
						
						print "4 Threads are Running, waiting for a Thread to terminate"

						while True:
							if threading.activeCount() < (_maxThreads+currentRunningInstances):
								break
							else:
								print "Active Count: ", threading.activeCount(), " < ", (_maxThreads+currentRunningInstances)
								time.sleep(1)

					print "A Thread has finished, start a new one"
					t = threading.Thread(target=self.call, args=(_LameCommandCreator, "bug" ))
					t.daemon = True
					t.start()
				else:
					#Copy all Files, which are no audio files
					print "Copy ", _file , " to ", out_file
					self.copyFile(_file, out_file)
					self.filesDone = self.filesDone + 1
	
	def getDifTime(self):
		try:
			tEnd = datetime.now()
			dif = tEnd - self.tStart
			return dif.seconds
		except:
			return 0
	def printFinish(self, guiMode):
		if guiMode:
			currentRunningInstances = 4
		else:
			currentRunningInstances = 1

		while threading.activeCount() != currentRunningInstances:
			print "Wait until all threads are done!"
			print threading.activeCount()
			time.sleep(2)
		print ""
		print "Encoding Time: ", self.getDifTime(), " Seconds"



	def copyFile(self, file_in, file_out):
		shutil.copy(file_in, file_out)
					
	def getWorkingDirectory(self):
		return os.getcwd()
	def call(self, com, non_sense):
		print subprocess.check_output(com.getCommand())
		self.filesDone = self.filesDone + 1
	def getFilesDone(self):
		return self.filesDone

class RestoreDirectoryStructure(object):
	def __init__(self, _input, output):
		self.restore(_input, output)
	def restore(self, _input, output):
		
		for _file in os.listdir(_input):
			_file = os.path.join(_input, _file)
			if os.path.isdir(_file) is True:
				path = os.path.join(output, os.path.basename(_file))
				print "Make Dir: ", path
				if not os.path.exists(path):
					os.makedirs(path)
				self.restore(_file, path)
	
class SystemCheck:
	def __init__(self):
		pass
	def isWindows(self):
		return sys.platform.startswith('win')
	def isLinux(self):
		return sys.platform.startswith('linux')
	def getPlatform(self):
		return sys.platform
	def getName(self):
		return os.name
	def getEnviron(self):
		return os.environ
	def isX64(self):
		return (platform.machine() == "x86_64")

class LameCommandCreator:

	PRESET_EXTREM = "extreme"
	PRESET_MEDIUM = "medium"
	PRESET_STANDARD = "standard"
	PRESET_INSANE = "insane"

	lame_path = None
	higher_quality = None
	bitrate = None
	preset = None
	file_out = None
	file_in = None
	fast_mode = None
	vbr = None

	def __init__(self, lame_path):
		self.lame_path = lame_path

	def setFastMode(self):
		self.fast_mode = "-f"
	def setHigherQuality(self):
		self.higher_quality = "-h"

	def setBitrate(self, bitrate):
		self.bitrate = bitrate
	def addPreset(self, preset):
		self.preset = preset
	def addVBR(self, vbr): #0 -9 - 0=bigger, 9=smaller Files
		self.vbr = vbr

	def setFileOut(self, output):
		self.file_out = output
	def setFileIn(self, _input):
		self.file_in = _input

	def getCommand(self):

		self.Command = []
		self.Command.append(self.lame_path)

		if self.bitrate is not None:
			self.Command.append("-b")
			self.Command.append(str(self.bitrate))
		if self.vbr is not None:
			self.Command.append("-V")
			self.Command.append(str(self.vbr))
		if self.preset is not None:
			self.Command.append("--preset")
			self.Command.append(self.preset)
		if self.higher_quality is not None:
			self.Command.append(self.higher_quality)
		if self.fast_mode is not None:
			self.Command.append(self.fast_mode)

		self.Command.append(self.file_in)
		self.Command.append(self.file_out)
		return self.Command

if len(sys.argv) == 3:
	print "Start init procedure"
	print 
	d = Encoder(encodePath=sys.argv[1], outputPath=sys.argv[2], guiMode=False)
	d.startEncoder()
else:
	print 
	print "Please provide a Source and a Destination directory!"
	print "Execute like: "
	print "python Encoder.py /home/user/Music/ /home/user/encoded_Music/"
	print
	print
	print "Programm will terminate"