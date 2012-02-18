from pyramid.security import Allow, Authenticated
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from szcz.resources import szcz


class Context(object):
    """  Default context factory. """

    __acl__ = [(Allow, Authenticated, 'view'),
               (Allow, Authenticated, 'user_profile'),]

    def __init__(self, request):
        szcz.need()
        self.request = request


@view_config(route_name='home', renderer='templates/home.pt', permission='view')
def logged_in(context, request):
    return {'request': request,
            'main' :  get_renderer('templates/master.pt').implementation()}

