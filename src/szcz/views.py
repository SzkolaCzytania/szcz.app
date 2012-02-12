from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from szcz.resources import szcz, library
from szcz.models import User, DBSession
import fanstatic


class Context(object):
    """  Default context factory. """
    def __init__(self, request):
        szcz.need()
        self.request = request


@view_config(route_name='home', renderer='templates/login_form.pt')
def home(request):
    needed = fanstatic.get_needed()
    szcz_url = needed.library_url(library)
    return {'szcz_url': szcz_url,
            'request': request}


@view_config(context='velruse.api.AuthenticationComplete', renderer='templates/home.pt')
def success(context, request):
    email = context.profile.get('verifiedEmail')
    user = DBSession.query(User).get(email)
    if not user:
        user = autoregister(context.profile)
    request.session['user'] = user
    return HTTPFound(location='/logged_in')


@view_config(route_name='logged_in', renderer='templates/home.pt')
def logged_in(context, request):
    return {'request': request,
            'fullname': request.session.get('user').fullname}


def autoregister(profile):
    session = DBSession()
    user = User(given_name = profile['name']['givenName'],
                family_name = profile['name']['familyName'],
                email = profile.get('verifiedEmail'))
    session.add(user)
    return user
