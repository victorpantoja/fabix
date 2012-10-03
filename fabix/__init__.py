# coding: utf-8
import fabric.api

VERSION = (0, 0, 1)

__version__ = ".".join([str(v) for v in VERSION])


def get_config(name=None):
    fabric.api.require('fabix')
    project_name = fabric.api.env.fabix.get('_current_project')
    config = fabric.api.env.fabix[project_name]
    if name is not None:
        return config[name]
    else:
        return config
