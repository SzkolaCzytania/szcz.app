# -*- coding: utf-8 -*-
import deform
import colander
import datetime

from pyramid.view import view_config
from pyramid_deform import SessionFileUploadTempStore
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from fanstaticdeform import deform_resource
from sqlalchemy.exc import SQLAlchemyError
from szcz.models import Group, File
from szcz import DBSession


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4] and self.__dict__[k] != None])


def filesize_validator(node, value):
    value['fp'].seek(0,2)
    if value['fp'].tell() > 50*1024:
        raise colander.Invalid(node, u'Maksymalny rozmiar pliku to 50kB.')


def merge_session_with_post(session, post):
    if not isinstance(post, dict):
        return None
    for key, value in post.items():
        setattr(session, key, value)
    return session


@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = SessionFileUploadTempStore(request)
    return deform.widget.FileUploadWidget(tmpstore)


class UserSchema(colander.Schema):

    SEX = ((u'male', u'Mężczyzna'), (u'female', u'Kobieta'))

    given_name = colander.SchemaNode(colander.String(), title=u'Imię')
    family_name = colander.SchemaNode(colander.String(), title=u'Nazwisko')
    profile = colander.SchemaNode(deform.schema.FileData(), title=u'Zdjęcie',
                                  validator = filesize_validator,
                                  missing = None,
                                  widget = upload_widget,)
    address = colander.SchemaNode(colander.String(),
                                  widget=deform.widget.TextAreaWidget(rows=4, cols=60),
                                  title=u'Adres pocztowy')
    birth = colander.SchemaNode(colander.Date(),
                                validator=colander.Range(min=datetime.date.min,
                                                         max=(datetime.date.today() - datetime.timedelta(18 * 365))),
                                title=u'Data urodzenia')
    sex = colander.SchemaNode(colander.String(),
                              validator=colander.OneOf([x[0] for x in SEX]),
                              widget=deform.widget.RadioChoiceWidget(values=SEX),
                              title=u'Płeć')
    terms = colander.SchemaNode(colander.Boolean(), title=u'Regulamin')


@view_config(route_name='userprofile', renderer='templates/userprofile.pt', permission='user_profile')
def userprofile(context, request):
    user = request.user
    schema = UserSchema().bind(request=request)
    form = deform.Form(schema, buttons=('zapisz', 'anuluj'), css_class=u'form-horizontal')
    deform_resource.needsFor(form)
    form['terms'].widget.template = 'szcz_terms'

    if request.POST:
        if not 'zapisz' in request.POST:
            return HTTPFound(location='/')

        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            return {'form': e.render(),
                    'main':  get_renderer('templates/master.pt').implementation()}

        if appstruct['profile']:
            profile = File()
            profile.filename = appstruct['profile']['filename']
            profile.mimetype = appstruct['profile']['mimetype']
            appstruct['profile']['fp'].seek(0)
            profile.data = appstruct['profile']['fp'].read()
            appstruct['profile']['fp'].seek(0,2)
            profile.size = appstruct['profile']['fp'].tell()
            appstruct['profile']['fp'].close()
            appstruct['profile'] = profile

        user = merge_session_with_post(user, appstruct)
        request.session.flash({'title': u'Gotowe!',
                                'body': u'Aktualizacja profilu zakończyła się sukcesem.'},
                                queue='success')
        return HTTPFound(location='/')

    appstruct = record_to_appstruct(user)
    return {'form': form.render(appstruct=appstruct),
            'main': get_renderer('templates/master.pt').implementation()}


@colander.deferred
def deferred_activation_validator(node, kw):

    class CheckUuid(object):
        def __init__(self, group):
            self.group = group

        def __call__(self, node, value):
            if value != self.group.activation:
                raise colander.Invalid(node, u'Zły kod aktywacyjny')

    return CheckUuid(kw['group'])


class GroupSchema(colander.Schema):
    name = colander.SchemaNode(colander.String(), title=u'Nazwa',
                               description='Pełna nazwa grupy')
    logo = colander.SchemaNode(deform.schema.FileData(), title=u'Logo',
                               validator = filesize_validator,
                               missing = None,
                               widget = upload_widget,)

    address = colander.SchemaNode(colander.String(), title=u'Adres')
    zip_code = colander.SchemaNode(colander.String(), title=u'Kod pocztowy')
    city = colander.SchemaNode(colander.String(), title=u'Miejscowość')
    end_date = colander.SchemaNode(colander.Date(),
                                   description='Minimum 1 miesiąc, maksymalnie 1 rok.',
                                   validator=colander.Range(min=(datetime.date.today() + datetime.timedelta(30)),
                                                            max=(datetime.date.today() + datetime.timedelta(365))),
                                   title=u'Data ważności grupy')
    activation_code = colander.SchemaNode(colander.String(), missing=colander.null,
                                          validator=deferred_activation_validator,
                                          title=u'Kod aktywacyjny')


class ManageGroupMembers(colander.Schema):

    class Sequence(colander.SequenceSchema):
        email = colander.SchemaNode(colander.String(),
                                    title = u'adres email',
                                    validator=colander.Email())
    emails = Sequence(title=u'Adresy email')


def maybe_remove_fields(node, kw):
    if kw['group'].state != u'w trakcie aktywacji':
        del node['activation_code']
    if kw['group'].state == u'w trakcie aktywacji':
        del node['address']
        del node['zip_code']
        del node['city']
        del node['end_date']


@view_config(route_name='manage_group_members', renderer='templates/manage_group_members.pt', permission='edit')
def manage_group_members(context, request):
    try:
        group = DBSession().query(Group).get(request.matchdict.get('id'))
    except SQLAlchemyError:
        raise HTTPNotFound
    if not group:
        raise HTTPNotFound

    schema = ManageGroupMembers().bind(request=request, group=group)
    form = deform.Form(schema, buttons=(u'zaproś', 'anuluj'), css_class=u'')
    form['emails'].widget = deform.widget.SequenceWidget(min_len=1)
    deform_resource.needsFor(form)

    if request.POST:
        if not u'zaproś' in request.POST:
            return HTTPFound(location='/groups/%s' % group.id)
        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            return {'form': e.render(),
                    'group_nav':  get_renderer('templates/group_macros.pt').implementation(),
                    'group': group,
                    'main':  get_renderer('templates/master.pt').implementation()}


        emails = set(appstruct.get('emails'))
        user = request.user
        for email in emails:
            mailer = get_mailer(request)
            message = Message(subject=u"Prośba o dołączenie do grupy %s" % group.name,
                              sender=user.email,
                              recipients=["%s" % email],
                              body=u"""%s chce abyś dołączył do grupy %s w serwisie Szkoła Czytania.
Aby zaakceptować zaproszenie przejdź do adresu: %s/groups/%s/join""" % (
                                        user.fullname, group.name, request.application_url, group.id))
            mailer.send_to_queue(message)

        request.session.flash({'title': u'Gotowe!',
                               'body': u'Zaproszenia zostały wysłane do: %s' % (','.join(emails))},
                               queue='success')
        return HTTPFound(location='/groups/%s' % group.id)

    return {'form': form.render(),
            'group': group,
            'group_nav':  get_renderer('templates/group_macros.pt').implementation(),
            'main': get_renderer('templates/master.pt').implementation()}


@view_config(route_name='edit_group', renderer='templates/edit_group.pt', permission='edit')
@view_config(route_name='add_group', renderer='templates/add_group.pt', permission='view')
def edit_group(context, request):
    if 'id' in request.matchdict:
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
    form = deform.Form(schema, buttons=('zapisz', 'anuluj'), css_class=u'form-horizontal')
    deform_resource.needsFor(form)

    if request.POST:
        if not 'zapisz' in request.POST:
            return HTTPFound(location='/groups/only_mine')
        items = request.POST.items()
        try:
            appstruct = form.validate(items)
        except deform.ValidationFailure, e:
            return {'form': e.render(),
                    'group_nav':  get_renderer('templates/group_macros.pt').implementation(),
                    'group': group,
                    'main':  get_renderer('templates/master.pt').implementation()}

        if appstruct['logo']:
            logo = File()
            logo.filename = appstruct['logo']['filename']
            logo.mimetype = appstruct['logo']['mimetype']
            appstruct['logo']['fp'].seek(0)
            logo.data = appstruct['logo']['fp'].read()
            appstruct['logo']['fp'].seek(0,2)
            logo.size = appstruct['logo']['fp'].tell()
            appstruct['logo']['fp'].close()
            appstruct['logo'] = logo
        if 'activation_code' in request.POST:
            group.state = u'aktywna'
            request.session.flash({'title': u'Gotowe!',
                                    'body': u'Grupa %s została aktywowana.' % group.name},
                                    queue='success')
            return HTTPFound(location='/groups/%s' % group.id)

        group = merge_session_with_post(group, appstruct)
        group.add_member(request.user, 'owner')
        session = DBSession()
        session.add(group)
        if is_new:
            request.session.flash({'title': u'Gotowe!',
                                    'body': u'Grupa %s została stworzona.' % group.name},
                                    queue='success')
        else:
            request.session.flash({'title': u'Gotowe!',
                                    'body': u'Grupa %s została zaktualizowana.' % group.name},
                                    queue='success')
        return HTTPFound(location='/groups/only_mine')

    appstruct = record_to_appstruct(group)
    return {'form': form.render(appstruct=appstruct),
            'group': group,
            'group_nav':  get_renderer('templates/group_macros.pt').implementation(),
            'main': get_renderer('templates/master.pt').implementation()}
