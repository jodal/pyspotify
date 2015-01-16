#include "libmockspotify.h"
#include "util.h"

sp_user *
mocksp_user_create(const char *canonical_name, const char *display_name, bool is_loaded)
{
    sp_user *user = ALLOC(sp_user);

    user->canonical_name = strclone(canonical_name);
    user->display_name   = strclone(display_name);
    user->is_loaded      = is_loaded;

    return user;
}

DEFINE_REFCOUNTERS_FOR(user);

DEFINE_READER(user, canonical_name, const char *);
DEFINE_READER(user, display_name, const char *);
DEFINE_READER(user, is_loaded, bool);
