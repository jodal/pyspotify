typedef struct {
    PyObject_HEAD
    sp_session *_session;
} Session;

extern PyTypeObject SessionType;
extern void session_init(PyObject *m);
extern PyObject *session_connect(PyObject *self, PyObject *args);
