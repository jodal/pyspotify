TARGET=spshell
LDLIBS += -lreadline
CFLAGs += -Werror

include ../common.mk

$(TARGET): spshell.o spshell_posix.o appkey.o cmd.o browse.o search.o toplist.o star.o
