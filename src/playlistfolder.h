#include <Python.h>
#include "pyspotify.h"

typedef struct {
    PyObject_HEAD
    char *_name;
    sp_uint64 _id;
    sp_playlist_type _type;
} PlaylistFolder;

#define PlaylistFolder_ID(o) ((PlaylistFolder *)o)->_id
#define PlaylistFolder_NAME(o) ((PlaylistFolder *)o)->_name
#define PlaylistFolder_SP_PLAYLIST_TYPE(o) ((PlaylistFolder *)o)->_type

extern PyTypeObject PlaylistFolderType;

PyObject *
PlaylistFolder_FromSpotify(sp_playlistcontainer *container, int index,
                           sp_playlist_type type);

extern void playlistfolder_init(PyObject *module);

