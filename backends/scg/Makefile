CC ?= gcc
CFLAGS = -O2 -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Wpedantic -I/usr/X11R6/include
LDFLAGS = -L/usr/X11R6/lib
LDLIBS = -lX11 -lXrandr

build:
	$(CC) $(CFLAGS) $(LDFLAGS) -o scg scg.c $(LDLIBS)

clean:
	rm -f scg
