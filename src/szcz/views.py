from pyramid.view import view_config
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.response import Response
from szcz.resources import szcz, library
import fanstatic


session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')


class Context(object):
    """
    Default context factory.
    """

    def __init__(self, request):
        szcz.need()
        self.request = request


@view_config(route_name='home', renderer='templates/home.pt')
def my_view(request):
    needed = fanstatic.get_needed()
    szcz_url = needed.library_url(library)
    return {'szcz_url': szcz_url,
            'request': request}


@view_config(context='velruse.api.AuthenticationComplete')
def success(context, request):
    return Response(str({'profile': context.profile,
                     'credentials': context.credentials,}))
