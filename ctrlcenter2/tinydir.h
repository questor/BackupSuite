// tiny directory listing
// - rlyeh, public domain | wtrmrkrlyeh
#pragma once
#include <string>

#ifdef _WIN32
#include <winsock2.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#ifndef S_ISDIR
    #define S_ISDIR(m) (((m) & S_IFMT) == S_IFDIR)
#endif

#endif

template<typename FN>
bool tinydir( const char *directory, const FN &yield ) {
    std::string src( directory );
    while( !src.empty() && (src.back() == '/' || src.back() == '\\') ) src.pop_back();
#ifdef _WIN32
    WIN32_FIND_DATA fdata;
    for( HANDLE h = FindFirstFileA( (src + "/*").c_str(), &fdata ); h != INVALID_HANDLE_VALUE; ) {
        for( bool next = true; next; next = FindNextFileA( h, &fdata ) != 0 ) {
            if( fdata.cFileName[0] != '.' ) {
                size_t fileSize = (size_t)fdata.nFileSizeLow;
                if(sizeof(size_t) >= sizeof(uint64_t))
                    fileSize |= (size_t)((uint64_t)fdata.nFileSizeHigh << (uint64_t)32);
                yield( (src + "/" + fdata.cFileName).c_str(), (fdata.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) > 0,  fileSize);
            }
        }
        return FindClose( h ), true;
    }
#else
    for( DIR *dir = opendir( (src + "/").c_str() ); dir; ) {

        int dfd = dirfd(dir);

        for( struct dirent *ep; (ep = readdir( dir )); ) {
            if(strcmp(".", ep->d_name) == 0)
                continue;
            if(strcmp("..", ep->d_name) == 0)
                continue;

            struct stat st;
            if(fstatat(dfd, ep->d_name, &st, 0) == -1) {
                printf("failed to stat %s, errno: %d\n", ep->d_name, errno);
                continue;
            }
            bool isDir = false;
            if((S_ISDIR(st.st_mode) != 0)) {
                isDir = true;
            }
//            printf("process %s (%s)\n", (src+"/"+ep->d_name).c_str(), isDir?"true":"false");
            yield( (src + "/" + ep->d_name).c_str(), isDir, st.st_size );
        }
        return closedir( dir ), true;
    }
#endif
    return false;
}

/*
#include <stdio.h>
#include <functional>
int main() {
    std::function<void(const char *,bool)> callback = [&]( const char *name, bool is_dir ) {
        printf( "%5s %s\n", is_dir ? "<dir>" : "", name );
        //if( is_dir ) tinydir( name, callback ); // <-- uncomment for recursive listing
    };
    return tinydir( "./", callback );
}
*/
