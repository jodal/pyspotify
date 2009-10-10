typedef struct {
    PyObject_HEAD
    sp_track *_track;
} Track;

extern PyTypeObject TrackType;

extern void track_init(PyObject *m);
