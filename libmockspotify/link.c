#include "libmockspotify.h"
#include "urlcode.h"
#include "util.h"

DEFINE_REFCOUNTERS_FOR(link);

sp_linktype
sp_link_type(sp_link *link)
{
  #define LINK_IS(type) (strstr(link->data, ":" #type))
  #define LINK_CASE_FOR(string, type) if (LINK_IS(string)) { return SP_LINKTYPE_##type; }

  LINK_CASE_FOR(search, SEARCH);
  LINK_CASE_FOR(track,  TRACK);
  LINK_CASE_FOR(album,  ALBUM);
  LINK_CASE_FOR(artist, ARTIST);
  LINK_CASE_FOR(image,  IMAGE);

  // Order of these three is significant
  LINK_CASE_FOR(playlist, PLAYLIST);
  LINK_CASE_FOR(starred,  STARRED);
  LINK_CASE_FOR(user,     PROFILE);

  return SP_LINKTYPE_INVALID;
}

/* * * * * * * * * * * * * * * * *
 *                               *
 * Below: sp_link_create_from_X  *
 *                               *
 * * * * * * * * * * * * * * * * */

sp_link *
sp_link_create_from_string(const char *link)
{
  /* unless the link starts with spotify: it is invalid */
  if (!link || !STARTS_WITH(link, "spotify:"))
  {
    return NULL;
  }
  else
  {
    sp_link *lnk = ALLOC(sp_link);
    lnk->data    = strclone(link);
    return lnk;
  }
}

sp_link *
sp_link_create_from_user(sp_user *user)
{
  sp_link *link = ALLOC(sp_link);
  link->data    = ALLOC_STR(strlen("spotify:user:") + strlen(user->canonical_name));
  sprintf(link->data, "spotify:user:%s", user->canonical_name);
  return link;
}

sp_link *
sp_link_create_from_image(sp_image *image)
{
  return sp_link_create_from_string(image_id_to_uri(image->image_id));
}

sp_link *
sp_link_create_from_track(sp_track *track, int offset)
{
  const char *link = registry_reverse_find((void *) track);
  int mins = 0, secs = 0;
  char *link_with_offset = NULL;

  if (offset > 0)
  {
    link_with_offset = ALLOC_STR(strlen(link) + strlen("#00:00"));

    offset = offset / 1000;
    mins = (offset / 60) % 60;
    secs = (offset - mins * 60) % 60;

    sprintf(link_with_offset, "%s", link);
    sprintf(link_with_offset + strlen(link), "#%02d:%02d", mins, secs);
    return sp_link_create_from_string(link_with_offset);
  }
  else
  {
    return sp_link_create_from_string(link);
  }
}

sp_link *
sp_link_create_from_album(sp_album *album)
{
  const char *link = registry_reverse_find((void *) album);
  return sp_link_create_from_string(link);
}

sp_link *
sp_link_create_from_album_cover(sp_album *album, sp_image_size size)
{
  const byte *image_id = sp_album_cover(album, size);

  if ( ! image_id)
  {
    return NULL;
  }

  return sp_link_create_from_string(image_id_to_uri(image_id));
}

sp_link *
sp_link_create_from_playlist(sp_playlist *playlist)
{
  const char *link = registry_reverse_find((void *) playlist);
  return sp_link_create_from_string(link);
}

sp_link *
sp_link_create_from_artist(sp_artist *artist)
{
  const char *link = registry_reverse_find((void *) artist);
  return sp_link_create_from_string(link);
}

sp_link *
sp_link_create_from_artist_portrait(sp_artist *artist, sp_image_size size)
{
  const byte *image_id = sp_artist_portrait(artist, size);

  if ( ! image_id)
  {
    return NULL;
  }

  return sp_link_create_from_string(image_id_to_uri(image_id));
}

sp_link *
sp_link_create_from_artistbrowse_portrait(sp_artistbrowse *artistbrowse, int index)
{
  const byte *image_id = sp_artistbrowse_portrait(artistbrowse, index);

  if ( ! image_id)
  {
    return NULL;
  }

  return sp_link_create_from_string(image_id_to_uri(image_id));
}

sp_link *
sp_link_create_from_search(sp_search *search)
{
  char *uri_encoded = url_encode(search->query);
  char *uri = ALLOC_STR(strlen("spotify:search:") + strlen(uri_encoded));
  sprintf(uri, "spotify:search:%s", uri_encoded);
  return sp_link_create_from_string(uri);
}

/* * * * * * * * * * * *
 *                     *
 * Below: sp_link_as_X *
 *                     *
 * * * * * * * * * * * */

int
sp_link_as_string(sp_link *link, char *buffer, int buffer_size)
{
  strncpy(buffer, link->data, buffer_size);

  if (buffer_size > 0)
  {
    buffer[buffer_size - 1] = '\0';
  }

  return (int) strlen(link->data);
}

#define SP_LINK_AS(type) \
  sp_##type * sp_link_as_##type(sp_link *link)      \
  {                                                 \
    return (sp_##type *) registry_find(link->data); \
  }

SP_LINK_AS(user);
SP_LINK_AS(artist);
SP_LINK_AS(album);
SP_LINK_AS(track);

sp_track *
sp_link_as_track_and_offset(sp_link *link, int *offset)
{
  /* parse the offset */
  int mins = 0, secs = 0;
  char *optr = NULL;

  sp_link *my_link = ALLOC(sp_link);
  my_link->data = strclone(link->data);

  if (optr = strchr(my_link->data, '#'))
  {
    sscanf(optr, "#%2u:%2u", &mins, &secs);
    *offset = (mins * 60 + secs) * 1000;
    *optr   = '\0';
  }
  else
  {
    *offset = 0;
  }

  return sp_link_as_track(my_link);
}
