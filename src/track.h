typedef struct {
    PyObject_HEAD
    sp_track *_track;
} Track;

#define Track_SP_TRACK(o) ((Track *)o)->_track

extern PyTypeObject TrackType;

PyObject *
Track_FromSpotify(sp_track * track);

extern void
track_init(PyObject *module);
