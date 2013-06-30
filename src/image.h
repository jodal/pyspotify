typedef struct {
    PyObject_HEAD
    sp_image *_image;
} Image;

#define Image_SP_IMAGE(o) ((Image *)o)->_image

extern PyTypeObject ImageType;

PyObject *
Image_FromSpotify(sp_image *image, bool add_ref);

extern void
image_init(PyObject *module);
