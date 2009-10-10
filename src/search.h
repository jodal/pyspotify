typedef struct {
    PyObject_HEAD
    sp_search *_search;
} Results;

extern PyTypeObject ResultsType;

extern void search_init(PyObject *m);
