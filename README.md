## Project file structure

```c
project-root/
├── xpl.py              // Exploit script for userland pwn (Python)
│
├── xpl.c               // Kernel exploit entry point (C)
│
├── Makefile            // Build options: default, debug, static, release
│
├── include/                // Shared headers
│   ├── utils.h             // Common macros & helpers (e.g., DIE(), hexdump(), etc.)
│   ├── stack_overflow.h    // Cookie leaker, overflow primitives
│   ├── ret2usr.h          // IRETQ trampoline, user context manager
│   └── ...
│ 
├── src/                // Modular exploit components (optional)
│   ├── utils.c
│   ├── stack_overflow.c
│   ├── ret2usr.c
│   └── ... 
│ 
├── obj/                // Auto-generated object files
│   └── *.o             // Keeps artifacts isolated      
│
├── lib/                // Auto-generated library files
│   └── libxpl.a        // Made from src/*.c to store .a file for only the needed symbols into final binary
│
├── scripts/                    // Helper automation and debugging scripts
│   ├── extract_image.sh        // Extract contents from kernel image (vmlinuz, bzImage, etc.)
│   ├── extract_initramfs.sh    // Unpack initramfs for modification or inspection
│   ├── pack_initramfs.sh       // Compile exploit binary and repackage it into initramfs.cpio.gz
│   ├── run_serial.sh           // Launch QEMU with serial terminal
│   ├── run_ret2usr.sh         // Boot QEMU for ret2usr-style kernel exploit testing\
│   └── patch_alarm.py          // Patch alarm syscall
│
├── xpl                 // Final compiled exploit binary
│
├── flag.txt            // Fake flags used for local testing
└── flag
```

### Userland pwn:

- **`xpl.py`**: Exploit script for userland challenges interfacing with `pwntools`, GDB, glibc, etc.

### Kernel pwn:

- **`xpl.c`**: This main exploit entry point (`main()`), typically crafted to trigger a vulnerability in a kernel module.
- **`include/`**: Contains headers for reusable components. Each `.h` defines the API for its corresponding `.c` module under `src/`.
- **`src/*.c`**: Modular C implementations for each major exploit component. These files are cleanly separated and easy to reuse across different kernel exploit chains.
- **`obj/*.o`**: Compiled object files for each .c source file to ensure a clean, flat object output directory and simplifies linking.
- **`lib/libxpl.a`**: A static archive containing all compiled object modules from `src/*.c`. This archive allows linking only necessary components into the final binary. This supports modular reuse—`xpl.c` can selectively link only the modules it needs from libxpl.a, avoiding recompilation or unnecessary code inclusion.
- **`build/`**: Auto-generated directory for `.o` files (one per `.c` file). Keeps root clean and build artifacts separated.
- **`Makefile`**: Flexible build system supporting different modes:
  - `make` – Default build for local testing (optimized, no debug info)
  - `make debug` – Adds debug symbols (`-g`) and disables optimizations (`-Og`) for easier GDB analysis
  - `make static` – Statically links everything (e.g., for isolated environments or remote kernel testing)
  - `make release` – Fully optimized and statically linked for final delivery or deployment
  - `make strip` – Removes symbol tables and debug info from the compiled binary
  - `make clean` – Cleans all generated artifacts

### Scripts

Suggest run scripts under project root directory, namely for example:

```sh
bash scripts/run_serial.sh
```

The `scripts/` folder contains utility scripts used to assist with compiling, extracting, and booting pwn lab environment:

- **`extract_image.sh`** – Extracts a raw disk image (e.g. `vmlinux`) for manual patching or inspection from a compressed kernel (e.g. `vmlinuz`).
- **`extract_initramfs.sh`** – Unpacks a gzipped `initramfs.cpio.gz` for manual modifications.
- **`pack_initramfs.sh`** – Compiles exploit (statically), moves it into the extracted `initramfs/`, and repacks it into `initramfs.cpio.gz`.
- **`run_serial.sh`** – Starts a QEMU guest with kernel serial output (good for debugging with `-nographic`).
- **`run_ret2usr.sh`** – Starts a preconfigured QEMU instance for local kernel ret2usr-style exploitation.
- **`patch_alarm.py`** – Custom patch ELF script to bypass the annoying alarm syscall for debugging.

