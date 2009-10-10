static PyTypeObject TrackType;

typedef struct {
    PyObject_HEAD
    sp_track *_track;
} Track;

typedef struct {
    PyObject_HEAD
    sp_link *_link;
} Link;

typedef struct {
    PyObject_HEAD
    sp_album *_album;
} Album;

typedef struct {
    PyObject_HEAD
    sp_artist *_artist;
} Artist;

typedef struct {
    PyObject_HEAD
    sp_playlist *_playlist;
} Playlist;

typedef struct {
    PyObject_HEAD
    sp_playlistcontainer *_playlistcontainer;
} PlaylistContainer;

typedef struct {
    PyObject_HEAD
    sp_search *_search;
} Results;

typedef struct {
    PyObject_HEAD
    sp_session *_session;
} Session;

