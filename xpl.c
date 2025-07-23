/**
 * Title : Linux Kernel Pwn Exploit
 * Author: Axura (@4xura) - https://4xura.com
 *
 * Description:
 * ------------
 * Entry point for a modular Linux kernel exploitation framework.
 * Move libs here from the framework for one-script exploit if needed.
 *
 * TODO:
 * -----
 * - Kernel heap exploit modules
 * - IO modules
 *
 * Usage:
 * ------
 * Refer to the Makefile ($ make help)
 *
 * Notes:
 * ------
 * Provided for educational use. Use responsibly.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h> 
#include <stddef.h>
#include <fcntl.h>
#include <errno.h>
#include "include/globals.h"
#include "include/utils.h"
#include "include/rop.h"

/* Configuration */
#define DEVICE_PATH     "/dev/vulndev"

/* IOCTL Codes */
#define VULN_IOCTL_READ  _IOR(0x1337, 1, char *)
#define VULN_IOCTL_WRITE _IOW(0x1337, 2, char *)
#define VULN_IOCTL_EXEC  _IO(0x1337, 3)

/* Exploit Entry */
int main(void)
{
    int fd = open_dev(DEVICE_PATH, O_RDWR);





    close(fd);
    printf("[✓] Done\n");
    return 0;
}

