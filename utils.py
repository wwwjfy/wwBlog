def cmp_post_names(a, b):
    return cmp(int(a.split('-', 1)[0]),
               int(b.split('-', 1)[0]))


def sort_post_names(names):
    names.sort(cmp=cmp_post_names)


def postprocess_post_content(slug, content, title_with_link):
    lines = content.splitlines()
    title_line, time_line = lines[0], lines[2]
    if not title_line.startswith('# '):
        assert('Unsupported format: first line is not started with "# "')
    title = title_line[2:]
    if title_with_link:
        lines[0] = '# [%s](/posts/%s)' % (title, slug)
    lines.insert(3, '{: .time }')
    return title, '\n'.join(lines)
