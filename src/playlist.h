typedef struct {
    PyObject_HEAD
    sp_playlist *_playlist;
} Playlist;

typedef struct {
    PyObject_HEAD
    sp_playlistcontainer *_playlistcontainer;
} PlaylistContainer;

extern PyTypeObject PlaylistType;
extern PyTypeObject PlaylistContainerType;

extern void playlist_init(PyObject *m);
