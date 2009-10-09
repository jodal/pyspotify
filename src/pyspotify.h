static PyTypeObject TrackType;

typedef struct {
    PyObject_HEAD
    sp_track *_track;
} Track;

