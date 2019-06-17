import multiprocessing
import subprocess
import os
import argparse

import logging

def runProcess(cmd):
	result = subprocess.run(cmd, stdout=subprocess.PIPE)
	return result

def uncompressAndGenerateHash(args):
	# decompress to temp

	file = args[0]
	inputpath = args[1][0]
	toolpath = args[1][1]

	filename, extension = os.path.splitext(file)
	lowerExt = extension.lower()

	outputfile = filename.replace(inputpath, "")
	outputfile = os.path.join("/tmp/", outputfile)

	if(lowerExt == '.lepton'):
		cmd = []
		cmd.append("%s/lepton" % toolpath)
		cmd.append("-singlethread")
		cmd.append("-allowprogressive") 
		cmd.append("%s" % file)					# is already with .lepton!
		cmd.append("%s" % outputfile)
		result = subprocess.run(cmd, stdout=subprocess.PIPE)
		if(result.returncode != 0):
			return ""

	elif(lowerExt == '.pcf'):
		cmd = []
		cmd.append("%s/precomp-cpp" % (toolpath))
		cmd.append("-r")
		cmd.append("-lt1")
		cmd.append("-o%s" % outputfile)
		cmd.append("%s" % file)
		result = subprocess.run(cmd, stdout=subprocess.PIPE)
		if(result.returncode != 0):
			return ""

	elif(lowerExt == '.zpaq'):
		cmd = []
		cmd.append("%s/zpaq715" % toolpath)
		cmd.append("x")
		cmd.append("%s" % file)
		cmd.append("-to");
		cmd.append("%s" % outputfile);
		cmd.append("-t1")
		result = subprocess.run(cmd, stdout=subprocess.PIPE)
		if(result.returncode != 0):
			return ""

	else:
		return ""

	cmd = []
	cmd.append("%s/meowhash" % toolpath)
	cmd.append("%s" % outputfile)
	cmd.append("--nologo")
	result = subprocess.run(cmd, stdout=subprocess.PIPE)
	if(result.returncode != 0):
		return ""

	os.remove(outputfile)

	ret = result.stdout.decode('UTF-8')

	print(ret)
	return ret


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
			cmd.append("%s/zpaq715" % toolpath)
			cmd.append("a")
			cmd.append("%s.zpaq" % outputfile)
			cmd.append("%s" % file)
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
	parser.add_argument('-i', "--input", help="Folder to Backup FROM", required=True)
	parser.add_argument('-o', "--output", help="Folder to Backup TO", required=False)
	parser.add_argument('-t', "--tools", help="Folder to compiled tools", required=True)
	parser.add_argument('-c', "--create", help="Create compressed Structure from input", required=False, action="store_true")
	parser.add_argument('-v', "--verify", help="Verify compressed structure", required=False, action="store_true")
	args = parser.parse_args()

	count = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(processes=count)
	print("-Number CPUs found: %d" % (count))

	if(args.create):
		print("-Create archive")

		dirs, files = generateFilelist(args.input)
		print("-Found %d files" % (len(files)))

		#filesizesUncompressed = getFilesizes(files)
		#print("-All filesizes uncompressed: %dMB(%d)" % (filesizesUncompressed/(1024*1024), filesizesUncompressed))

		print("-Generate hashing commands")
		cmds = generateCommandListHashing(args.tools, files)
		
		print("-Generating the hashes of the files")
		hashresults = []
		for res in pool.imap_unordered(runProcess, cmds):
			hashresults.append(res)

		errorfiles = []
		hashestowrite = []
		for result in hashresults:
			if(result.returncode != 0):
				print("HASHERROR: %s(%d)" % (result.stdout, result.returncode))
				errorfiles.append(result.stdout)
			else:
				hashestowrite.append(result.stdout)

		print("-Write hashes to file in output path")
		with open(args.output + "/filehashes.txt", 'w') as f:
			for item in hashestowrite:
				itemStr = item.decode('UTF-8')
				itemStr = itemStr.replace(args.input, "")
				f.write("%s\n" % itemStr)
			f.close()

		print("-Create folder structure in ouput path")
		for dir in dirs:
			dir = dir.replace(args.input, "")
			path = os.path.join(args.output, dir)
			os.makedirs(path, exist_ok=True)

		print("-Generate commands to compress data")
		cmds = generateCommandListCompression(args.tools, args.output, files, args.input)

		print("-Compress all files")
		compressresults = []
		for res in pool.imap_unordered(runProcess, cmds):
			compressresults.append(res)

		for result in compressresults:
			if(result.returncode != 0):
				print("COMPRESSERROR: %s(%d)" % (result.stdout, result.returncode))

	print("-Finished!")

	if(args.verify):
		print("-Verify archive")
		dirs, files = generateFilelist(args.input)
		print("-Found %d files" % len(files))

		print("-Create folder structure in ouput path")
		for dir in dirs:
			dir = dir.replace(args.input, "")
			path = os.path.join("/tmp/", dir)
			os.makedirs(path, exist_ok=True)

		args = [args.input, args.tools]
		new_iterable = ([x, args] for x in files)

		verifyResults = []
		for res in pool.imap_unordered(uncompressAndGenerateHash, new_iterable):
			verifyResults.append(res)

		# here in verifyResults the path is still wrong because it's lead by "/tmp/" which need to be removed...

		print(verifyResults)

		# create set of all file hashes
		originalHashes = {}
		with open(args.input + "/filehashes.txt", 'r') as f:
			for line in f:
				hashfunc, hashvalue, path = line.split()
				originalHashes[hashvalue] = path

# precomp seems to be asking something? maybe overwrite confirmation?

# ['', '', '', '', '', '', '', '', '', '', 'MeowHash 81A3D9CD-4D2C35FB-80C05C01-05D3820E /tmp/pngs/pixelwp2.png', 'MeowHash F45ADA0A-8D929581-2CB3949F-2D2C3C21 /tmp/pngs/pixelwp16.png', 'MeowHash 0F09791B-46556AF7-7893EDFC-2D3024AB /tmp/pngs

#if word in words:
#	print word
