typedef struct {
    PyObject_HEAD
    sp_link *_link;
} Link;

#define Link_SP_LINK(o) ((Link *)o)->_link
#define LINK_MAX_URI_LENGTH 1024

extern PyTypeObject LinkType;

extern void
link_init(PyObject *module);
