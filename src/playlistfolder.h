#include <Python.h>
#include "pyspotify.h"

typedef struct {
    PyObject_HEAD
    char        *_name;
    sp_uint64   _id;
    sp_playlist_type _type;
} PlaylistFolder;

extern PyTypeObject PlaylistFolderType;

extern void playlistfolder_init(PyObject *m);

PyObject *PlaylistFolder_FromSpotify(sp_playlistcontainer *pc,
                                     int index,
                                     sp_playlist_type type);
