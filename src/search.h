typedef struct {
    PyObject_HEAD
    sp_search *_search;
} Results;

#define Results_SP_SEARCH(o) ((Results *)o)->_search

extern PyTypeObject ResultsType;

PyObject *
Results_FromSpotify(sp_search * search);

extern void
search_init(PyObject *m);
