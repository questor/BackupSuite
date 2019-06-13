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

def generateCommandListCompression(toolpath, outputpath, filelist):
	logging.info("generate command list for compression")

	cmdlist = []
	for file in filelist:
		filename, extension = os.path.splitext(file)
		# extension = '.ext'
		lowerExt = extension.lower()

		#lepton compresses better than precomp-cpp on jpegs

		if(lowerExt == '.jpg') or (lowerExt == '.jpeg'):
			cmdlist.append("%s/lepton -singlethread -allowprogressive %s %s/%s.lepton" % (toolpath, file, outputpath, file))
		elif(lowerExt == '.mp3'):			# don't recompress with lzma, it's bigger afterwards!
			cmdlist.append("%s/precomp-cpp -lt1 -cn -o%s/%s.pcf %s" % (toolpath, outputpath, file, file))
		elif(lowerExt == '.png') or (lowerExt == '.gif') or (lowerExt == '.pdf') or (lowerExt == 'zip') or (lowerExt == '.gzip') or (lowerExt == '.bzip2'):
			cmdlist.append("%s/precomp-cpp -lt1 -cl -o%s/%s.pcf %s" % (toolpath, outputpath, file, file))
			# TODO: check if here do not recompress it with lzma but instead use zpag afterwards?
			# TODO: make list of files to be deleted afterwards because they are temporary
		else:
			cmdlist.append("%s/zpaq715 a %s/%s.zpaq %s -m5 -t1" % (toolpath, outputpath, file, file))
			# -m5 is dead slow :/
			# -m4 is much faster already and still better than lzma2 from precomp-cpp

			#-rwxr-xr-x 1 devenv root    2036046 Jun 13 15:49 pixelwp2.png*
			#-rw-rw-r-- 1 devenv devenv 12543751 Jun 13 16:55 pixelwp2.pcf
			#-rw-rw-r-- 1 devenv devenv  1726904 Jun 13 16:54 pixelwp2.pcf_LZMA
			#-rw-rw-r-- 1 devenv devenv  1439668 Jun 13 16:56 test.zpaq (-m5) (50sec)
			#-rw-rw-r-- 1 devenv devenv  1517409 Jun 13 16:59 test.zpaq (-m4) (13sec)
			
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


	cmds = generateCommandListCompression(args.tools, args.output, files)

	#for cmd in cmds:
	#	print("cmd: %s" % (cmd))

	#pool.map(work, cmds)

