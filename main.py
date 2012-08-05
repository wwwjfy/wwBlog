import os
import re

from flask import Flask
from flask import render_template
from flaskext.markdown import Markdown
import yaml

import utils


config = yaml.load(file('config.yaml', 'r'))

app = Flask(__name__)
md = Markdown(app, extensions=['attr_list', 'fenced_code'])

legal_post_file_name = re.compile(r'^[0-9]+-.*\.md$')


@app.route('/')
def index():
    return render_template('admin/index.html', config=config)


@app.route('/generate')
def generate():
    _, _, preprocessed_names = os.walk('posts').next()
    names = []
    for name in preprocessed_names:
        if legal_post_file_name.match(name) is not None:
            names.append(name)
    utils.sort_post_names(names)

    posts = []
    for name in names:
        with open('posts/%s' % name, 'r') as f:
            posts.append(f.read().decode(config['encoding']))

    index_content = render_template('frontend/index.html', config=config, posts=posts)
    file('site/index.html', 'w').write(index_content.encode(config['encoding']))
    return 'Done!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config['debug'])
