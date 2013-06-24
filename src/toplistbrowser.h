typedef struct {
    PyObject_HEAD
    sp_toplistbrowse *_toplistbrowse;
} ToplistBrowser;

typedef struct {
    sp_toplistregion type;
    char *username;
} toplistregion;

#define ToplistBrowser_SP_TOPLISTBROWSE(o) ((ToplistBrowser *)o)->_toplistbrowse

extern PyTypeObject ToplistBrowserType;

PyObject *
ToplistBrowser_FromSpotify(sp_toplistbrowse *browser, bool add_ref);

extern void
toplistbrowser_init(PyObject *module);
