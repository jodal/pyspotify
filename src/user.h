typedef struct {
    PyObject_HEAD
    sp_user *_user;
} User;

extern PyTypeObject UserType;

extern void user_init(PyObject *m);

PyObject *User_FromSpotify(sp_user * user);
