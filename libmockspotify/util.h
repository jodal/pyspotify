#ifndef UTIL_H
#define UTIL_H

/*** Utility functions ***/

#define true 1
#define false 0

#ifdef DEBUG
#define DEBUGTEST 1
#else
#define DEBUGTEST 0
#endif

#define DEBUG_PRINT(fmt, ...)                                               \
    do { if (DEBUGTEST) fprintf(stderr, "%s:%d:%s(): " fmt "\n", __FILE__,     \
                            __LINE__, __func__, __VA_ARGS__); } while (0)

#define ALLOC(type) ALLOC_N(type, 1)
#define ALLOC_N(type, n) ((type*) xmalloc(sizeof(type) * (n)))
#define ALLOC_STR(n) ALLOC_N(char, n + 1)

#define MEMCPY(dst, src, type) MEMCPY_N(dst, src, type, 1)
#define MEMCPY_N(dst, src, type, n) (memcpy((dst), (src), sizeof(type) * (n)))

#define UNUSED(x) UNUSED_ ## x __attribute__((unused))

void *xmalloc(size_t);
void xfree(void *);
char *hextoa(const char *, int);
void atohex(char *, const byte *, int);
char *strclone(const char *string);
int compare_ints(const void *, const void *);
char *image_id_to_uri(const byte *);
char *unregion(int);

#define STARTS_WITH(x, y) (strncmp((x), (y), strlen(y)) == 0)

#define DEFINE_REFCOUNTERS_FOR(type)       \
  sp_error sp_##type##_add_ref(sp_##type *UNUSED(x)) { return SP_ERROR_OK;} \
  sp_error sp_##type##_release(sp_##type *UNUSED(x)) { return SP_ERROR_OK;}

#define DEFINE_READER(kind, field, return_type) \
  return_type sp_##kind##_##field(sp_##kind *x) \
  {                                             \
    return x->field;                            \
  }

#define DEFINE_MOCK_READER(kind, field, return_type) \
  return_type mocksp_##kind##_get_##field(sp_##kind *x) \
  {                                             \
    return x->field;                            \
  }

#define DEFINE_SESSION_READER(kind, field, return_type) \
  return_type sp_##kind##_##field(sp_session *UNUSED(x), sp_##kind *y) \
  {                                                     \
    return y->field;                                    \
  }

#define DEFINE_ARRAY_READER(kind, field, return_type) \
  return_type sp_##kind##_##field(sp_##kind *x, int index) \
  {                                                        \
    if (index >= x->num_##field##s) return NULL;         \
    return x->field##s[index];                           \
  }

#define DEFINE_ARRAY_MEMBER_READER(kind, field, member, return_type) \
  return_type sp_##kind##_##field##_##member(sp_##kind *x, int index) \
  {                                                        \
    if (index >= x->num_##field##s) return (return_type) 0;         \
    return x->field##s[index].member;                   \
  }

#define DEFINE_IMAGE_READER(kind, field)                            \
  const byte *sp_##kind##_##field(sp_##kind *x, sp_image_size size) \
  {                                                                 \
    return x->field;                                                \
  }

#endif /* UTIL_H */
