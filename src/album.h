typedef struct {
    PyObject_HEAD
    sp_album *_album;
} Album;

#define Album_SP_ALBUM(o) ((Album *)o)->_album

extern
PyTypeObject AlbumType;

PyObject *
Album_FromSpotify(sp_album * album);

extern void
album_init(PyObject *module);
