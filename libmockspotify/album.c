#include "libmockspotify.h"
#include "util.h"

sp_album *
mocksp_album_create(const char *name, sp_artist *artist, int year, const byte *cover,
                    sp_albumtype type, bool loaded, bool available)
{
  sp_album *album = ALLOC(sp_album);

  album->name         = strclone(name);
  album->year         = year;
  album->type         = type;
  album->artist       = artist;
  album->is_loaded    = loaded;
  album->is_available = available;

  if (cover)
  {
    album->cover = ALLOC_N(byte, 20);
    MEMCPY_N(album->cover, cover, byte, 20);
  }

  return album;
}

DEFINE_REFCOUNTERS_FOR(album);

DEFINE_READER(album, is_loaded, bool);
DEFINE_READER(album, is_available, bool);
DEFINE_READER(album, artist, sp_artist *);
DEFINE_IMAGE_READER(album, cover);
DEFINE_READER(album, name, const char *);
DEFINE_READER(album, year, int);
DEFINE_READER(album, type, sp_albumtype);
