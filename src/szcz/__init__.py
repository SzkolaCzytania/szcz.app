from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.include('pyramid_fanstatic')
    config.include('velruse.providers.google')
    config.include('velruse.providers.facebook')
    config.include('velruse.providers.twitter')
    config.add_route('home', '/')
    config.scan()
    config.set_root_factory('szcz.views.Context')
    config.set_session_factory('szcz.views.session_factory')
    return config.make_wsgi_app()
