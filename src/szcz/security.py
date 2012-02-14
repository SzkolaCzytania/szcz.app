from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.security import unauthenticated_userid
from pyramid.renderers import get_renderer
from fanstaticdeform import deform_req
from szcz.models import User, DBSession
import deform
import colander


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
        request.session['profile'] = context.profile
        return HTTPFound(location='/usercreate')
    return login_success(user, request)


def login_success(user, request):
    headers = remember(request, user.email)
    return HTTPFound(location='/', headers=headers)


@view_config(route_name='usercreate', renderer='templates/usercreate.pt')
def usercreate(context, request):
    session = DBSession()
    deform_req.need()
    profile = request.session.get('profile')
    schema = UserSchema()
    user = User(given_name = profile['name']['givenName'],
                family_name = profile['name']['familyName'],
                email = profile.get('verifiedEmail'))

    form = deform.Form(schema, buttons=('submit','cancel'), css_class=u'form-horizontal')
    form['email'].widget.template = form['email'].widget.readonly_template

    if request.POST:
        items = request.POST.items()
        items.append(('email', profile.get('verifiedEmail')))
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            return {'form': e.render(),
                    'main':  get_renderer('templates/master.pt').implementation(),}

        user = merge_session_with_post(user, items)
        session.add(user)
        del request.session['profile']
        return login_success(user, request)

    appstruct = record_to_appstruct(user)
    return {'form':form.render(appstruct=appstruct),
            'main':  get_renderer('templates/master.pt').implementation(),}


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]])


def merge_session_with_post(session, post):
    for key,value in post:
        setattr(session, key, value)
    return session


class UserSchema(colander.Schema):
    email = colander.SchemaNode(colander.String())
    given_name = colander.SchemaNode(colander.String())
    family_name = colander.SchemaNode(colander.String())

