from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from fanstaticdeform import deform_req
from szcz.resources import szcz, library
from szcz.models import User, DBSession
import fanstatic
import deform
import colander


class Context(object):
    """  Default context factory. """
    def __init__(self, request):
        szcz.need()
        self.request = request


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]])


def merge_session_with_post(session, post):
    for key,value in post:
        setattr(session, key, value)
    return session


@view_config(route_name='login_form', renderer='templates/login_form.pt')
def login_form(request):
    needed = fanstatic.get_needed()
    szcz_url = needed.library_url(library)
    return {'szcz_url': szcz_url,
            'request': request}


@view_config(context='velruse.api.AuthenticationComplete', renderer='templates/home.pt')
def success(context, request):
    email = context.profile.get('verifiedEmail')
    user = DBSession.query(User).get(email)
    if not user:
        request.session['profile'] = context.profile
        return HTTPFound(location='/usercreate')
    request.session['fullname'] = user.fullname
    return HTTPFound(location='/logged_in')


@view_config(route_name='logged_in', renderer='templates/home.pt')
def logged_in(context, request):
    return {'request': request,
            'fullname': request.session.get('fullname')}


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
            return {'form':e.render()}

        user = merge_session_with_post(user, items)
        session.add(user)
        request.session['fullname'] = user.fullname
        del request.session['profile']
        return HTTPFound(location='/logged_in')

    appstruct = record_to_appstruct(user)
    return {'form':form.render(appstruct=appstruct)}


class UserSchema(colander.Schema):
    email = colander.SchemaNode(colander.String())
    given_name = colander.SchemaNode(colander.String())
    family_name = colander.SchemaNode(colander.String())

