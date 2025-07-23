/**
 * Title : Qemu PCI devices Pwn Exploit
 * Author: Axura (@4xura) - https://4xura.com
 *
 * Description:
 * ------------
 * Exploit script for a PCI device inside a QEMU virtual machine.
 * Provides MMIO and PMIO access primitives for interacting with a memory-mapped
 * or port-mapped emulated device (e.g., `resource0`) exposed by QEMU.
 *
 * TODO:
 * -----
 * - Extend IO primitives 
 *
 * Usage:
 * ------
 * gcc -o xpl -g -O0 -static xpl.c
 *
 * Notes:
 * ------
 * Provided for educational use. Use responsibly.
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <stddef.h>
#include <sys/mman.h>
#include <stdint.h>
#include <sys/io.h>

#define leak(sym) \
    printf("[*] Leak %-20s addr: \033[1;33m0x%lx\033[0m\n", #sym, (size_t)(sym))

#define leak64(sym) \
    printf("[*] Leak %-20s addr: \033[1;33m0x%llx\033[0m\n", #sym, (uint64_t)(sym))

#define die(msg)                         \
    do {                                                \
        fprintf(stderr, "\033[31m\033[1m[x] Error: \033[0m%s\n", msg);  \
        perror("");                                     \
        exit(EXIT_FAILURE);                             \
    } while (0)

/* 
 * PCI Device
 */
#define PCI_DEVICE  "/sys/devices/pci0000:00/0000:00:04.0/resource0" 

// Open PCI device
int open_pci_resource(const char *pci_resource_path) {
    int fd = open(pci_resource_path, O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("open pci resource");
        exit(EXIT_FAILURE);
    }
    return fd;
}

/* 
 * MMIO 
 */
#define MMIO_REGS   64
#define MMIO_SIZE   (MMIO_REGS * sizeof(uint32_t))

#define MAP_SIZE    0x1000UL 
#define MAP_MASK    (MAP_SIZE - 1)

// Map MMIO region using fd open from pci device
void *map_mmio_region(int fd) {
    void *mmio_base = mmap(NULL, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (mmio_base == MAP_FAILED) {
        perror("mmap failed");
        exit(EXIT_FAILURE);
    }
    return mmio_base;
}

// Read 32-bit value from MMIO
uint32_t mmio_read(uint32_t addr) {
    return *(uint32_t *)addr;
}

// Write 32-bit value to MMIO
void mmio_write(uint32_t addr, uint32_t val) {
    *((uint32_t *)addr) = val;
}

/* 
 * PMIO 
 */
#define PMIO_ADDR   0
#define PMIO_DATA   4
#define PMIO_REGS   STRNG_MMIO_REGS
#define PMIO_SIZE   8
#define PMIO_PORT   0xc050

// Require CAP_SYS_RAWIO
void setup_pmio(void) {
    if (iopl(3) < 0) {
        perror("failed to change I/O privilege level (need root?)");
        exit(EXIT_FAILURE);
    }
}

// Read 32-bit value to PMIO
uint32_t pmio_read(uint32_t port) {
    return inl(port);
}

// Write 32-bit value to PMIO
void pmio_write(uint32_t port, uint32_t val) {
    outl(val, port);
}

/*
 * Exploit
 */
int main(int argc, char **argv, char **envp)
{
    /*
     * initialization
     */
    int         mmio_fd;
    uint64_t    mmio_base;  // Target host is 64 bit

    mmio_fd     = open_pci_resource(PCI_DEVICE);
    mmio_base   = (uint64_t)map_mmio_region(mmio_fd);
    leak64(mmio_base);

    setup_pmio();





    return 0;
}

