import os
import yaml


config = yaml.load(file('config.yaml', 'r'))

if os.path.exists('config.prod.yaml'):
    config.update(yaml.load(file('config.prod.yaml', 'r')))
