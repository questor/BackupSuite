
#pragma once

// more or less taken from https://github.com/questor/eaio/blob/master/EAFileUtil.cpp

#ifdef _WIN32
    #include <windows.h>
    #include <direct.h>
#else
 	#include <stdio.h>
    #include <errno.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/stat.h>
    #ifndef S_ISDIR
        #define S_ISDIR(m) (((m) & S_IFMT) == S_IFDIR)
    #endif
#endif

bool dirExists(std::string dir) {

#ifdef _WIN32
	const DWORD attr = ::GetFileAttributesA(dir.c_str());
	return ((attr != INVALID_FILE_ATTRIBUTES) && ((attr & FILE_ATTRIBUTE_DIRECTORY) != 0));
#else
	struct stat st;
	const int result = stat(dir.c_str(), &st);
	if(result == 0) {
		return S_ISDIR(st.st_mode) != 0;
	}
	return false;
#endif
}

bool createSingleDir(std::string dir) {
	if(dir.back() == '/')
		dir.pop_back();

#ifdef _WIN32
	BOOL res = CreateDirectoryA(dir.c_str(), NULL);
	return res || (GetLastError() == ERROR_ALREADY_EXISTS);
#else
	const int res = mkdir(dir.c_str(), 0777);
	return ((res == 0) || (errno == EEXIST));
#endif
}

// (1) bla/
// (2) /bla/blub/
// (3) bla/blub/

bool smartCreate(std::string directory) {			//string has to end with "/"!
	int cursor = 0;
	int foundPos;
//	printf("==============\nsmartCreate(%s)\n", directory.c_str());
	while(1) {
		int foundPos = directory.find("/", cursor);
//		printf("pos %d\n", foundPos);
		if(foundPos == std::string::npos) {
			if(cursor == 0) {	//if no separator was found check for single folder in relative syntax (1)
				if(!dirExists(directory)) {
					return createSingleDir(directory);
				}
			}
			break;
		} else if(foundPos == 0) {
			// case (2), skip first occurence
			cursor = foundPos+1;
		} else {
			std::string subDir = directory.substr(0, foundPos);
//			printf("createDir %s\n", subDir.c_str());
			createSingleDir(subDir);
			cursor = foundPos+1;
		}
	}
	return true;
}

static std::string getEnvVar(std::string const &key) {
	char *val = getenv(key.c_str());
	if(val == nullptr) {
		return std::string("");
	} else {
		return std::string(val);
	}
}

std::string getTemporaryFolder() {
#ifdef _WIN32
	WCHAR tempPath[MAX_PATH+1];
	::GetTempPath(MAX_PATH, &tempPath[0]);
	return std::string(tempPath);
#else
	std::string path;
	path = getEnvVar("TMPDIR");	if(path.length() != 0) { return path; }
	path = getEnvVar("TMP");	if(path.length() != 0) { return path; }
	path = getEnvVar("TEMP");	if(path.length() != 0) { return path; }
	path = getEnvVar("TEMPDIR");	if(path.length() != 0) { return path; }

	path = "/tmp";			// or "/data/local/tmp" on android
	return path;
#endif
}