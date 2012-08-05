def cmp_post_names(a, b):
    return cmp(int(a.split('-', 1)),
               int(b.split('-', 1)))


def sort_post_names(names):
    names.sort(cmp=cmp_post_names)
