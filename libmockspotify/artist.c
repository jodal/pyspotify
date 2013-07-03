#include "libmockspotify.h"
#include "util.h"

sp_artist *
mocksp_artist_create(const char *name, const byte* portrait, bool is_loaded)
{
  sp_artist *artist = ALLOC(sp_artist);
  artist->name      = strclone(name);
  artist->is_loaded = is_loaded;

  if (portrait)
  {
    artist->portrait = ALLOC_N(byte, 20);
    MEMCPY_N(artist->portrait, portrait, byte, 20);
  }

  return artist;
}

DEFINE_REFCOUNTERS_FOR(artist);
DEFINE_READER(artist, name, const char *);
DEFINE_IMAGE_READER(artist, portrait);
DEFINE_READER(artist, is_loaded, bool);
