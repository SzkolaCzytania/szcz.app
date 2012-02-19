from pyramid.security import Allow, Authenticated
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.exc import SQLAlchemyError

from szcz.resources import szcz, datatables
from szcz.models import Book
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


@view_config(route_name='books', renderer='templates/list_books.pt', permission='view')
def all_books(context, request):
    datatables.need()
    books = DBSession().query(Book).order_by(Book.title)
    return {'request': request,
            'books': books,
            'main' : get_renderer('templates/master.pt').implementation()}

@view_config(route_name='book', renderer='templates/view_book.pt', permission='view')
def view_book(context, request):
    try:
        book = DBSession().query(Book).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    return {'request': request,
            'book': book,
            'main' : get_renderer('templates/master.pt').implementation()}
