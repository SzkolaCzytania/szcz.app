# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.security import unauthenticated_userid
from pyramid.renderers import get_renderer, render
from pyramid.response import Response
from velruse import login_url
from szcz.models import User
from szcz import DBSession


def groupfinder(userid, request):
    roles = []
    if request.user and request.user.isActivated():
        roles.append('group:activated_users')
    if userid == u'andrew@mleczko.net':
        roles.append('group:administrator')
    return roles


def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        return DBSession().query(User).get(userid)


@view_config(context='pyramid.httpexceptions.HTTPUnauthorized', renderer='templates/login_form.pt')
def login_form(request):
    return {'request': request,
            'login_url': login_url,
            'main':  get_renderer('templates/master.pt').implementation()}


@view_config(context='pyramid.httpexceptions.HTTPForbidden')
def forbidden(context, request):
    values = {'request': request,
              'login_url': login_url,
              'main':  get_renderer('templates/master.pt').implementation()}
    if request.user:
        result = render('templates/forbidden.pt', values)
        response = Response(result)
        response.code_int = 403
    else:
        result = render('templates/login_form.pt', values)
        response = Response(result)
        response.code_int = 401
    return response


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location='/', headers=headers)


@view_config(context='velruse.AuthenticationComplete')
def velruse_complete(context, request):
    email = context.profile.get('verifiedEmail')
    user = DBSession.query(User).get(email)

    if not user:
        session = DBSession()
        try:
            given_name, family_name = context.profile['displayName'].split(' ')
        except ValueError:
            given_name = context.profile['displayName']
            family_name = context.profile['displayName']
        user = User(given_name=given_name,
                    family_name=family_name,
                    email=context.profile.get('verifiedEmail'))
        session.add(user)
        headers = remember(request, user.email)
        return HTTPFound(location='/profile', headers=headers)

    headers = remember(request, user.email)
    return HTTPFound(location='/', headers=headers)


@view_config(context='velruse.AuthenticationDenied')
def velruse_rejected(context, request):
    request.session.flash({'title': u'Brak autoryzacji',
                            'body': u'Nie zostałeś poprawnie zautoryzowany przez profil zewnętrzny.'},
                            queue='error')
    return HTTPFound(location='/')
