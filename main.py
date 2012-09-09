import os
import time

from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flaskext.markdown import Markdown

from config import config
import utils

content_template = """\
# %(title)s

%(time)s

%(content)s
"""


app = Flask(__name__)
Markdown(app, extensions=['attr_list', 'fenced_code'])


@app.route('/')
def index():
    infos = utils.get_post_infos()

    for info in infos:
        with open('posts/%s' % info['filename'], 'r') as f:
            content = f.read().decode(config['encoding'])
            title = utils.get_title(content)
            info['title'] = title
            info['date'] = utils.date_localize_from_utc(info['time'])
    return render_template('admin/index.html', config=config, infos=infos)


@app.route('/generate')
def generate():
    posts = utils.get_posts()

    index_content = render_template('frontend/index.html',
                                    config=config,
                                    frontend=True,
                                    posts=posts)
    file('site/index.html', 'w').write(
                                    index_content.encode(config['encoding']))

    not_found_content = render_template('404.html',
                                        config=config,
                                        frontend=True)
    file('site/404.html', 'w').write(
                                not_found_content.encode(config['encoding']))

    utils.clear_dir('site/posts')
    infos = utils.get_post_infos()

    for info in infos:
        with open('posts/%s' % info['filename'], 'r') as f:
            content = f.read().decode(config['encoding'])
            title = utils.get_title(content)
            content = utils.postprocess_post_content(info['slug'],
                                                            content, False)
            html_content = render_template('frontend/post.html',
                                           config=config,
                                           frontend=True,
                                           title=title,
                                           content=content)
            file('site/posts/%s.html' % info['slug'], 'w').write(
                                    html_content.encode(config['encoding']))

    return 'Done!'


@app.route('/edit/<time_slug>', methods=['GET', 'POST'])
def edit(time_slug):
    filename = '%s.md' % time_slug
    file_path = 'posts/%s' % filename
    if not os.path.exists(file_path):
        # TODO: 404 page
        return '', 404
    if request.method == 'GET':
        info = utils.parse_filename(filename)
        with open(file_path) as f:
            content = f.read().decode(config['encoding'])
        info['title'] = utils.get_title(content)
        info['content'] = '\n'.join(content.splitlines()[4:])
        info['date'] = utils.date_localize_from_utc(info['time'])

        return render_template('admin/edit.html',
                               config=config,
                               info=info)
    elif request.method == 'POST':
        result = utils.parse_filename(filename)
        if not result:
            return '', 404
        with open(file_path) as f:
            origin_content = f.read().decode(config['encoding'])
        title = request.form['title'].strip()
        date = request.form['date'].strip()
        content = request.form['content'].strip()
        slug = request.form['slug'].strip()

        try:
            post_time = utils.datetime2epoch(date)
        except ValueError:
            # TODO: flash message
            return '', 404
        time_str = utils.date_localize_from_utc(post_time)

        file_to_remove = None
        if post_time != result['time'] or slug != result['slug']:
            file_to_remove = file_path
            file_path = 'posts/%s-%s.md' % (post_time, slug)

        file_content = content_template % {'title': title,
                                           'time': time_str,
                                           'content': content}
        with open(file_path, 'w') as f:
            f.write(file_content.encode(config['encoding']))

        if file_to_remove:
            os.remove(file_to_remove)

        return redirect('/')


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'GET':
        info = {'title': 'New post', 'new': '1'}
        return render_template('admin/edit.html',
                               config=config,
                               info=info)
    elif request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        slug = request.form['slug'].strip()
        post_time = int(time.time())
        time_str = utils.date_localize_from_utc(post_time)

        file_content = content_template % {'title': title,
                                           'time': time_str,
                                           'content': content}
        file_path = 'posts/%s-%s.md' % (post_time, slug)
        with open(file_path, 'w') as f:
            f.write(file_content.encode(config['encoding']))

        return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config['debug'])
