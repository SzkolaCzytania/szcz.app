# -*- coding: utf-8 -*-
import deform
import colander
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from fanstaticdeform import deform_req


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4] and self.__dict__[k] != None])


def merge_session_with_post(session, post):
    for key,value in post.items():
        setattr(session, key, value)
    return session


class UserSchema(colander.Schema):

    SEX = ((u'male',u'Mężczyzna'),(u'female',u'Kobieta'))

    given_name = colander.SchemaNode(colander.String(),
                                     title=u'Imię')
    family_name = colander.SchemaNode(colander.String(),
                                      title=u'Nazwisko')
    address = colander.SchemaNode(colander.String(),
                                  widget=deform.widget.TextAreaWidget(rows=4, cols=60),
                                  title=u'Adres pocztowy')
    age = colander.SchemaNode(colander.Integer(),
                              title=u'Wiek')
    sex = colander.SchemaNode(colander.String(),
                              validator=colander.OneOf([x[0] for x in SEX]),
                              widget=deform.widget.RadioChoiceWidget(values=SEX),
                              title=u'Płeć')
    terms = colander.SchemaNode(colander.Boolean(),
                                title=u'Regulamin')


@view_config(route_name='userprofile', renderer='templates/userprofile.pt', permission='user_profile')
def usercreate(context, request):
    deform_req.need()

    user = request.user
    schema = UserSchema()
    form = deform.Form(schema, buttons=('submit','cancel'), css_class=u'form-horizontal')
    form['terms'].widget.template = 'szcz_terms'

    if request.POST:
        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            return {'form': e.render(),
                    'main':  get_renderer('templates/master.pt').implementation(),}

        user = merge_session_with_post(user, appstruct)
        return HTTPFound(location = '/')

    appstruct = record_to_appstruct(user)
    return {'form':form.render(appstruct=appstruct),
            'main':  get_renderer('templates/master.pt').implementation(),}
