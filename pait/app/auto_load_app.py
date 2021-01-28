try:
    from flask import Flask
except ImportError:
    Flask = None

try:
    from starlette.applications import Starlette
except ImportError:
    Starlette = None


def auto_load_app_class():
    """A project using only a web framework, to use `auto_load_app_class`"""
    app_list: list = [Flask, Starlette]
    real_app = None
    for app in app_list:
        if app:
            raise RuntimeError(f'Pait unable to make a choice {real_app} & {app}')
        real_app = app
    if not real_app:
        raise RuntimeError("Pait can't auto load app class")
    return real_app
