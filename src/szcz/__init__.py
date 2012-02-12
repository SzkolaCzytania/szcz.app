from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
from szcz.models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings)
    config.include('pyramid_fanstatic')
    config.include('velruse.providers.google')
    config.include('velruse.providers.facebook')
    config.include('velruse.providers.twitter')
    config.include('pyramid_beaker')
    config.add_route('home', '/')
    config.add_route('logged_in', '/logged_in')
    config.scan()
    config.set_root_factory('szcz.views.Context')
    config.set_session_factory(session_factory)
    return config.make_wsgi_app()
