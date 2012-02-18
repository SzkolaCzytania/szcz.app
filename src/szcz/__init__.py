from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pkg_resources import resource_filename
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from deform import Form


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

MirrorDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
MirrorBase = declarative_base()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.apps.')
    DBSession.configure(bind=engine)
    mirror_engine = engine_from_config(settings, 'sqlalchemy.mirror.')
    MirrorDBSession.configure(bind=mirror_engine)
    MirrorBase.metadata.bind = mirror_engine

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

    deform_templates = resource_filename('deform', 'templates')
    deform_bootstrap_templates = resource_filename('deform_bootstrap', 'templates')
    deform_szcz_templates = resource_filename('szcz', 'templates')
    search_path = (deform_szcz_templates, deform_bootstrap_templates, deform_templates)
    Form.set_zpt_renderer(search_path)

    config.add_route('home', '/')
    config.add_route('logout', '/logout')
    config.add_route('userprofile', '/profile')
    config.add_route('books', '/books')
    config.add_route('book', '/book/{id}')

    config.add_static_view('deform_static', 'deform:static')
    config.scan()
    config.set_root_factory('szcz.views.Context')
    config.set_session_factory(session_factory)
    return config.make_wsgi_app()
