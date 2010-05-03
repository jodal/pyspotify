prefix ?= /usr/local
arch ?= amd64

all:
	$(error "Usage: make [prefix=/install/me/here] install | uninstall")

install:
	mkdir -p $(prefix)/include/libspotify
	install include/libspotify/api.h $(prefix)/include/libspotify

	mkdir -p $(prefix)/lib
	install $(arch)/libspotify.so.4.0.400076 \
		$(prefix)/lib
	cd $(prefix)/lib && ln -sf libspotify.so.4.0.400076 libspotify.so.4 && ln -sf libspotify.so.4.0.400076 libspotify.so

	mkdir -p $(prefix)/lib/pkgconfig
	sed -e s:@pkg_prefix@:$(prefix):g \
		<pkgconfig/libspotify.pc.in \
		>$(prefix)/lib/pkgconfig/libspotify.pc

frobnicate:;

