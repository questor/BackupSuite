
# TODOs:
# - verify doesn't work with incremental backups as not all files in the database
#   are available on the media
# - uncompressible zpaq is handled by zpaq, precomp(especially gif) not yet. for uncompressible
#   gif even worse a defect file is left on the disc!
# - gif-handling seems to be broken in precomp, files are decompressed not the same as the original
#   ones, so for the time beeing gif is processed through zpaq

# - on windows you should NOT use drive-characters because they will end up in the hash-file-list and
#   database and you can not easily use the same archive on linux

import multiprocessing
import subprocess
import os
import sys
#import re
import argparse
import tempfile
import tqdm

import shutil
from colorama import Fore, Back, Style
import colorama

counter = None

class Counter(object):
    def __init__(self, initval=0):
        self.val = multiprocessing.Value('i', initval)
        self.lock = multiprocessing.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value

def init(args):
	global counter
	counter = args

def normalizePath(path):
#	return os.path.normpath(os.sep.join(re.split(r'\\|/', path)))
	return path.replace("\\", "/")

def runProcess(cmd):
	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if(result.returncode != 0):
		print((Fore.RED + "CMD FAILED: %s" + Style.RESET_ALL) % cmd)
	return result

def compressFiles(args):
	global counter

	counter.increment()

	file = args[0]

	toolpath = args[1][0]
	outputpath = args[1][1]
	inputpath = args[1][2]
	tempfolder = args[1][3]

	filename, extension = os.path.splitext(file)
	lowerExt = extension.lower()

	#lepton compresses better than precomp-cpp on jpegs

	outputfile = file.replace(inputpath, "")
	outputfile = os.path.join(outputpath, outputfile)

	cmd = []
	if(lowerExt == '.jpg') or (lowerExt == '.jpeg'):
		if sys.platform == 'win32':
			cmd.append("%s/lepton.exe" % toolpath)
		else:
			cmd.append("%s/lepton" % toolpath)
		cmd.append("-singlethread")
		cmd.append("-allowprogressive") 
		cmd.append("%s" % (file))
		cmd.append("%s.lepton" % (outputfile))
	elif(lowerExt == '.mp3'):			# don't recompress with lzma, it's bigger afterwards!
		cmd.append("%s/precomp-cpp" % (toolpath))
		cmd.append("-lt1")
		cmd.append("-cn")
		cmd.append("-o%s.pcf" % (outputfile))
		cmd.append("-u%s/~precomp_temp_%d" % (tempfolder, counter.value()))
		cmd.append("%s" % (file))
	elif(lowerExt == '.png') or (lowerExt == '.pdf') or (lowerExt == 'zip') or (lowerExt == '.gzip') or (lowerExt == '.bzip2'):
		cmd.append("%s/precomp-cpp" % (toolpath))
		cmd.append("-lt1")
		cmd.append("-cl")
		cmd.append("-o%s.pcf" % (outputfile))
		cmd.append("-u%s/~precomp_temp_%d" % (tempfolder, counter.value()))
		cmd.append("%s" % (file))
	else:
		cmd.append("%s/zpaq715" % toolpath)
		cmd.append("a")
		cmd.append("%s.zpaq" % outputfile)
		cmd.append("%s" % file)
		cmd.append("-m4")
		cmd.append("-t1")
		# -m5 is dead slow :/
		# -m4 is much faster already and still better than lzma2 from precomp-cpp

		#-rwxr-xr-x 1 devenv root    2036046 Jun 13 15:49 pixelwp2.png*
		#-rw-rw-r-- 1 devenv devenv 12543751 Jun 13 16:55 pixelwp2.pcf
		#-rw-rw-r-- 1 devenv devenv  1726904 Jun 13 16:54 pixelwp2.pcf_LZMA
		#-rw-rw-r-- 1 devenv devenv  1439668 Jun 13 16:56 test.zpaq (-m5) (50sec)
		#-rw-rw-r-- 1 devenv devenv  1517409 Jun 13 16:59 test.zpaq (-m4) (13sec)

	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if(result.returncode != 0):
		print((Fore.RED + "COMPRESS FAILED: %s copy file without touching it" + Style.RESET_ALL) % cmd)
		shutil.copyfile(file, outputfile)
		result.returncode = 0
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

	#print("uncompressing %s to tmp" % filename)

	if(lowerExt == '.lepton'):
		cmd = []
		if sys.platform == 'win32':
			cmd.append("%s/lepton.exe" % toolpath)
		else:
			cmd.append("%s/lepton" % toolpath)
		cmd.append("-singlethread")
		cmd.append("-allowprogressive") 
		cmd.append("%s" % file)					# is already with .lepton!
		cmd.append("%s" % outputfile)
	elif(lowerExt == '.pcf'):
		cmd = []
		cmd.append("%s/precomp-cpp" % (toolpath))
		cmd.append("-r")
		cmd.append("-lt1")
		cmd.append("-o%s" % outputfile)
		cmd.append("%s" % file)
	elif(lowerExt == '.zpaq'):
		cmd = []
		cmd.append("%s/zpaq715" % toolpath)
		cmd.append("x")
		cmd.append("%s" % file)
		cmd.append("-to");
		cmd.append("%s" % outputfile);
		cmd.append("-t1")
	else:
		print((Fore.RED + "VERIFY ERROR(1): %s (%s)" + Style.RESET_ALL) % (file, lowerExt))
		return ""

	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if(result.returncode != 0):
		print((Fore.RED + "VERIFY ERROR(2): %s" + Style.RESET_ALL) % file)
		return ""

	cmd = []
	cmd.append("%s/meowhash" % toolpath)
	cmd.append("%s" % outputfile)
	cmd.append("--nologo")
	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if(result.returncode != 0):
		print((Fore.RED + "VERIFY ERROR(3): %s" + Style.RESET_ALL) % file)
		return ""

	os.remove(outputfile)

	if sys.platform == 'win32':
		ret = result.stdout.decode('cp1252')
	else:
		ret = result.stdout.decode('UTF-8')
	return ret

def generateFilelist(path):
	retDirs = []
	retFiles = []
	for root,directories,filenames in os.walk(path):
		for directory in directories:
			retDirs.append(normalizePath(os.path.join(root,directory)))
		for filename in filenames:
			retFiles.append(normalizePath(os.path.join(root, filename)))
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

def mergeFilehashesToDatabase(databasepath, inputpath):
	database = []
	if(os.path.isfile(databasepath)):
		print(Fore.BLUE + "-Reading database" + Style.RESET_ALL)
		with open(databasepath, 'r') as f:
			for line in f:
				filehashfunc, space, rest = line.partition(' ')
				filehashvalue, space, filepath = rest.partition(' ')
				filepath = filepath.strip()
				database.append([filehashfunc, filehashvalue, filepath])
	else:
		print(Fore.BLUE + "-No database found, creating a new one" + Style.RESET_ALL)

	print(Fore.BLUE + "-Read filehashes and merge" + Style.RESET_ALL)
	with open(inputpath + "/filehashes.txt", 'r') as f:
		for line in f:
			filehashfunc, space, rest = line.partition(' ')
			filehashvalue, space, filepath = rest.partition(' ')
			filepath = filepath.strip()

			found = False
			for idx, sublist in enumerate(database):
				if sublist[2] == filepath:
					found = True
					database[idx][1] = filehashvalue			# blindly overwrite
					break

			if not found:
				database.append([filehashfunc, filehashvalue, filepath])

	print(Fore.BLUE + "-Write database" + Style.RESET_ALL)
	with open(databasepath, 'w') as f:
		for item in database:
			itemStr = item[0] + " " + item[1] + " " + item[2]
			f.write("%s\n" % itemStr)
		f.close()


if __name__ == '__main__':
	colorama.init()			#init colorama

	print(Style.RESET_ALL + Fore.GREEN + "BackupIt V1.0 BETA" + Style.RESET_ALL)

	parser = argparse.ArgumentParser(description="Backup Control Script")
	parser.add_argument('-i', "--input", help="Folder to Backup FROM", required=True)
	parser.add_argument('-o', "--output", help="Folder to Backup TO", required=False)
	parser.add_argument('-t', "--tools", help="Folder to compiled tools", required=False)
	parser.add_argument('-d', "--database", help="Database-File to Use", required=False)
	parser.add_argument('-c', "--create", help="Create compressed Structure from input", required=False, action="store_true")
	parser.add_argument('-v', "--verify", help="Verify compressed structure", required=False, action="store_true")
	parser.add_argument('-m', "--merge", help="Merge hashfile to database", required=False, action="store_true")
	args = parser.parse_args()

	temporaryPath = tempfile.gettempdir()

	if(not args.input.endswith('/')) and (not args.input.endswith('\\')):
		args.input = args.input + '/'

	if(args.output):
		if(not args.output.endswith('/')) and (not args.output.endswith('\\')):
			args.input = args.input + '/'

	counter = Counter(0)

	count = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(processes=count, initargs=(counter,))
	print((Fore.BLUE + "-Number CPUs found: %d" + Style.RESET_ALL) % (count))

	if(args.merge):
		if args.database is None:
			print(Fore.RED + "no database file specified!"+Style.RESET_ALL)
			exit(1)
		print(Fore.GREEN + "-Merge hashlist to database"+ Style.RESET_ALL)
		mergeFilehashesToDatabase(args.database, normalizePath(args.input))

	if(args.create):
		print(Fore.GREEN + "-Create archive" + Style.RESET_ALL)

		dirs, files = generateFilelist(normalizePath(args.input))
		print((Fore.BLUE + "-Found %d files" + Style.RESET_ALL) % (len(files)))

		filesizesUncompressed = getFilesizes(files)
		print((Fore.BLUE + "-All filesizes uncompressed: %dMB(%dbytes)" + Style.RESET_ALL) % (filesizesUncompressed/(1024*1024), filesizesUncompressed))

		print(Fore.BLUE + "-Generate hashing commands" + Style.RESET_ALL)
		cmds = generateCommandListHashing(args.tools, files)
		
		print(Fore.BLUE + "-Generating the hashes of the files" + Style.RESET_ALL)
		hashresults = []
		for res in tqdm.tqdm(pool.imap_unordered(runProcess, cmds), total=len(cmds)):
			hashresults.append(res)

		errorfiles = []
		hashestowrite = []
		for result in hashresults:
			if(result.returncode != 0):
				print(Fore.RED + "HASHERROR: %s(%d)" + Style.RESET_ALL % (result.stdout, result.returncode))
				errorfiles.append(result.stdout)
			else:
				if sys.platform == 'win32':
					hashestowrite.append(result.stdout.decode('cp1252'))
				else:
					hashestowrite.append(result.stdout.decode('UTF-8'))

		database = []
		if args.database is not None:
			if os.path.isfile(args.database):
				print(Fore.BLUE + "-Reading database" + Style.RESET_ALL)
				with open(args.database, 'r') as f:
					for line in f:
						filehashfunc, space, rest = line.partition(' ')
						filehashvalue, space, filepath = rest.partition(' ')
						filepath = filepath.strip()
						database.append([filehashfunc, filehashvalue, filepath])

				print((Fore.BLUE + "-%d entries imported from old database" + Style.RESET_ALL) % len(database))

				print(Fore.BLUE + "-Search for updates of files (incremental update mode)" + Style.RESET_ALL)

				filelistToProcess = []
				newfilelist = []
				for item in hashestowrite:

					filehashfunc, space, rest = item.partition(' ')
					filehashvalue, space, filepath = rest.partition(' ')
					filepath = filepath.strip()

					found = False
					for idx, sublist in enumerate(database):
						if sublist[2] == filepath:
							found = True
							if(database[idx][1] != filehashvalue):
								filelistToProcess.append(item)
								newfilelist.append(filepath)
								database[idx][1] = filehashvalue			# update database to have new hash
								print(Fore.GREEN + "IncrementalMode: filehash changed, process file %s" % filepath)
							#else:
							#	print(Fore.GREEN + "IncrementalMode: unchanged, skip file %s" % filepath)
							break

					if not found:
						print(Fore.GREEN + "IncrementalMode: new file %s" % filepath)
						database.append([filehashfunc, filehashvalue, filepath])
						filelistToProcess.append(item)
						newfilelist.append(filepath)

				hashestowrite = filelistToProcess
				files = newfilelist

				if len(hashestowrite) == 0:
					print(Fore.GREEN + "-IncrementalMode: found nothing to do, all files unchanged. exiting")
					exit(0)

			else:
				print(Fore.BLUE + "-No database found, creating a new one" + Style.RESET_ALL)
				for item in hashestowrite:
					filehashfunc, space, rest = item.partition(' ')
					filehashvalue, space, filepath = rest.partition(' ')
					filepath = filepath.strip()

					database.append([filehashfunc, filehashvalue, filepath])
		else:
			print(Fore.BLUE + "-No database file specified, will not create a new one" + Style.RESET_ALL)

		print(Fore.BLUE + "-Write hashes to file in output path" + Style.RESET_ALL)
		with open(args.output + "/filehashes.txt", 'w') as f:
			for itemStr in hashestowrite:
				itemStr = itemStr.replace(normalizePath(args.input), "")
				f.write("%s\n" % itemStr)
			f.close()

		print((Fore.BLUE + "-Create folder structure in ouput path %s" + Style.RESET_ALL) % args.output)
		normalizedInput = normalizePath(args.input)
		normalizedOutput = normalizePath(args.output)
		for dir in dirs:
			dir = dir.replace(normalizedInput, "")
			path = os.path.join(normalizedOutput, dir)
			os.makedirs(path, exist_ok=True)

		compressArgs = [args.tools, args.output, normalizePath(args.input), temporaryPath]
		newIterable = ([x, compressArgs] for x in files)

		print(Fore.BLUE + "-Compress all files" + Style.RESET_ALL)
		compressresults = []
		for res in tqdm.tqdm(pool.imap_unordered(compressFiles, newIterable), total=len(files)):
			compressresults.append(res)

		for result in compressresults:
			if(result.returncode != 0):
				print((Fore.RED + "COMPRESSERROR: %s(%d)" + Style.RESET_ALL) % (result.stdout, result.returncode))

		if args.database is not None:
			print(Fore.BLUE + "-Write database" + Style.RESET_ALL)
			with open(args.database, 'w') as f:
				for item in database:
					itemStr = item[0] + " " + item[1] + " " + item[2]
					f.write("%s\n" % itemStr)
				f.close()
		else:
			print(Fore.BLUE + "-No database path specified, will not write db" + Style.RESET_ALL)

		print(Fore.GREEN + "-Finished!" + Style.RESET_ALL)

	if(args.verify):
		print(Fore.GREEN + "-Verify archive" + Style.RESET_ALL)
		dirs, files = generateFilelist(args.input)

		filehashpath = normalizePath(os.path.join(args.input, "filehashes.txt"))
		files.remove(filehashpath)

		print((Fore.BLUE + "-Found %d files" + Style.RESET_ALL) % len(files))

		print(Fore.BLUE + "-Create folder structure in temporary path" + Style.RESET_ALL)
		for dir in dirs:
			dir = dir.replace(normalizePath(args.input), "")
			path = os.path.join("/tmp/", dir)
			os.makedirs(path, exist_ok=True)

		verifyargs = [normalizePath(args.input), args.tools]
		newIterable = ([x, verifyargs] for x in files)

		rawVerifyResults = []
		for res in tqdm.tqdm(pool.imap_unordered(uncompressAndGenerateHash, newIterable), total=len(files)):
			rawVerifyResults.append(res)

		verifyResults = []
		for item in rawVerifyResults:
			verifyResults.append(item.replace("/tmp/", ""))

		# here in verifyResults the path is still wrong because it's lead by "/tmp/" which need to be removed...

		print(Fore.BLUE + "-Comparing all hashes to found files" + Style.RESET_ALL)
		# create set of all file hashes
		originalHashes = {}
		allOK = True
		notFoundFiles = []
		with open(args.input + "/filehashes.txt", 'r') as f:
			for line in f:
				filehashfunc, space, rest = line.partition(' ')
				filehashvalue, space, filepath = rest.partition(' ')

				# search for file and hash in verify-set

				filepath = filepath.strip()

				origFile = [x for x in verifyResults if x.endswith(" "+filepath)]			# force comparison of complete path

				if(len(origFile) == 1):
					origFile = str(origFile)
					if filehashvalue not in origFile:
						print((Fore.RED + "%s: HASH HAS CHANGED!(%s,%s)" + Style.RESET_ALL) % (filepath, origFile, filehashvalue))
						allOK = False
				else:
					if(len(origFile) == 0):
						notFoundFiles.append(filepath)
					else:
						print((Fore.RED + "More than one entry in database found for file %s, dunno what to do?" + Style.RESET_ALL) % filepath)
					allOK = False

		# TODO: how to find files which are present on disc, but not in the filehashes-file?
		# files in filehashes but not found on disk are handled

		if(allOK == False):
			print(Fore.RED + "\n\n")
			print(" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("! There were errors during verification !")
			print(" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			print("The following files are present in the filehashes-file, but are not found on disk:")
			print(*notFoundFiles, sep="\n")
			print(Style.RESET_ALL)
		else:
			print(Fore.GREEN + "Verification: all hashes in the file found on disc and are equal" + Style.RESET_ALL)
	
	colorama.deinit()
