/*
            Copyright Oliver Kowalke 2009.
            Copyright Thomas Sailer 2013.
   Distributed under the Boost Software License, Version 1.0.
      (See accompanying file LICENSE_1_0.txt or copy at
            http://www.boost.org/LICENSE_1_0.txt)
*/

/*************************************************************************************
* ---------------------------------------------------------------------------------- *
* |     0   |     1   |     2    |     3   |     4   |     5   |     6   |     7   | *
* ---------------------------------------------------------------------------------- *
* |    0x0  |    0x4  |    0x8   |    0xc  |   0x10  |   0x14  |   0x18  |   0x1c  | *
* ---------------------------------------------------------------------------------- *
* |                          SEE registers (XMM6-XMM15)                            | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |     8   |    9    |    10    |    11   |    12   |    13   |    14   |    15   | *
* ---------------------------------------------------------------------------------- *
* |   0x20  |  0x24   |   0x28   |   0x2c  |   0x30  |   0x34  |   0x38  |   0x3c  | *
* ---------------------------------------------------------------------------------- *
* |                          SEE registers (XMM6-XMM15)                            | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    16   |    17   |    18   |    19    |    20   |    21   |    22   |    23   | *
* ---------------------------------------------------------------------------------- *
* |   0xe40  |   0x44 |   0x48  |   0x4c   |   0x50  |   0x54  |   0x58  |   0x5c  | *
* ---------------------------------------------------------------------------------- *
* |                          SEE registers (XMM6-XMM15)                            | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    24   |   25    |    26    |   27    |    28   |    29   |    30   |    31   | *
* ---------------------------------------------------------------------------------- *
* |   0x60  |   0x64  |   0x68   |   0x6c  |   0x70  |   0x74  |   0x78  |   0x7c  | *
* ---------------------------------------------------------------------------------- *
* |                          SEE registers (XMM6-XMM15)                            | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    32   |   32    |    33    |   34    |    35   |    36   |    37   |    38   | *
* ---------------------------------------------------------------------------------- *
* |   0x80  |   0x84  |   0x88   |   0x8c  |   0x90  |   0x94  |   0x98  |   0x9c  | *
* ---------------------------------------------------------------------------------- *
* |                          SEE registers (XMM6-XMM15)                            | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    39   |   40    |    41    |   42    |    43   |    44   |    45   |    46   | *
* ---------------------------------------------------------------------------------- *
* |   0xa0  |   0xa4  |   0xa8   |   0xac  |   0xb0  |   0xb4  |   0xb8  |   0xbc  | *
* ---------------------------------------------------------------------------------- *
* | fc_mxcsr|fc_x87_cw|     <alignment>    |       fbr_strg    |      fc_dealloc   | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    47   |   48    |    49    |   50    |    51   |    52   |    53   |    54   | *
* ---------------------------------------------------------------------------------- *
* |   0xc0  |   0xc4  |   0xc8   |   0xcc  |   0xd0  |   0xd4  |   0xd8  |   0xdc  | *
* ---------------------------------------------------------------------------------- *
* |        limit      |         base       |         R12       |         R13       | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    55   |   56    |    57    |   58    |    59   |    60   |    61   |    62   | *
* ---------------------------------------------------------------------------------- *
* |   0xe0  |   0xe4  |   0xe8   |   0xec  |   0xf0  |   0xf4  |   0xf8  |   0xfc  | *
* ---------------------------------------------------------------------------------- *
* |        R14        |         R15        |         RDI       |        RSI        | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    63   |   64    |    65    |   66    |    67   |    68   |    69   |    70   | *
* ---------------------------------------------------------------------------------- *
* |  0x100  |  0x104  |  0x108   |  0x10c  |  0x110  |  0x114  |  0x118  |  0x11c  | *
* ---------------------------------------------------------------------------------- *
* |        RBX        |         RBP        |       hidden      |        RIP        | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    71   |   72    |    73    |   74    |    75   |    76   |    77   |    78   | *
* ---------------------------------------------------------------------------------- *
* |  0x120  |  0x124  |  0x128   |  0x12c  |  0x130  |  0x134  |  0x138  |  0x13c  | *
* ---------------------------------------------------------------------------------- *
* |                                   parameter area                               | *
* ---------------------------------------------------------------------------------- *
* ---------------------------------------------------------------------------------- *
* |    79   |   80    |    81    |   82    |    83   |    84   |    85   |    86   | *
* ---------------------------------------------------------------------------------- *
* |  0x140  |  0x144  |  0x148   |  0x14c  |  0x150  |  0x154  |  0x158  |  0x15c  | *
* ---------------------------------------------------------------------------------- *
* |       FCTX        |        DATA        |                                       | *
* ---------------------------------------------------------------------------------- *
**************************************************************************************/

.file	"make_x86_64_ms_pe_gas.asm"
.text
.p2align 4,,15
.globl	jq_make_fcontext
.def	jq_make_fcontext;	.scl	2;	.type	32;	.endef
.seh_proc	jq_make_fcontext
jq_make_fcontext:
.seh_endprologue

    /* first arg of jq_make_fcontext() == top of context-stack */
    movq  %rcx, %rax

    /* shift address in RAX to lower 16 byte boundary */
    /* == pointer to fcontext_t and address of context stack */
    andq  $-16, %rax

    /* reserve space for context-data on context-stack */
    /* on context-function entry: (RSP -0x8) % 16 == 0 */
    leaq  -0x150(%rax), %rax

    /* third arg of jq_make_fcontext() == address of context-function */
    movq  %r8, 0x100(%rax)

    /* first arg of jq_make_fcontext() == top of context-stack */
    /* save top address of context stack as 'base' */
    movq  %rcx, 0xc8(%rax)
    /* second arg of jq_make_fcontext() == size of context-stack */
    /* negate stack size for LEA instruction (== substraction) */
    negq  %rdx
    /* compute bottom address of context stack (limit) */
    leaq  (%rcx,%rdx), %rcx
    /* save bottom address of context stack as 'limit' */
    movq  %rcx, 0xc0(%rax)
    /* save address of context stack limit as 'dealloction stack' */
    movq  %rcx, 0xb8(%rax)
	/* set fiber-storage to zero */
    xorq  %rcx, %rcx
    movq  %rcx, 0xb0(%rax)

    /* compute address of transport_t */
    leaq  0x140(%rax), %rcx
    /* store address of transport_t in hidden field */
    movq %rcx, 0x110(%rax)

    /* compute abs address of label trampoline */
    leaq  trampoline(%rip), %rcx
    /* save address of finish as return-address for context-function */
    /* will be entered after jq_jump_fcontext() first time */
    movq  %rcx, 0x118(%rax)

    /* compute abs address of label finish */
    leaq  finish(%rip), %rcx
    /* save address of finish as return-address for context-function */
    /* will be entered after context-function returns */
    movq  %rcx, 0x108(%rax)

    ret /* return pointer to context-data */

trampoline:
    /* store return address on stack */
    /* fix stack alignment */ 
    pushq %rbp
    /* jump to context-function */
    jmp *%rbx

finish:
    /* 32byte shadow-space for _exit() */
    andq  $-32, %rsp
    /* 32byte shadow-space for _exit() are */
    /* already reserved by jq_make_fcontext() */
    /* exit code is zero */
    xorq  %rcx, %rcx
    /* exit application */
    call  _exit
    hlt
.seh_endproc

.def	_exit;	.scl	2;	.type	32;	.endef  /* standard C library function */

.section .drectve
.ascii " -export:\"jq_make_fcontext\""