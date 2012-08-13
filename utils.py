import os
import re

from config import config


legal_post_file_name = re.compile(r'(^[0-9]+)-(.*)\.md$')


def sort_post_infos(infos):
    infos.sort(key=lambda info: info['time'])


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


def clear_dir(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.startswith('.'):
                os.remove(os.path.join(dirpath, filename))


def get_post_infos():
    preprocessed_names = os.walk('posts').next()[2]
    infos = []
    for name in preprocessed_names:
        match = legal_post_file_name.match(name)
        if match is not None:
            infos.append({'filename': match.group(0),
                          'time': int(match.group(1)),
                          'slug': match.group(2)})
    sort_post_infos(infos)
    return infos


def get_posts():
    infos = get_post_infos()

    posts = []
    for info in infos:
        with open('posts/%s' % info['filename'], 'r') as f:
            content = f.read().decode(config['encoding'])
            _, content = postprocess_post_content(info['slug'], content, True)
            posts.append(content)
    return posts
