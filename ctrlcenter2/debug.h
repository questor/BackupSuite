
#ifndef __DEBUG_H__
#define __DEBUG_H__

#include <stdio.h>

#ifdef DEBUG
   #if __GNUC__
      #define BREAKPOINT() __builtin_trap()
   #elif _MSC_VER
      #define BREAKPOINT() __debugbreak()
   #else
      #define BREAKPOINT *(volatile int*)0=0
   #endif

   #define ASSERT(x,comment) do { \
                                 if(!(x)) { \
                                    printf("%s:%d(%s): ASSERTION FAILED (%s): %s", __FILE__, __LINE__, __FUNCTION__, #x, comment); \
                                    BREAKPOINT(); \
                              } \
                           } while(0)
#else    //#ifdef _DEBUG
   #define ASSERT(x,comment)
#endif   //#ifdef _DEBUG

#endif   //#ifndef __DEBUG_H__
