import multiprocessing
import subprocess
import os
import argparse

import logging

def work(cmd):
	#logging.info("running %s" % (cmd))
	result = subprocess.run(cmd, stdout=subprocess.PIPE)
	return result
	#return subprocess.call(cmd, shell=False, stderr=subprocess.PIPE)

def generateFilelist(path):
	logging.info("generate file list from: %s"%(path))
	retDirs = []
	retFiles = []
	for root,directories,filenames in os.walk(path):
		for directory in directories:
			retDirs.append(os.path.join(root,directory))
		for filename in filenames:
			retFiles.append(os.path.join(root, filename))
	return retDirs, retFiles

def generateCommandListHashing(toolpath, filelist):
	logging.info("generate command list for hashing")

	cmdlist = []
	for file in filelist:
		cmd = []
		cmd.append("%s/meowhash" % (toolpath))
		cmd.append("%s" % (file))
		cmd.append("--nologo")
		cmdlist.append(cmd)

	return cmdlist

def generateCommandListCompression(toolpath, filelist):
	logging.info("generate command list for compression")

	cmdlist = []
	for file in filelist:
		filename, extension = os.path.splitext(file)
		# extension = '.ext'
		if(extension == '.jpg') or (extension == 'jpeg'):
			cmdlist.append("%s/lepton blabla %s" % (toolpath, file))
		else:
			cmdlist.append("%s/zpaq715 blabla %s" % (toolpath, file))
	return cmdlist

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)

	print("BackupIt V0.1")

	parser = argparse.ArgumentParser(description="Backup Control Script")
	parser.add_argument('-i', '--input', help="Folder to Backup FROM", required=True)
	parser.add_argument('-o', '--output', help="Folder to Backup TO", required=True)
	parser.add_argument('-t', '--tools', help="Folder to compiled tools", required=True)
	args = parser.parse_args()

	count = multiprocessing.cpu_count()
	print("-Number CPUs found: %d" % (count))

	dirs, files = generateFilelist(args.input)
	print("-Found %d files" % (len(files)))

	#for file in files:
	#	print("file: %s" % (file))

	print("-Generate hashing commands")
	cmds = generateCommandListHashing(args.tools, files)
	
	#for cmd in cmds:
	#	print("cmd: %s" % (cmd))

	print("-Generating the hashes of the files")
	pool = multiprocessing.Pool(processes=count)
	hashresults = pool.map(work, cmds)

	for result in hashresults:
		if(result.returncode != 0):
			print("HASHERROR: %s(%d)" % (result.stdout, result.returncode))
		else:
			print(result.stdout)


	cmds = generateCommandListCompression(args.tools, files)

	#for cmd in cmds:
	#	print("cmd: %s" % (cmd))

	#pool.map(work, cmds)

