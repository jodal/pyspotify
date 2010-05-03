EXAMPLES=jukebox spshell

.PHONY: all clean

ifdef LIBSPOTIFY_PATH
ARG=LIBSPOTIFY_PATH="$(shell cd "$(LIBSPOTIFY_PATH)" && pwd)"
endif

all clean:
	for a in $(EXAMPLES); do $(MAKE) -C $$a $(ARG) $@; done
