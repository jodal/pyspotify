typedef struct {
    PyObject_HEAD sp_image *_image;
} Image;

extern PyTypeObject ImageType;

extern void image_init(PyObject *m);

PyObject *Image_FromSpotify(sp_image * image);
