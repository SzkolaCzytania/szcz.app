# -*- coding: utf-8 -*-
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.response import Response
from pyramid.security import Allow, has_permission
from pyramid.security import ALL_PERMISSIONS
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from sqlalchemy.exc import SQLAlchemyError
from repoze.workflow import WorkflowError
from repoze.workflow import get_workflow
from szcz.models import Group, GroupMember
from szcz import DBSession, views
from szcz.resources import datatables


PRIVATE = ['nieaktywna', 'w trakcie aktywacji', 'w edycji']


class GroupContext(views.Context):
    def __init__(self, request):
        super(GroupContext, self).__init__(request)
        self.__acl__ = [(Allow, 'group:administrator', ALL_PERMISSIONS)]

        if self.is_owner:
            self.__acl__.append((Allow, request.user.email, 'review'))
            if self.group.state in PRIVATE:
                self.__acl__.append((Allow, request.user.email, 'edit'))

        if self.is_member:
            self.__acl__.append((Allow, request.user.email, 'view'))

        if self.group.state not in PRIVATE:
            self.__acl__.append((Allow, 'group:activated_users', 'view'))

    def _get_state(self):
        return self.group.state

    def _set_state(self, value):
        self.group.state = value

    state = property(fget=_get_state, fset=_set_state)

    def _get_membership_state(self):
        return self.group_membership.state

    def _set_membership_state(self, value):
        self.group_membership.state = value

    membership_state = property(fget=_get_membership_state, fset=_set_membership_state)

    @property
    def group(self):
        try:
            group = DBSession().query(Group).get(self.request.matchdict.get('id'))
        except SQLAlchemyError:
            raise HTTPNotFound
        if not group:
            raise HTTPNotFound
        return group

    @property
    def group_membership(self):
        group_id = self.group.id
        email = self.request.matchdict.get('email')
        try:
            membership = DBSession().query(GroupMember).get((group_id, email))
        except SQLAlchemyError:
            raise HTTPNotFound
        if not membership:
            raise HTTPNotFound
        return membership

    @property
    def state_css(self):
        return self.group.state_css

    @property
    def states(self):
        return self.wf and self.wf.get_transitions(self, self.request) or []

    @property
    def wf(self):
        try:
            return get_workflow(self.group, 'GroupWorkflow')
        except WorkflowError:
            return None

    @property
    def is_owner(self):
        for group in self.request.user.groups:
            if group.group_id == self.group.id and group.membership == 'owner':
                return True
        return False

    @property
    def is_member(self):
        for group in self.request.user.groups:
            if group.group_id == self.group.id:
                return True
        return False

    def has_permission(self, perm):
        return has_permission(perm, self, self.request)

    def canBeActivated(self):

        def metadata_check(group):
            if group.name and \
                   group.address and \
                   group.city and \
                   group.zip_code and \
                   group.end_date and \
                   group.activation:
                return True
            else:
                self.request.session.flash({'title': u'Błąd!',
                                             'body': u'Proszę uzupełnić dane grupy.'},
                                            queue='error')
                return False

        def members_check(group):
            if len(group.members) < 2:
                self.request.session.flash({'title': u'Błąd!',
                                             'body': u'Grupa musi mieć minimum 2 uczestników.'},
                                             queue='error')
                return False
            else:
                return True

        def books_check(group):
            if len(group.books) < len(group.members):
                self.request.session.flash({'title': u'Błąd!',
                                             'body': u'Grupa ma więcej uczestników niż książek.'},
                                             queue='error')
                return False
            else:
                return True

        return metadata_check(self.group) and members_check(self.group) and books_check(self.group)


def activate(content, info):
    if not content.canBeActivated():
        raise WorkflowError
    else:
        return send_activation(content, info)


def send_activation(content, info):
    mailer = get_mailer(content.request)
    settings = get_current_registry().settings
    admins = settings.get('szcz.admins').split(',')
    message = Message(subject=u"Prośba o aktywację nowej grupy",
                      recipients=admins,
                      html=u"<a href='%s/groups/%s/edit'>Aktywuj %s</a>" % (content.request.application_url, content.group.id, content.group.name),
                      extra_headers={'X-MC-Template': 'activation-requeset',
                                     'X-MC-MergeVars': '{"MAIN": "%s/groups/%s/edit"}' % (content.request.application_url, content.group.id)})
    mailer.send(message)


def acept(content, info):
    if not content.canBeActivated():
        raise WorkflowError
    else:
        return send_aceptation(content, info)


def send_aceptation(content, info):
    mailer = get_mailer(content.request)
    settings = get_current_registry().settings
    admins = settings.get('szcz.admins').split(',')
    message = Message(subject=u"Prośba o akceptację zmian grupy",
                      recipients=admins,
                      html=u"<a href='%s/groups/%s'>%s</a>" % (content.request.application_url, content.group.id, content.group.name),
                      extra_headers={'X-MC-Template': 'accept-group-changed',
                                     'X-MC-MergeVars': '{"MAIN": "%s/groups/%s"}' % (content.request.application_url, content.group.id)})
    mailer.send(message)


@view_config(route_name='list_groups', renderer='templates/list_groups.pt', permission='view')
def list_groups(context, request):
    datatables.need()
    groups = DBSession().query(Group).filter_by(state=u'aktywna').order_by(Group.name)
    return {'request': request,
            'groups': groups,
            'main': get_renderer('templates/master.pt').implementation()}


@view_config(route_name='my_groups', renderer='templates/my_groups.pt', permission='view')
def my_groups(context, request):
    groups = request.user.groups
    return {'request': request,
            'groups': groups,
            'main': get_renderer('templates/master.pt').implementation()}


@view_config(route_name='view_group', renderer='templates/view_group.pt', permission='view')
def view_group(context, request):
    return {'request': request,
            'group': context.group,
            'group_nav': get_renderer('templates/group_macros.pt').implementation(),
            'main': get_renderer('templates/master.pt').implementation()}


@view_config(route_name='logo_group', permission='view')
def logo_group(context, request):
    logo = context.group.logo
    if not logo:
        raise HTTPNotFound
    return Response(headerlist=[('Content-Disposition', '%s;filename="%s"' % (
                                 'inline', logo.filename.encode('ascii', 'ignore'))),
                                ('Content-Length', str(logo.size)),
                                ('Content-Type', str(logo.mimetype))],
                    app_iter=logo.data,)


@view_config(route_name='wf_group', permission='review', request_param='destination')
def change_group_state(context, request):
    try:
        context.wf.transition_to_state(context, request, request.params.get('destination'), skip_same=False)
    except WorkflowError:
        request.session.flash({'title': u'Błąd!', 'body': u'Nie udało się zmienić statusu.'}, queue='error')
        return HTTPFound(location='/groups/%s' % context.group.id)
    request.session.flash({'title': u'Gotowe!', 'body': u'Status grupy został uaktualniony.'}, queue='success')
    return HTTPFound(location='/groups/%s' % context.group.id)


@view_config(route_name='wf_groupmembership', permission='edit', request_param='destination')
def change_groupmembership_state(context, request):
    try:
        wf = get_workflow(context.group_membership, 'GroupMembershipWorkflow')
    except WorkflowError:
        raise HTTPNotFound
    try:
        wf.transition_to_state(context, request, request.params.get('destination'), skip_same=False)
    except WorkflowError:
        request.session.flash({'title': u'Błąd!', 'body': u'Nie udało się zmienić statusu.'}, queue='error')
        return HTTPFound(location='/groups/%s/manage_group_members' % context.group.id)
    request.session.flash({'title': u'Gotowe!', 'body': u'Status użytkownika został uaktualniony.'}, queue='success')
    return HTTPFound(location='/groups/%s/manage_group_members' % context.group.id)


@view_config(route_name='join_group', permission='view')
def join_group(context, request):
    context.group.add_member(request.user, 'member')
    request.session.flash({'title': u'Gotowe!',
                            'body': u'Zostałeś członkiem grupy %s.' % context.group.name},
                            queue='success')
    return HTTPFound(location='/groups/%s' % context.group.id)
