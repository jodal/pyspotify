typedef struct {
    PyObject_HEAD sp_link *_link;
} Link;

extern PyTypeObject LinkType;

extern void link_init(PyObject *m);
