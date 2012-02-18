from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.security import unauthenticated_userid
from pyramid.renderers import get_renderer
from szcz.models import User, DBSession


def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        return DBSession().query(User).get(userid)


@view_config(context='pyramid.httpexceptions.HTTPForbidden', renderer='templates/login_form.pt')
def login_form(request):
    return {'request': request,
            'main':  get_renderer('templates/master.pt').implementation(),}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = '/', headers = headers)


@view_config(context='velruse.api.AuthenticationComplete')
def velruse_complete(context, request):
    email = context.profile.get('verifiedEmail')
    user = DBSession.query(User).get(email)

    if not user:
        session = DBSession()
        user = User(given_name = context.profile['name']['givenName'],
                    family_name = context.profile['name']['familyName'],
                    email = context.profile.get('verifiedEmail'))
        session.add(user)
        headers = remember(request, user.email)
        return HTTPFound(location='/profile', headers=headers)

    headers = remember(request, user.email)
    return HTTPFound(location='/', headers=headers)
