#ifndef SIG2USER_H
#define SIG2USER_H

#include <signal.h>

/*
 * ============= SIGSERGV Handler ret2usr =============
 * SIGSEGV handler can trick to bypass KPTI/NX after failed iretq
 * 
 * If ROP fails and causes a userland segfault, we register a
 *      SIGSEGV handler (e.g., get_shell). The kernel sets up a clean
 *      signal frame, restores user page tables (with exec perms), and
 *      safely invokes the handler in user mode — even under KPTI.
 */

// Simply run:
// signal(SIGSEGV, get_shell);


#endif  // SIG2USER_H
