import deform
import colander
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from fanstaticdeform import deform_req


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]])


def merge_session_with_post(session, post):
    for key,value in post:
        setattr(session, key, value)
    return session


class UserSchema(colander.Schema):
    given_name = colander.SchemaNode(colander.String())
    family_name = colander.SchemaNode(colander.String())


@view_config(route_name='userprofile', renderer='templates/userprofile.pt', permission='user_profile')
def usercreate(context, request):
    deform_req.need()

    user = request.user
    schema = UserSchema()
    form = deform.Form(schema, buttons=('submit','cancel'), css_class=u'form-horizontal')

    if request.POST:
        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            return {'form': e.render(),
                    'main':  get_renderer('templates/master.pt').implementation(),}

        user = merge_session_with_post(user, items)
        return HTTPFound(location = '/')

    appstruct = record_to_appstruct(user)
    return {'form':form.render(appstruct=appstruct),
            'main':  get_renderer('templates/master.pt').implementation(),}
