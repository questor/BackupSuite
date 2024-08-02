
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <functional>

#include "argtable3/argtable3.h"

#include "subprocess.h"
#include "tinydir.h"
#include "tinydirhelper.h"
#include "tinyhuman.h"
#include "tinytty.h"

#include "quickpool.h"
#include "concurrentqueue/concurrentqueue.h"

// utils ===========================================================================================

std::string replaceAll(std::string &input, std::string searchFor, std::string replaceBy) {
	std::string str = input;
	size_t index = 0;
	while (true) {
	     /* Locate the substring to replace. */
	     index = str.find(searchFor, index);
	     if (index == std::string::npos)
	     	break;

	     /* Make the replacement. */
	     str.replace(index, searchFor.length(), replaceBy);

	     /* Advance index forward so the next iteration doesn't pick it up as well. */
	     index += replaceBy.length();
	}
	return str;
}

const char* ws = " \t\n\r\f\v";

// trim from end of string (right)
inline std::string& rtrim(std::string& s, const char* t = ws) {
    s.erase(s.find_last_not_of(t) + 1);
    return s;
}

// trim from beginning of string (left)
inline std::string& ltrim(std::string& s, const char* t = ws) {
    s.erase(0, s.find_first_not_of(t));
    return s;
}

// trim from both ends of string (right then left)
inline std::string& trim(std::string& s, const char* t = ws) {
    return ltrim(rtrim(s, t), t);
}

std::string normalizeFilePath(std::string &input) {
	std::string retStr;
	//make sure '\' is converted to '/'
	retStr = replaceAll(input, "\\", "/");
	retStr = trim(retStr);

	return retStr;
}
std::string normalizeFilePath(const char *input) {
	std::string inputStr(input);
	return normalizeFilePath(inputStr);
}

std::string normalizeDirPath(std::string &input) {
	std::string retStr = normalizeFilePath(input);
	//make sure directories end with a "/"
	if(retStr.back() != '/')
		retStr = retStr + '/';
	return retStr;
}
std::string normalizeDirPath(const char *input) {
	std::string inputStr(input);
	return normalizeDirPath(inputStr);
}

const char *skipWhitespace(const char *ptr) {
	while((*ptr==' ') || (*ptr=='\t') || (*ptr==13) || (*ptr==10)) {
		++ptr;
	}
	return ptr;
}
const char *skipNonWhitespace(const char *ptr) {
	while((*ptr!=' ') && (*ptr!='\t') && (*ptr!=13) && (*ptr!=10) && (*ptr!=0)) {
		++ptr;
	}
	return ptr;
}
const char *skipNewline(const char *ptr) {
	while((*ptr==13) || (*ptr==10)) {
		++ptr;
	}
	return ptr;
}
const char *skipNonNewline(const char *ptr) {
	while((*ptr!=13) && (*ptr!=10) && (*ptr!=0)) {
		++ptr;
	}
	return ptr;
}

// FileHashes ===========================================================================================
class FileHashes {
public:
	bool readFileHashes(const std::string &filePath) {
		mFileEntries.clear();
		mFileEntries.reserve(10000);	//to start with some higher value...

		FILE *fp = fopen(filePath.c_str(), "r");
		if(fp == 0) {
			return false;
		}
		fseek(fp, 0, SEEK_END);
		int fileSize = ftell(fp);
		fseek(fp, 0, SEEK_SET);
		char *fileBuffer = new char[fileSize+10];
		int alreadyReadBytes = 0;
		while(alreadyReadBytes < fileSize) {
			alreadyReadBytes += fread(fileBuffer+alreadyReadBytes, 1, fileSize-alreadyReadBytes, fp);
		}
		fclose(fp);

		parseBuffer(fileBuffer, fileSize);

		delete[] fileBuffer;
		return true;
	}
	bool saveFileHashes(const std::string &filePath) {
		FILE *fp = fopen(filePath.c_str(), "w");
		if(fp == 0) {
			return false;
		}
		for(int i=0; i<mFileEntries.size(); ++i) {
			FileEntry &entry = mFileEntries[i];
			fprintf(fp, "%s %s %s\n", entry.mHashFunc.c_str(), entry.mHashValue.c_str(), entry.mPath.c_str());
		}
		fclose(fp);
		return true;
	}

	int getNumberEntries() {
		return mFileEntries.size();
	}

	void parseBuffer(const char *buffer, int numberBytes) {
		const char* readCursor = buffer;
		while(readCursor < buffer+numberBytes) {
			const char *startToken = readCursor;
			readCursor = skipNonWhitespace(readCursor);
			std::string hashFunc(startToken, readCursor-startToken);

			startToken = skipWhitespace(readCursor);
			readCursor = skipNonWhitespace(startToken);
			std::string hashValue(startToken, readCursor-startToken);

			startToken = skipWhitespace(readCursor);
			readCursor = skipNonWhitespace(startToken);
			std::string filePath(startToken, readCursor-startToken);

			FileEntry entry;
			entry.mHashFunc = hashFunc;
			entry.mHashValue = hashValue;
			entry.mPath = filePath;
			mFileEntries.push_back(entry);

			if(readCursor < buffer+numberBytes)
				readCursor = skipNewline(readCursor);
		}
	}

	enum class CompareResult : uint8_t {
		eSame, eChanged, eNew
	};

	std::vector<CompareResult> compareToFileHashes(FileHashes &otherFiles) {
		std::vector<CompareResult> results;
		results.reserve(mFileEntries.size());

		for(auto &entry : mFileEntries) {
			int otherFileIndex = otherFiles.findIndexToFile(entry.mPath);
			if(otherFileIndex == -1) {
				results.push_back(CompareResult::eNew);
			} else {
				if(entry.mHashValue == otherFiles.mFileEntries[otherFileIndex].mHashValue) {
					results.push_back(CompareResult::eSame);
				} else {
					results.push_back(CompareResult::eChanged);
				}
			}
		}
		return results;
	}

	struct FileEntry {
		std::string mHashFunc;
		std::string mHashValue;
		std::string mPath;
	};

	FileEntry &getEntry(int index) {
		return mFileEntries[index];
	}

private:
	int findIndexToFile(std::string &path) {
		int curIndex = 0;
		while(curIndex < mFileEntries.size()) {
			if(path.compare(mFileEntries[curIndex].mPath) == 0) {
				return curIndex;
			}
			curIndex += 1;
		}
		return -1;
	}

	std::vector<FileEntry> mFileEntries;
};

struct Configuration {
	std::string inputFolder;
	std::string outputFolder;
	std::string toolsFolder;
	std::string databaseFilename;
	std::string unittestPath;
	FileHashes database;
} gConfiguration;


// main ============================================================================================

int main(int argc, char **argv) {
	arg_lit *helpFlag = arg_lit0("h", "help", "prints this help");
	arg_file *inputDir = arg_file1("i", "input", "<dir>", "Folder to Backup FROM");
	arg_file *outputDir = arg_file1("o", "output", "<dir>", "Folder to Backup TO");
	arg_file *tools = arg_file0("t", "tools", "<dir>", "Folder to compiled tools");
	arg_file *databaseFilename = arg_file0("d", "database", "<file>", "Database-File to use");
	arg_lit *createFlag = arg_lit0("c", "create", "create initial backup");
	arg_lit *verifyFlag = arg_lit0("v", "verify", "verify compressed structure");
	arg_lit *mergeFlag = arg_lit0("m", "merge", "merge hashfile to FileHashes");
	arg_file *unittestpath = arg_file0("u", "unittestpath", "<dir>", "directory which is NOT stored as part of the backup(used in unittests");
	struct arg_end *end = arg_end(20);	//store up to 20 errors

	void *argtable[] = {helpFlag, inputDir, outputDir, tools, databaseFilename,
					createFlag, verifyFlag, mergeFlag, unittestpath, end};

	int exitCode = 0;
	char toolName[] = "ctrlcenter2";

	int numberArgErrors = arg_parse(argc, argv, argtable);
	if(helpFlag->count > 0) {
		printf("Usage: %s", toolName);
		arg_print_syntax(stdout, argtable, "\n");
		printf("\n\n");
		arg_print_glossary(stdout, argtable, "  %-25s %s\n");
		goto exitTool;
	}
	if(numberArgErrors > 0) {
		arg_print_errors(stdout, end, toolName);
		printf("try %s --help for more information\n", toolName);
		exitCode = 1;
		goto exitTool;
	}

	gConfiguration.inputFolder = normalizeDirPath(inputDir->filename[0]);
	gConfiguration.outputFolder = normalizeDirPath(outputDir->filename[0]);
	if(tools->count == 0) {
		gConfiguration.toolsFolder = "bin_lnx64_release";
	} else {
		gConfiguration.toolsFolder = normalizeDirPath(tools->filename[0]);
	}
	if(databaseFilename->count == 0) {
		gConfiguration.databaseFilename = "database.txt";
	} else {
		gConfiguration.databaseFilename = normalizeFilePath(databaseFilename->filename[0]);
	}

	if(unittestpath->count == 0) {
		gConfiguration.unittestPath = "";
	} else {
		gConfiguration.unittestPath = normalizeDirPath(unittestpath->filename[0]);
	}

	//dump configuration
	printf(" BackupSuite - CtrlCenter2\n");
	printf("-=========================-\n");
	printf("inputFolder: %s\n", gConfiguration.inputFolder.c_str());
	printf("outputFolder: %s\n", gConfiguration.outputFolder.c_str());
	printf("toolsFolder: %s\n", gConfiguration.toolsFolder.c_str());
	printf("databasefilename: %s\n", gConfiguration.databaseFilename.c_str());
	printf("unittestpath: %s\n", gConfiguration.unittestPath.c_str());

	if(verifyFlag->count != 0) {
		printf("\n*mode: verify archive(compare filelist to uncompressed files in archive)\n");

		goto exitTool;
	}

	//try to load FileHashes
	if(gConfiguration.database.readFileHashes(gConfiguration.databaseFilename) == true) {
		printf("- read database %s successfully, %d entries\n", gConfiguration.databaseFilename.c_str(), gConfiguration.database.getNumberEntries());
	} else {
		printf("- database %s not found, start with blank one\n", gConfiguration.databaseFilename.c_str());
	}

	if(createFlag->count != 0) {
		printf("\n*mode: create new archive\n");

		// generate list of files to process
		std::vector<std::string> filesToProcess;

		std::vector<std::string> recursiveFolders;

	    std::function<void(const char *,bool)> callback = [&]( const char *name, bool is_dir ) {
//	        printf( "%5s %s\n", is_dir ? "<dir>" : "", name );
	        if( is_dir ) {
	        	recursiveFolders.push_back(std::string(name));
	        } else {
	        	filesToProcess.emplace_back(name);
	        }
	    };
    	tinydir( "./", callback );
    	while(recursiveFolders.size() != 0) {
    		std::string dir = recursiveFolders.back() + "/";
    		recursiveFolders.pop_back();
    		tinydir(dir.c_str(), callback);
    	}

    	std::vector<std::future<std::string>> results(filesToProcess.size());

    	for(int i=0; i<filesToProcess.size(); ++i) {
    		results[i] = quickpool::async([&filesToProcess](int i) {
    			std::string &fileToProcess = filesToProcess[i];

    			std::string executable = gConfiguration.toolsFolder + "meowhash";

    			const char *cmdLine[] = {executable.c_str(), fileToProcess.c_str(), "--nologo", nullptr};
    			subprocess_s subprocess;
    			int result = subprocess_create(cmdLine, subprocess_option_no_window|subprocess_option_inherit_environment, &subprocess);
    			if(result != 0) {
    				printf("ERROR(1) during hashing of file %s\n", fileToProcess.c_str());
    				exit(-1);
    			}
    			int subprocessReturn;
    			result = subprocess_join(&subprocess, &subprocessReturn);
    			if(result != 0) {
    				printf("ERROR(2) during hashing of file %s\n", fileToProcess.c_str());
    				exit(-1);
    			}
    			if(subprocessReturn != 0) {
    				printf("ERROR(3) during hashing of file %s\n", fileToProcess.c_str());
    				exit(-1);
    			}

    			FILE *fp = subprocess_stdout(&subprocess);
    			char tmp[128];
    			if(fp != 0) {
	    			fgets(tmp, 128, fp);
    			}
    			subprocess_destroy(&subprocess);

    			return std::string(tmp);
    		}, i);
    	}
    	quickpool::wait();

    	FileHashes filesHashes;
    	for(int i=0; i<results.size(); ++i) {
    		std::string res = results[i].get();
    		filesHashes.parseBuffer(res.c_str(), res.size());
    	}

		// search for updates of files in FileHashes (hash changed, new file, deleted files?)
    	std::vector<FileHashes::CompareResult> compare = filesHashes.compareToFileHashes(gConfiguration.database);

		// write hashes to filelist in output path

		// create folder structure in output path
		for(int i=0; i<filesHashes.getNumberEntries(); ++i) {
			if(compare[i] != FileHashes::CompareResult::eSame) {		//changed or new?
				smartCreate(filesHashes.getEntry(i).mPath);
			}
		}

		// compress all files

		// write FileHashes


	} else if(mergeFlag->count != 0) {
		printf("\n*mode: merge old filelist to FileHashes\n");

	}

exitTool:
	arg_freetable(argtable, sizeof(argtable)/sizeof(argtable[0]));
	return exitCode;
}

