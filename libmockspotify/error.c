#include <stdio.h>
#include <stdlib.h>
#include "libmockspotify.h"
#include "util.h"

const char*
sp_error_message(sp_error error)
{
    char *buff = ALLOC_N(char, 20);
    sprintf(buff, "sp_error: %d", error);
    return buff;
}
