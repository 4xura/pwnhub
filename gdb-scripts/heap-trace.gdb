# heap-trace.gdb

set logging file heap_trace.log
set logging redirect on
set logging on
set pagination off

# Breakpoints
break malloc
break calloc
break realloc
break free

# malloc
commands 1
  silent
  printf "[MALLOC] size = %zu\n", $rdi
  backtrace 
  finish
  printf "[MALLOC] returned = %p\n", $rax
  continue
end

# calloc
commands 2
  silent
  printf "[CALLOC] nmemb = %zu, size = %zu\n", $rdi, $rsi
  backtrace 
  finish
  printf "[CALLOC] returned = %p\n", $rax
  continue
end

# realloc
commands 3
  silent
  printf "[REALLOC] ptr = %p, size = %zu\n", $rdi, $rsi
  backtrace 
  finish
  printf "[REALLOC] returned = %p\n", $rax
  continue
end

# free
commands 4
  silent
  printf "[FREE] ptr = %p\n", $rdi
  backtrace 
  continue
end
