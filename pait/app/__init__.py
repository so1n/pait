from .auto_load_app import auto_load_app_class
from .flask_pait import load_app as load_flask
from .flask_pait import pait as flask_pait
from .starletter_pait import load_app as load_starlette
from .starletter_pait import pait as starlette_pait


def load_app(app):
    app_name: str = app.__class__.__name__
    if app_name == 'Flask':
        load_flask(app)
    elif app_name == 'Starlette':
        load_starlette(app)
    else:
        raise NotImplementedError(f'Pait not support:{app}')


def pait(tag='root'):
    load_class_app = auto_load_app_class()
    if load_class_app.__name__ == 'Flask':
        flask_pait(tag=tag)
    elif load_class_app.__name__ == 'Starlette':
        starlette_pait(tag=tag)
    else:
        raise NotImplementedError(f'Pait not support:{load_class_app}')

