typedef struct {
    PyObject_HEAD
    sp_toplistbrowse *_toplistbrowse;
} ToplistBrowser;

#define ToplistBrowser_SP_TOPLISTBROWSE(o) ((ToplistBrowser *)o)->_toplistbrowse

extern PyTypeObject ToplistBrowserType;

PyObject *
ToplistBrowser_FromSpotify(sp_toplistbrowse *browser);

extern void
toplistbrowser_init(PyObject *module);
