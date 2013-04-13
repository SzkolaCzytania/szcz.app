# -*- coding: utf-8 -*-
import os
from pyramid.response import FileResponse
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.exc import SQLAlchemyError
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Authenticated
from szcz.resources import szcz
from szcz.models import Book, Canon
from szcz import DBSession
from szcz.resources import datatables


class Context(object):
    """  Default context factory. """
    __acl__ = [(Allow, 'group:activated_users', 'view'),
               (Allow, Authenticated, 'user_profile'),
               (Allow, 'group:administrator', ALL_PERMISSIONS),
               ]

    def __init__(self, request):
        szcz.need()
        self.request = request

@view_config(route_name='favicon')
def favicon_view(request):
    here = os.path.dirname(__file__)
    icon = os.path.join(here, 'resources/img/', 'favicon.ico')
    return FileResponse(icon, request=request)


@view_config(context='pyramid.httpexceptions.HTTPNotFound', renderer='templates/notfound.pt')
def notfound(request):
    request.response.status_int = 404
    return {'request': request,
            'main':  get_renderer('templates/master.pt').implementation()}


@view_config(route_name='home', renderer='templates/home.pt', permission='view')
def home(context, request):
    return {'request': request,
            'main':  get_renderer('templates/master.pt').implementation()}


@view_config(route_name='list_canons', renderer='templates/list_canons.pt', permission='view')
def list_canons(context, request):
    datatables.need()
    canons = DBSession().query(Canon).order_by(Canon.title)
    return {'request': request,
            'canons': canons,
            'main': get_renderer('templates/master.pt').implementation()}


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
            'main': get_renderer('templates/master.pt').implementation()}


@view_config(route_name='list_books', renderer='templates/list_books.pt', permission='view')
def list_books(context, request):
    datatables.need()
    books = DBSession().query(Book).order_by(Book.title)
    return {'request': request,
            'books': books,
            'main': get_renderer('templates/master.pt').implementation()}


@view_config(route_name='my_books', renderer='templates/my_books.pt', permission='view')
def my_books(context, request):
    datatables.need()
    groups = request.user.groups
    return {'request': request,
            'groups': groups,
            'main': get_renderer('templates/master.pt').implementation()}


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
            'main': get_renderer('templates/master.pt').implementation()}
