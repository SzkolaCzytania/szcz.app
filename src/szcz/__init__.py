from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pkg_resources import resource_filename
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from deform import Form


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    session_factory = session_factory_from_settings(settings)
    from szcz.security import groupfinder
    authentication_policy = SessionAuthenticationPolicy(callback=groupfinder)
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
    config.include('pyramid_mailer')
    config.include('pyramid_zcml')

    deform_templates = resource_filename('deform', 'templates')
    deform_bootstrap_templates = resource_filename('deform_bootstrap', 'templates')
    deform_szcz_templates = resource_filename('szcz', 'templates')
    search_path = (deform_szcz_templates, deform_bootstrap_templates, deform_templates)
    Form.set_zpt_renderer(search_path)

    config.add_route('home', '/')
    config.add_route('logout', '/logout')
    config.add_route('userprofile', '/profile')

    config.add_route('view_book', '/books/{id:\d+}')
    config.add_route('my_books', '/books/only_mine')
    config.add_route('list_books', '/books')

    config.add_route('list_canons', '/canons')
    config.add_route('view_canon', '/canons/{id:\d+}')

    config.add_route('my_groups', '/groups/only_mine')
    config.add_route('list_groups', '/groups')
    config.add_route('add_group', '/groups/+')
    config.add_route('join_group', '/groups/{id:\d+}/join', factory='szcz.groups.GroupContext')
    config.add_route('logo_group', '/groups/{id:\d+}/logo_view', factory='szcz.groups.GroupContext')
    config.add_route('wf_group', '/groups/{id:\d+}/change_state', factory='szcz.groups.GroupContext')
    config.add_route('view_group', '/groups/{id:\d+}', factory='szcz.groups.GroupContext')
    config.add_route('edit_group', '/groups/{id:\d+}/edit', factory='szcz.groups.GroupContext')

    config.add_static_view('deform_static', 'deform:static')
    config.scan()
    config.set_root_factory('szcz.views.Context')
    config.set_session_factory(session_factory)

    config.load_zcml('workflow.zcml')

    return config.make_wsgi_app()
