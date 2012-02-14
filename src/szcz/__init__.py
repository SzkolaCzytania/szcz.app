from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    session_factory = session_factory_from_settings(settings)
    authentication_policy = SessionAuthenticationPolicy()
    authorization_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings)
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    config.set_request_property('szcz.security.get_user', name='user', reify=True)

    config.include('pyramid_fanstatic')
    config.include('velruse.providers.google')
    config.include('velruse.providers.facebook')
    config.include('velruse.providers.twitter')
    config.include('pyramid_beaker')
    config.include('deform_bootstrap')

    config.add_route('home', '/')
    config.add_route('login_form', '/login_form')
    config.add_route('logout', '/logout')
    config.add_route('usercreate', '/usercreate')

    config.add_static_view('deform_static', 'deform:static')
    config.scan()
    config.set_root_factory('szcz.views.Context')
    config.set_session_factory(session_factory)
    return config.make_wsgi_app()
