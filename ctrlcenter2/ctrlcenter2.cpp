
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <functional>

#include "argtable3/argtable3.h"

#include "subprocess.h"
#include "tinydir.h"
#include "tinyhuman.h"
#include "tinytty.h"

#include "jq/jq.h"
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

std::string normalizeFilePath(std::string &input) {
	std::string retStr;
	//make sure '\' is converted to '/'
	retStr = replaceAll(input, "\\", "/");
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

char *skipWhitespace(char *ptr) {
	while((*ptr==' ') || (*ptr=='\t')) {
		++ptr;
	}
	return ptr;
}
char *skipNonWhitespace(char *ptr) {
	while((*ptr!=' ') && (*ptr!='\t')) {
		++ptr;
	}
	return ptr;
}
char *skipNewline(char *ptr) {
	while((*ptr==13) || (*ptr==10)) {
		++ptr;
	}
	return ptr;
}
char *skipNonNewline(char *ptr) {
	while((*ptr!=13) && (*ptr!=10)) {
		++ptr;
	}
	return ptr;
}

// database ===========================================================================================
class Database {
public:
	bool readDatabase(const std::string &filePath) {
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

		char* readCursor = fileBuffer;
		while(readCursor < fileBuffer+fileSize) {
			char *startToken = readCursor;
			readCursor = skipNonWhitespace(readCursor);
			std::string hashFunc(startToken, readCursor-1-startToken);

			startToken = skipWhitespace(readCursor);
			readCursor = skipNonWhitespace(readCursor);
			std::string hashValue(startToken, readCursor-1-startToken);

			startToken = readCursor;
			readCursor = skipNonNewline(readCursor);
			std::string filePath(startToken, readCursor-1-startToken);

			readCursor = skipNewline(readCursor);

			FileEntry entry;
			entry.mHashFunc = hashFunc;
			entry.mHashValue = hashValue;
			entry.mPath = filePath;
			mFileEntries.push_back(entry);
		}

		delete[] fileBuffer;
		return true;
	}
	bool saveDatabase(const std::string &filePath) {
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

private:
	struct FileEntry {
		std::string mHashFunc;
		std::string mHashValue;
		std::string mPath;
	};
	std::vector<FileEntry> mFileEntries;
};

struct Configuration {
	std::string inputFolder;
	std::string outputFolder;
	std::string toolsFolder;
	std::string databaseFileName;
	std::string unittestPath;
	Database database;
} gConfiguration;


// main ============================================================================================

int main(int argc, char **argv) {
	arg_lit *helpFlag = arg_lit0("h", "help", "prints this help");
	arg_file *inputDir = arg_file1("i", "input", "<dir>", "Folder to Backup FROM");
	arg_file *outputDir = arg_file1("o", "output", "<dir>", "Folder to Backup TO");
	arg_file *tools = arg_file0("t", "tools", "<dir>", "Folder to compiled tools");
	arg_file *databasefile = arg_file0("d", "database", "<file>", "Database-File to use");
	arg_lit *createFlag = arg_lit0("c", "create", "create initial backup");
	arg_lit *verifyFlag = arg_lit0("v", "verify", "verify compressed structure");
	arg_lit *mergeFlag = arg_lit0("m", "merge", "merge hashfile to database");
	arg_file *unittestpath = arg_file0("u", "unittestpath", "<dir>", "directory which is NOT stored as part of the backup(used in unittests");
	struct arg_end *end = arg_end(20);	//store up to 20 errors

	void *argtable[] = {helpFlag, inputDir, outputDir, tools, databasefile,
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
	if(databasefile->count == 0) {
		gConfiguration.databaseFileName = "database.txt";
	} else {
		gConfiguration.databaseFileName = normalizeFilePath(databasefile->filename[0]);
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
	printf("databasefilename: %s\n", gConfiguration.databaseFileName.c_str());
	printf("unittestpath: %s\n", gConfiguration.unittestPath.c_str());

	if(verifyFlag->count != 0) {
		printf("\n*mode: verify archive(compare filelist to uncompressed files in archive)\n");

		goto exitTool;
	}

	//try to load database
	if(gConfiguration.database.readDatabase(gConfiguration.databaseFileName) == true) {
		printf("- read database %s successfully, %d entries\n", gConfiguration.databaseFileName.c_str(), gConfiguration.database.getNumberEntries());
	} else {
		printf("- database %s not found, start with blank one\n", gConfiguration.databaseFileName.c_str());
	}

	if(createFlag->count != 0) {
		printf("\n*mode: create new archive\n");

		// generate list of files to process
		std::vector<std::string> filesToProcess;

	    std::function<void(const char *,bool)> callback = [&]( const char *name, bool is_dir ) {
//	        printf( "%5s %s\n", is_dir ? "<dir>" : "", name );
	        if( is_dir ) {
	        	tinydir( name, callback );
	        } else {
	        	filesToProcess.emplace_back(name);
	        }
	    };
    	tinydir( "./", callback );

    	JqAttributes jqAttributes;							//init worker thread system
    	JqInitAttributes(&jqAttributes);
    	JqStart(&jqAttributes);
    	JqSetThreadQueueOrder(&jqAttributes.QueueOrder[0]);


		// hash all files
    	JqHandle hqHandle = JqAdd("Hashing files",
    		[](int begin, int end) {
    			printf("hallo\n");
    		},
    		0,	//queue
    		filesToProcess.size(),
    	);

		// search for updates of files in database (hash changed, new file, deleted files?)

		// write hashes to filelist in output path

		// create folder structure in output path

		// compress all files

		// write database

    	JqStop();

	} else if(mergeFlag->count != 0) {
		printf("\n*mode: merge old filelist to database\n");

	}

exitTool:
	arg_freetable(argtable, sizeof(argtable)/sizeof(argtable[0]));
	return exitCode;
}

