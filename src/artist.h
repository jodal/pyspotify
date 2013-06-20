typedef struct {
    PyObject_HEAD
    sp_artist *_artist;
} Artist;

#define Artist_SP_ARTIST(o) ((Artist *)o)->_artist

extern PyTypeObject ArtistType;

PyObject *
Artist_FromSpotify(sp_artist * artist);

extern void
artist_init(PyObject *module);
