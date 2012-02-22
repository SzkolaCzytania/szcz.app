# -*- coding: utf-8 -*-
from pyramid.security import Allow, Authenticated
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.response import Response
from sqlalchemy.exc import SQLAlchemyError

from szcz.resources import szcz, datatables
from szcz.models import Book, Group, Canon
from szcz import DBSession


class Context(object):
    """  Default context factory. """

    __acl__ = [(Allow, Authenticated, 'view'),
               (Allow, Authenticated, 'user_profile'),]

    def __init__(self, request):
        szcz.need()
        self.request = request


@view_config(context='pyramid.httpexceptions.HTTPNotFound', renderer='templates/notfound.pt')
def notfound(request):
    request.response.status_int = 404
    return {'request': request,
            'main' :  get_renderer('templates/master.pt').implementation()}


@view_config(route_name='home', renderer='templates/home.pt', permission='view')
def home(context, request):
    return {'request': request,
            'main' :  get_renderer('templates/master.pt').implementation()}


@view_config(route_name='list_canons', renderer='templates/list_canons.pt', permission='view')
def list_canons(context, request):
    datatables.need()
    canons = DBSession().query(Canon).order_by(Canon.title)
    return {'request': request,
            'canons': canons,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='view_canon', renderer='templates/view_canon.pt', permission='view')
def view_canon(context, request):
    datatables.need()
    try:
        canon = DBSession().query(Canon).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    if not canon:
        raise HTTPNotFound
    return {'request': request,
            'canon': canon,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='list_books', renderer='templates/list_books.pt', permission='view')
def list_books(context, request):
    datatables.need()
    books = DBSession().query(Book).order_by(Book.title)
    return {'request': request,
            'books': books,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='my_books', renderer='templates/my_books.pt', permission='view')
def my_books(context, request):
    datatables.need()
    groups = request.user.groups
    return {'request': request,
            'groups': groups,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='view_book', renderer='templates/view_book.pt', permission='view')
def view_book(context, request):
    try:
        book = DBSession().query(Book).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    if not book:
        raise HTTPNotFound
    return {'request': request,
            'book': book,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='list_groups', renderer='templates/list_groups.pt', permission='view')
def list_groups(context, request):
    datatables.need()
    groups = DBSession().query(Group).order_by(Group.name)
    return {'request': request,
            'groups': groups,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='my_groups', renderer='templates/my_groups.pt', permission='view')
def my_groups(context, request):
    groups = request.user.groups
    return {'request': request,
            'groups': groups,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='view_group', renderer='templates/view_group.pt', permission='view')
def view_group(context, request):
    try:
        group = DBSession().query(Group).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    if not group:
        raise HTTPNotFound
    return {'request': request,
            'group': group,
            'main' : get_renderer('templates/master.pt').implementation()}


@view_config(route_name='logo_group', permission='view')
def logo_group(context, request):
    try:
        group = DBSession().query(Group).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    if not group:
        raise HTTPNotFound
    logo = group.logo 
    return Response(headerlist=[('Content-Disposition', '%s;filename="%s"' % (
                                    'inline', logo.filename.encode('ascii', 'ignore'))),
                                ('Content-Length', str(logo.size)),
                                ('Content-Type', str(logo.mimetype)),],
                    app_iter=logo.data,)


@view_config(route_name='join_group', permission='view')
def join_group(context, request):
    try:
        group = DBSession().query(Group).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    if not group:
        raise HTTPNotFound

    group.add_member(request.user, 'member')
    request.session.flash({'title':u'Gotowe!','body': u'Zostałeś członkiem grupy %s.' % group.name},queue='success')
    return HTTPFound(location = '/groups/%s' % group.id)
