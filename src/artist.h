typedef struct {
    PyObject_HEAD sp_artist *_artist;
} Artist;

extern PyTypeObject ArtistType;

extern void artist_init(PyObject *m);

PyObject *Artist_FromSpotify(sp_artist * artist);
