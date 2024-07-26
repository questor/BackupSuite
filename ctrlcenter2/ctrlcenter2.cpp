
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>

#include "argtable3/argtable3.h"

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

std::string normalizePath(std::string &input) {
	std::string retStr;
	//make sure '\' is converted to '/'
	retStr = replaceAll(input, "\\", "/");

	return retStr;
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
	}

private:
	struct FileEntry {
		std::string mHashFunc;
		std::string mHashValue;
		std::string mPath;
	};
	std::vector<FileEntry> mFileEntries;
};

// main ============================================================================================

int main(int argc, char **argv) {

	arg_lit *helpFlag = arg_lit0("h", "help", "prints this help");
	arg_filen *input = arg_filen("i", "input", "Folder to Backup FROM");
	arg_filen *output = arg_filen("o", "output", "Folder to Backup TO");
	arg_filen *tools = arg_filen("t", "tools", "Folder to compiled tools");
	arg_filen *databasefile = arg_filen("d", "database", "Database-File to use");
	arg_lit *createFlag = arg_lit0("c", "create", "create initial backup");
	arg_lit *verifyFlag = arg_lit0("v", "verify", "verify compressed structure");
	arg_lit *mergeFlag = arg_lit0("m", "merge", "merge hashfile to database");
	arg_filen *unittestpath = arg_filen("u", "unittestpath", "directory which is NOT stored as part of the backup(used in unittests");
	arg_end *end = arg_end(20);	//store up to 20 errors

	void *argtable[] = {helpFlag, input, output, tools, databasefile,
					createFlag, verifyFlag, mergeFlag, unittestpath, end};


	int exitCode = 0;
	char toolName[] = "ctrlcenter2";

	int numberArgErrors = arg_parse(argc, argv, argtable);
	if(help->count > 0) {
		printf("Usage: %s", toolName);
		arg_print_syntax(stdout, argtable, "\n");
		printf("\n\n");
		arg_print_glossary(stdout, argtable, "  %-25s %s\n");
		goto exitTool;
	}
	if(numberArgErrors > 0) {
		arg_print_errors(stdout, end, toolName);
		print("try %s --help for more information\n", toolName);
		exitCode = 1;
		goto exitTool;
	}



exitTool:
	arg_freetable(argtable, sizeof(argtable)/sizeof(argtable[0]));
	return exitCode;
}

