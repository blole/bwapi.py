#!/usr/bin/python2
import argparse
import sys
import os
import re
import time
import subprocess

def fullpath(path):
	return os.path.join(os.getcwd(), path)

class Ini:
	def __init__(self, path):
		self.path = path
		if not os.path.isfile(path):
			sys.exit("error: ini file '"+fullpath(self.path)+"' not found")
		with open(path) as f:
			self.text = f.read()
	
	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()
	
	def set(self, key, value):
		line = re.compile(r'^('+key+'[^\S\n\r]*=[^\S\n\r]*).*$', re.MULTILINE)
		(self.text, subs) = line.subn('\\1'+value, self.text)
		if subs < 1:
			sys.exit("error: key '"+key+"' not found in '"+fullpath(self.path)+"'")
	
	def close(self):
		with open(self.path, 'w') as f:
			f.write(self.text)
		

parser = argparse.ArgumentParser(description='run starcraft with bwapi injected')
parser.add_argument('-s', '--starcraft-dir',	help='path to starcraft dir',					metavar='DIR', default='.')
parser.add_argument('-a', '--ai',				help='ai dll',									metavar='DLL', required=True)
parser.add_argument('-t', '--tournament',		help='tournament dll',							metavar='DLL')
parser.add_argument('-d', '--debug',			help='inject BWAPId.dll instead of BWAPI.dll',	action='store_true')
parser.add_argument('-v', '--verbose',			help='print command before executing it',		action='store_true')
parser.add_argument('-i', '--injectory',		help='path to injectory',						metavar='EXE', default='injectory')
parser.add_argument('--args',					help='args to pass to injectory',				nargs=argparse.REMAINDER, default='')
args = parser.parse_args()


os.chdir(args.starcraft_dir)

ini = Ini('bwapi-data/bwapi.ini')

#set ai
if not os.path.isfile(args.ai):
	sys.exit("error: ai dll file '"+fullpath(args.ai)+"' not found")
if args.debug:
	ini.set('ai_dbg', args.ai)
else:
	ini.set('ai', args.ai)

#set tournament
if args.tournament:
	if not os.path.isfile(args.tournament):
		sys.exit("error: tournament dll file '"+fullpath(args.tournament)+"' not found")
	ini.set('tournament', args.tournament)
ini.close()


#run
debugSuffix = 'd' if args.debug else ''
command = args.injectory+' --launch starcraft.exe --inject bwapi-data/BWAPI'+debugSuffix+'.dll '+' '.join(args.args)
if args.verbose:
	print command
subprocess.call(command.split())
time.sleep(3)
