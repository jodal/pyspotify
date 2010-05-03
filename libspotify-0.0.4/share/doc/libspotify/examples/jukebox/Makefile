ifeq ($(shell uname),Darwin)
ifdef USE_AUDIOQUEUE
AUDIO_DRIVER=osx
LDFLAGS += -framework AudioToolbox
else
AUDIO_DRIVER=openal
LDFLAGS += -framework OpenAL
endif
else
CFLAGS  = $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --cflags alsa)
LDFLAGS = $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --libs-only-L alsa)
LDLIBS  = $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --libs-only-l --libs-only-other alsa)
AUDIO_DRIVER=alsa
endif

TARGET=jukebox

include ../common.mk

$(TARGET): jukebox.o appkey.o $(AUDIO_DRIVER)-audio.o audio.o

audio.o: audio.c audio.h
alsa-audio.o: alsa-audio.c audio.h
osx-audio.o: osx-audio.c audio.h
openal-audio.o: openal-audio.c audio.h
jukebox.o: jukebox.c audio.h
