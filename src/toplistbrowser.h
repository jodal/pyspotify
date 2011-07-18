typedef struct {
    PyObject_HEAD
    sp_toplistbrowse *_toplistbrowse;
} ToplistBrowser;

extern PyTypeObject ToplistBrowserType;

extern void toplistbrowser_init(PyObject *m);

PyObject *ToplistBrowser_FromSpotify(sp_toplistbrowse *toplistbrowse);
