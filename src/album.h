typedef struct {
    PyObject_HEAD sp_album *_album;
} Album;

#define Album_SP_ALBUM(a) ((Album *)a)->_album

extern PyTypeObject AlbumType;

extern void album_init(PyObject *m);

PyObject *Album_FromSpotify(sp_album * album);
