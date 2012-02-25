# -*- coding: utf-8 -*-
import deform
import colander
from cStringIO import StringIO
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from fanstaticdeform import deform_resource
from sqlalchemy.exc import SQLAlchemyError
from repoze.workflow import WorkflowError
from szcz.models import Group#, File
from szcz import DBSession


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4] and self.__dict__[k] != None])


def merge_session_with_post(session, post):
    if not isinstance(post, dict):
        return None
    for key,value in post.items():
        setattr(session, key, value)
    return session


class FileUploadTempStore(object):

    def __init__(self, request):
        self.request = request
        self.session = request.session

    def __setitem__(self, name, value):
        pickleable = value.copy()
        fp = pickleable.get('fp', None)
        if fp is not None:
            pickleable['fp'] = fp.read()
        return self.session.__setitem__(name, pickleable)

    def __getitem__(self, name):
        if name in self.session:
            sessiondata = self.session['name']
            filedata = {}
            for (key, value) in sessiondata:
                if ((key == 'fp') and (value is not None)):
                    # translate the file data back into a file
                    # like object
                    value = StringIO(value)
                    filedata[key] = value
            return filedata
        raise KeyError('"%s" not in session' % name)

    def __delitem__(self, name):
        del self.session[name]

    def __contains__(self, name):
        return (name in self.session)

    def get(self, name, default=None):
        try:
            self.__getitem__(name)
        except:
            return default

    def preview_url(self, name):
        return None


@colander.deferred
def deferred_fileupload_widget(node, kw):
    tmpstore = FileUploadTempStore(kw['request'])
    return deform.widget.FileUploadWidget(tmpstore)


class UserSchema(colander.Schema):

    SEX = ((u'male',u'Mężczyzna'),(u'female',u'Kobieta'))

    given_name = colander.SchemaNode(colander.String(), title=u'Imię')
    family_name = colander.SchemaNode(colander.String(), title=u'Nazwisko')
    address = colander.SchemaNode(colander.String(),
                                  widget=deform.widget.TextAreaWidget(rows=4, cols=60),
                                  title=u'Adres pocztowy')
    age = colander.SchemaNode(colander.Integer(), title=u'Wiek')
    sex = colander.SchemaNode(colander.String(),
                              validator=colander.OneOf([x[0] for x in SEX]),
                              widget=deform.widget.RadioChoiceWidget(values=SEX),
                              title=u'Płeć')
    terms = colander.SchemaNode(colander.Boolean(), title=u'Regulamin')


@view_config(route_name='userprofile', renderer='templates/userprofile.pt', permission='user_profile')
def userprofile(context, request):
    user = request.user
    schema = UserSchema()
    form = deform.Form(schema, buttons=('zapisz','anuluj'), css_class=u'form-horizontal')
    deform_resource.needsFor(form)
    form['terms'].widget.template = 'szcz_terms'

    if request.POST:
        if not 'zapisz' in request.POST:
            return HTTPFound(location = '/')

        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            request.session.flash({'title':u'Błędy','body': u'Popraw zaznaczone błędy'},queue='error')
            return {'form': e.render(),
                    'main':  get_renderer('templates/master.pt').implementation(),}

        user = merge_session_with_post(user, appstruct)
        request.session.flash({'title':u'Gotowe!','body': u'Aktualizacja profilu zakończyła się sukcesem.'},queue='success')
        return HTTPFound(location = '/')

    appstruct = record_to_appstruct(user)
    return {'form':form.render(appstruct=appstruct),
            'main':  get_renderer('templates/master.pt').implementation(),}


@colander.deferred
def deferred_activation_validator(node, kw):
    """BBB: to be finished """
    return colander.OneOf(['123456789','abcdefghijk'])


class GroupSchema(colander.Schema):
    name = colander.SchemaNode(colander.String(), title=u'Nazwa')
#    logo = colander.SchemaNode(deform.FileData(),
#                               missing = colander.null,
#                               widget=deferred_fileupload_widget)
    address = colander.SchemaNode(colander.String(), title=u'Adres')
    zip_code = colander.SchemaNode(colander.String(), title=u'Kod pocztowy')
    city = colander.SchemaNode(colander.String(), title=u'Miejscowość')
    end_date = colander.SchemaNode(colander.Date(), title=u'Data ważności grupy')
    activation_code = colander.SchemaNode(colander.String(), missing=colander.null,
                                          validator=deferred_activation_validator,
                                          title=u'Kod aktywacyjny')


def maybe_remove_fields(node, kw):
    if kw['group'].state != u'w trakcie aktywacji':
        del node['activation_code']
    if kw['group'].state == u'w trakcie aktywacji':
        del node['address']
        del node['zip_code']
        del node['city']
        del node['end_date']


@view_config(route_name='edit_group', renderer='templates/edit_group.pt', permission='edit')
@view_config(route_name='add_group', renderer='templates/add_group.pt', permission='view')
def add_group(context, request):

    if request.matchdict.has_key('id'):
        try:
            group = DBSession().query(Group).get(request.matchdict.get('id'))
            is_new = False
        except SQLAlchemyError:
            raise HTTPNotFound
        if not group:
            raise HTTPNotFound
    else:
        group = Group()
        is_new = True

    schema = GroupSchema(after_bind=maybe_remove_fields).bind(request=request, group=group)
    form = deform.Form(schema, buttons=('zapisz','anuluj'), css_class=u'form-horizontal')
    deform_resource.needsFor(form)

    if request.POST:
        if not 'zapisz' in request.POST:
            return HTTPFound(location = '/groups/only_mine')
        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            request.session.flash({'title':u'Błędy','body': u'Popraw zaznaczone błędy'},queue='error')
            return {'form': e.render(),
                    'group_nav':  get_renderer('templates/group_macros.pt').implementation(),
                    'group': group,
                    'main':  get_renderer('templates/master.pt').implementation(),}

#        logo = merge_session_with_post(File(),appstruct.pop('logo'))
#        if logo:
#            logo.fp.seek(0)
#            data = logo.fp.read()
#            logo.data = data
#            logo.size = len(data)

        if 'activation_code' in request.POST:
            group.state = u'aktywna'
            request.session.flash({'title':u'Gotowe!','body': u'Grupa %s została aktywowana.' % group.name},queue='success')
            return HTTPFound(location = '/groups/%s' % group.id)

        group = merge_session_with_post(group, appstruct)
        group.add_member(request.user, 'owner')
        session = DBSession()
        session.add(group)
        if is_new:
            request.session.flash({'title':u'Gotowe!','body': u'Grupa %s została stworzona.' % group.name},queue='success')
        else:
            request.session.flash({'title':u'Gotowe!','body': u'Grupa %s została zaktualizowana.' % group.name},queue='success')
        return HTTPFound(location = '/groups/only_mine')


    appstruct = record_to_appstruct(group)
    return {'form':form.render(appstruct=appstruct),
            'group': group,
            'group_nav':  get_renderer('templates/group_macros.pt').implementation(),
            'main':  get_renderer('templates/master.pt').implementation(),}

