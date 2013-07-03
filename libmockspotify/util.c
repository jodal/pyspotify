#include "libmockspotify.h"
#include "util.h"

void*
xmalloc(size_t size)
{
  void *ptr = malloc(size);
  memset(ptr, 0, size);
  return ptr;
}

void
xfree(void *ptr)
{
  if (ptr)
  {
    free(ptr);
  }
}

int
htoi(char n)
{
  if (n >= '0' && n <= '9') return n - '0';
  else if (n >= 'a' && n <= 'f') return n - 'a' + 10;
  else if (n >= 'A' && n <= 'F') return n - 'A' + 10;
  else return 0;
}

char
itoh(int n)
{
  char hex[] = { "0123456789abcdef" };
  return hex[n];
}

char*
hextoa(const char *str, int size)
{
  int length, i;
  char *result = NULL;

  if (size % 2) return NULL;

  length = (size / 2);
  result = ALLOC_STR(length);

  for (i = 0; i < size; i += 2)
  {
    result[i/2] = (htoi(str[i]) << 4) + htoi(str[i+1]);
  }

  // this is okay, length is actually strlen(result) -1
  result[length] = '\0';

  return result;
}

void
atohex(char *dst, const byte *src, int size)
{
  int i;
  int p;

  for (i = p = 0; i < size; i += 2, p = i/2)
  {
    dst[i]   = itoh((src[p] >> 4) & 0x0F);
    dst[i+1] = itoh(src[p] & 0xF);
  }
}

char *
strclone(const char *string)
{
  char *dst = NULL;

  if (string == NULL)
  {
    return (char *) ""; /* Oh shit… */
  }

  dst = ALLOC_STR(strlen(string));
  strcpy(dst, string);
  return dst;
}

int
compare_ints(const void *a, const void *b)
{
  const int *ia = (int *)a;
  const int *ib = (int *)b;

  return *ia - *ib;
}

char *
image_id_to_uri(const byte *image_id)
{
  char *data = ALLOC_STR(54);
  sprintf(data, "spotify:image:");
  atohex(data + strlen("spotify:image:"), image_id, 40);
  return data;
}

char *unregion(int iregion)
{
  char *region = ALLOC_STR(2);
  region[0] = (iregion >> 8) & 0x00FF;
  region[1] = iregion & 0x00FF;
  return region;
}
