typedef struct {
    PyObject_HEAD
    sp_session *_session;
    PyObject *client;
} Session;

#define Session_SP_SESSION(o) ((Session *)o)->_session

extern sp_session *g_session;

extern PyTypeObject SessionType;
extern void session_init(PyObject *m);

extern PyObject *handle_error(int error);

PyObject *
Session_FromSpotify(sp_session * session);
