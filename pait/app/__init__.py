from .auto_load_app import auto_load_app_class
from .pait_flask import load_app as load_flask
from .pait_flask import params_verify as flask_params_verify
from .pait_starletter import load_app as load_starlette
from .pait_starletter import params_verify as starlette_params_verify


def load_app(app):
    app_name: str = app.__class__.__name__
    if app_name == 'Flask':
        load_flask(app)
    elif app_name == 'Starlette':
        load_starlette(app)
    else:
        raise NotImplementedError(f'Pait not support:{app}')


def params_verify(tag='root'):
    load_class_app = auto_load_app_class()
    if load_class_app.__name__ == 'Flask':
        flask_params_verify(tag=tag)
    elif load_class_app.__name__ == 'Starlette':
        starlette_params_verify(tag=tag)
    else:
        raise NotImplementedError(f'Pait not support:{load_class_app}')

