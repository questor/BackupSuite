import multiprocessing
import subprocess
import os
import argparse

import logging

def work(cmd):
	result = subprocess.run(cmd, stdout=subprocess.PIPE)
	return result

def generateFilelist(path):
	retDirs = []
	retFiles = []
	for root,directories,filenames in os.walk(path):
		for directory in directories:
			retDirs.append(os.path.join(root,directory))
		for filename in filenames:
			retFiles.append(os.path.join(root, filename))
	return retDirs, retFiles

def generateCommandListHashing(toolpath, filelist):
	cmdlist = []
	for file in filelist:
		cmd = []
		cmd.append("%s/meowhash" % (toolpath))
		cmd.append("%s" % (file))
		cmd.append("--nologo")
		cmdlist.append(cmd)

	return cmdlist

def getFilesizes(filelist):
	completeSize = 0
	for file in filelist:
		completeSize += os.path.getsize(file)
	return completeSize

def generateCommandListCompression(toolpath, outputpath, filelist, inputpath):
	cmdlist = []
	for file in filelist:
		filename, extension = os.path.splitext(file)
		# extension = '.ext'
		lowerExt = extension.lower()

		#lepton compresses better than precomp-cpp on jpegs

		outputfile = file.replace(inputpath, "")
		outputfile = os.path.join(args.output, outputfile)

		if(lowerExt == '.jpg') or (lowerExt == '.jpeg'):
			cmd = []
			cmd.append("%s/lepton" % (toolpath))
			cmd.append("-singlethread")
			cmd.append("-allowprogressive") 
			cmd.append("%s" % (file))
			cmd.append("%s.lepton" % (outputfile))
			cmdlist.append(cmd)
		elif(lowerExt == '.mp3'):			# don't recompress with lzma, it's bigger afterwards!
			cmd = []
			cmd.append("%s/precomp-cpp" % (toolpath))
			cmd.append("-lt1")
			cmd.append("-cn")
			cmd.append("-o%s.pcf" % (outputfile))
			cmd.append("%s" % (file))
			cmdlist.append(cmd)
		elif(lowerExt == '.png') or (lowerExt == '.gif') or (lowerExt == '.pdf') or (lowerExt == 'zip') or (lowerExt == '.gzip') or (lowerExt == '.bzip2'):
			cmd = []
			cmd.append("%s/precomp-cpp" % (toolpath))
			cmd.append("-lt1")
			cmd.append("-cl")
			cmd.append("-o%s.pcf" % (outputfile))
			cmd.append("%s" % (file))
			cmdlist.append(cmd)
			# TODO: check if here do not recompress it with lzma but instead use zpag afterwards?
			# TODO: make list of files to be deleted afterwards because they are temporary
		else:
			cmd = []
			cmd.append("%s/zpaq715" % (toolpath))
			cmd.append("a")
			cmd.append("%s.zpaq" % (outputfile))
			cmd.append("%s" % (file))
			cmd.append("-m4")
			cmd.append("-t1")
			cmdlist.append(cmd)
			# -m5 is dead slow :/
			# -m4 is much faster already and still better than lzma2 from precomp-cpp

			#-rwxr-xr-x 1 devenv root    2036046 Jun 13 15:49 pixelwp2.png*
			#-rw-rw-r-- 1 devenv devenv 12543751 Jun 13 16:55 pixelwp2.pcf
			#-rw-rw-r-- 1 devenv devenv  1726904 Jun 13 16:54 pixelwp2.pcf_LZMA
			#-rw-rw-r-- 1 devenv devenv  1439668 Jun 13 16:56 test.zpaq (-m5) (50sec)
			#-rw-rw-r-- 1 devenv devenv  1517409 Jun 13 16:59 test.zpaq (-m4) (13sec)
			
	return cmdlist

if __name__ == '__main__':
	#logging.basicConfig(level=logging.INFO)

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

	filesizesUncompressed = getFilesizes(files)
	print("-All filesizes uncompressed: %dMB(%d)" % (filesizesUncompressed/(1024*1024), filesizesUncompressed))

	#for file in files:
	#	print("file: %s" % (file))

	print("-Generate hashing commands")
	cmds = generateCommandListHashing(args.tools, files)
	
	#for cmd in cmds:
	#	print("cmd: %s" % (cmd))

	print("-Generating the hashes of the files")
	pool = multiprocessing.Pool(processes=count)

	hashresults = []
	for res in pool.imap_unordered(work, cmds):
		hashresults.append(res)

	errorfiles = []
	hashestowrite = []
	for result in hashresults:
		if(result.returncode != 0):
			print("HASHERROR: %s(%d)" % (result.stdout, result.returncode))
			errorfiles.append(result.stdout)
		else:
			#print(result.stdout)
			hashestowrite.append(result.stdout)

#MeowHash 12B741B3-5929BA8F-6E329A7D-AF4FBB29 jpegs/Gpx-SP-107-2560.jpg

	print("-Write hashes to file in output path")
	with open(args.output + "/filehashes.txt", 'w') as f:
		for item in hashestowrite:
			itemStr = item.decode('UTF-8')
			itemStr = itemStr.replace(args.input, "")
			f.write("%s\n" % itemStr)
		f.close()

	# TODO: create folderstructure in destination folder
	for dir in dirs:
		dir = dir.replace(args.input, "")
		path = os.path.join(args.output, dir)
		#print("create folder: %s" % (path))
		os.makedirs(path, exist_ok=True)

	print("-Generate commands to compress data")
	cmds = generateCommandListCompression(args.tools, args.output, files, args.input)

	print("-Compress all files")
	#for cmd in cmds:
	#	print("cmd: %s" % (cmd))
	compressresults = []
	for res in pool.imap_unordered(work, cmds):
		compressresults.append(res)

	for result in compressresults:
		if(result.returncode != 0):
			print("COMPRESSERROR: %s(%d)" % (result.stdout, result.returncode))

	print("-Finished!")
