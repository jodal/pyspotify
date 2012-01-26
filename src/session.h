typedef struct {
    PyObject_HEAD
    sp_session *_session;
    PyObject *client;
} Session;

extern sp_session *g_session;

extern PyTypeObject SessionType;
extern void session_init(PyObject *m);
extern PyObject *session_connect(PyObject *self, PyObject *args);

extern PyObject *handle_error(int error);

PyObject *
Session_FromSpotify(sp_session * session);
