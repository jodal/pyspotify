#include "libmockspotify.h"
#include "util.h"

typedef struct node_t node_t;
struct node_t
{
  char *url;
  void *ptr;
  node_t *next;
};

node_t *g_node = NULL;
node_t **g_tail = &g_node;

void *
registry_find(const char *url)
{
  node_t *curr;

  for (curr = g_node; curr; curr = curr->next)
  {
    if (strcmp(url, curr->url) == 0) return curr->ptr;
  }

  return NULL;
}

const char *
registry_reverse_find(void *sp_pointer)
{
  node_t *curr;

  for (curr = g_node; curr; curr = curr->next)
  {
    if (curr->ptr == sp_pointer) return curr->url;
  }

  return NULL;
}

void
registry_add(const char *url, void *ptr)
{
  *g_tail = ALLOC(node_t);
  (*g_tail)->url = strclone(url);
  (*g_tail)->ptr = ptr;
  g_tail = &((*g_tail)->next);
}

void
registry_clean(void)
{
  node_t *curr;
  node_t *next;

  for (curr = g_node; curr; curr = next)
  {
    next = curr->next;
    free(curr);
  }

  g_node = NULL;
  g_tail = &g_node;
}
