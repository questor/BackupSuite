/* ========================================================================

   meow_example.cpp - basic usage example of the Meow hash
   (C) Copyright 2018-2019 by Molly Rocket, Inc. (https://mollyrocket.com)
   
   See https://mollyrocket.com/meowhash for details.
   
   ======================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <memory.h>

//
// NOTE(casey): Step 1 - include the meow_hash header for your platform
//

#include "meow_hash_x64_aesni.h"


//
// NOTE(casey): entire_file / ReadEntireFile / FreeEntireFile are simple helpers
// for loading a file into memory.  They are defined at the end of this file.
//
typedef struct entire_file
{
    size_t Size;
    void *Contents;
} entire_file;
static entire_file ReadEntireFile(char *Filename);
static void FreeEntireFile(entire_file *File);

static void
PrintHash(meow_u128 Hash)
{
    printf("%08X-%08X-%08X-%08X",
           MeowU32From(Hash, 3),
           MeowU32From(Hash, 2),
           MeowU32From(Hash, 1),
           MeowU32From(Hash, 0));
}

static void
HashOneFile(char *FilenameA)
{
    // NOTE(casey): Load the file
    entire_file A = ReadEntireFile(FilenameA);
    if(A.Contents)
    {
        // NOTE(casey): Ask Meow for the hash
        meow_u128 HashA = MeowHash(MeowDefaultSeed, A.Size, A.Contents);
        
        // NOTE(casey): Print the hash
        printf("MeowHash ");
        PrintHash(HashA);
        printf(" %s", FilenameA);
    }
    
    FreeEntireFile(&A);
}


//
// NOTE(casey): That's it!  Everything else below here is just boilerplate for starting up
// and loading files with the C runtime library.
//

int
main(int ArgCount, char **Args)
{
    // NOTE(casey): Print the banner
    if(ArgCount <= 2) {
        printf("meowhash %s\n", MEOW_HASH_VERSION_NAME);
        printf("(C) Copyright 2018-2019 by Molly Rocket, Inc. (https://mollyrocket.com)\n");
        printf("See https://mollyrocket.com/meowhash for details.\n");
        printf("\n");        
    }
    
    if(ArgCount == 2 || ArgCount == 3)
        HashOneFile(Args[1]);
    else {
        printf("dunno what to do, this is a special (modified) meowhash app, so default params doesn't work!\n");
    }
    return(0);
}

static entire_file
ReadEntireFile(char *Filename)
{
    entire_file Result = {0};
    
    FILE *File = fopen(Filename, "rb");
    if(File)
    {
        fseek(File, 0, SEEK_END);
        Result.Size = ftell(File);
        fseek(File, 0, SEEK_SET);
        
        Result.Contents = malloc(Result.Size);
        if(Result.Contents)
        {
            if(Result.Size)
            {
                fread(Result.Contents, Result.Size, 1, File);
            }
        }
        else
        {
            Result.Contents = 0;
            Result.Size = 0;
        }
        
        fclose(File);
    }
    else
    {
        printf("ERROR: Unable to load \"%s\"\n", Filename);
    }
    
    
    return(Result);
}

static void
FreeEntireFile(entire_file *File)
{
    if(File->Contents)
    {
        free(File->Contents);
        File->Contents = 0;
    }
    
    File->Size = 0;
}

