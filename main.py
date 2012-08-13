from flask import Flask
from flask import render_template
from flaskext.markdown import Markdown

from config import config
import utils


app = Flask(__name__)
md = Markdown(app, extensions=['attr_list', 'fenced_code'])


@app.route('/')
def index():
    return render_template('admin/index.html', config=config)


@app.route('/generate')
def generate():
    posts = utils.get_posts()

    index_content = render_template('frontend/index.html',
                                    config=config,
                                    posts=posts)
    file('site/index.html', 'w').write(
                                    index_content.encode(config['encoding']))

    not_found_content = render_template('404.html', config=config)
    file('site/404.html', 'w').write(
                                not_found_content.encode(config['encoding']))

    utils.clear_dir('site/posts')
    infos = utils.get_post_infos()

    for info in infos:
        with open('posts/%s' % info['filename'], 'r') as f:
            content = f.read().decode(config['encoding'])
            title, content = utils.postprocess_post_content(info['slug'],
                                                            content, False)
            html_content = render_template('frontend/post.html',
                                           config=config,
                                           title=title,
                                           content=content)
            file('site/posts/%s.html' % info['slug'], 'w').write(
                                    html_content.encode(config['encoding']))

    return 'Done!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config['debug'])
