typedef struct {
    PyObject_HEAD
    sp_session *_session;
} Session;

#define Session_SP_SESSION(o) ((Session *)o)->_session

extern sp_session *g_session;
extern PyTypeObject SessionType;

extern PyObject *
handle_error(sp_error error);

PyObject *
Session_FromSpotify(sp_session * session);

extern void
session_init(PyObject *module);
