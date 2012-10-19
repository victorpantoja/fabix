# coding: utf-8
import fabric.api as fab

VERSION = (0, 0, 2)

__version__ = ".".join([str(v) for v in VERSION])

fab.env.fabix = fab.env.get('fabix', dict())


def get_project_name():
    fab.require('fabix')
    name = fab.env.fabix.get('_current_project', None)
    assert name, "No project defined."
    return name


def get_config(name=None):
    fab.require('fabix')
    pj_name = get_project_name()
    config = fab.env.fabix.get(pj_name, dict())
    if name is not None:
        return config.get(name)
    else:
        return config
