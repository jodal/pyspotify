typedef struct {
    PyObject_HEAD
    sp_user *_user;
} User;

#define User_SP_USER(o) ((User *)o)->_user

extern PyTypeObject UserType;

PyObject *
User_FromSpotify(sp_user *user, bool add_ref);

extern void
user_init(PyObject *module);

