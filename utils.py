import calendar
import datetime
import os
import re

import pytz

from config import config


legal_post_file_name = re.compile(r'(^[0-9]+)-(.*)\.md$')


def parse_filename(name):
    match = legal_post_file_name.match(name)
    if match is not None:
        return {'filename': match.group(0),
                'time': int(match.group(1)),
                'slug': match.group(2)}


def sort_post_infos(infos):
    infos.sort(key=lambda info: info['time'], reverse=True)


def get_post_infos(with_title=False):
    preprocessed_names = os.walk('posts').next()[2]
    infos = []
    for name in preprocessed_names:
        result = parse_filename(name)
        if result:
            infos.append(result)
    sort_post_infos(infos)
    return infos


def get_title(content):
    lines = content.splitlines()
    title_line = lines[0]
    if not title_line.startswith('# '):
        assert('Unsupported format: first line is not started with "# "')
    return title_line[2:]


def postprocess_post_content(slug, content, title_with_link):
    title = get_title(content)
    lines = content.splitlines()
    if title_with_link:
        lines[0] = '# [%s](/posts/%s)' % (title, slug)
    lines.insert(3, '{: .time }')
    return '\n'.join(lines)


def clear_dir(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.startswith('.'):
                os.remove(os.path.join(dirpath, filename))
        break


def get_posts():
    infos = get_post_infos()

    posts = []
    for info in infos:
        with open('posts/%s' % info['filename'], 'r') as f:
            content = f.read().decode(config['encoding'])
            content = postprocess_post_content(info['slug'], content, True)
            posts.append(content)
    return posts


def date_localize_from_utc(utc, origin=False):
    date = datetime.datetime.fromtimestamp(utc,
                                           pytz.timezone(config['timezone']))
    if origin:
        return date
    else:
        return date.strftime(config['datetime_format'])


def datetime2epoch(date_str):
    d = datetime.datetime.strptime(date_str, config['datetime_format'])
    tz = pytz.timezone(config['timezone'])
    d = tz.localize(d)
    return calendar.timegm(d.utctimetuple())
