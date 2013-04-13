from sqlalchemy import Column, Text, String, Integer, Boolean, ForeignKey, Table, DateTime, LargeBinary, Unicode, Date
from sqlalchemy.orm import relationship, backref, mapper
from zope.interface import implements
import uuid
from szcz import Base, interfaces


class File(Base):
    __tablename__ = 'related_files'
    id = Column('id', Integer, primary_key=True)
    data = Column(LargeBinary())
    filename = Column(Unicode(100))
    mimetype = Column(String(100))
    size = Column(Integer())


class User(Base):
    __tablename__ = 'users'
    email = Column(String, primary_key=True)
    profile_id = Column(Integer, ForeignKey('related_files.id'))
    profile = relationship(File, uselist=False)
    given_name = Column(Text)
    family_name = Column(Text)
    address = Column(Text)
    birth = Column(Date)
    sex = Column(String)
    terms = Column(Boolean, default=False)

    @property
    def fullname(self):
        return '%s %s' % (self.given_name, self.family_name)

    def list_my_books(self):
        for membership in self.groups:
            for book in membership.group.books:
                yield book

    def isActivated(self):
        if self.given_name and \
           self.family_name and \
           self.address and \
           self.birth and \
           self.sex and \
           self.terms:
            return True
        else:
            return False


relations = Table("relations", Base.metadata,
                  Column("source_id", Integer, ForeignKey('content.content_id'), primary_key=True),
                  Column("target_id", Integer, ForeignKey('content.content_id'), primary_key=True),
                  Column("relationship", String(128), primary_key=True))


class Relation(object):
    def __init__(self, source=None, target=None, relation=None):
        self.source = source
        self.target = target
        self.relationship = relation


class Content(Base):
    __tablename__ = 'content'
    content_id = Column(Integer, primary_key=True)
    content_uid = Column(String(36), nullable=False)
    object_type = Column(String(64))
    object_type = Column(String(64))
    status = Column(String(64))
    portal_type = Column(String(64))
    path = Column(Text)
    title = Column(Text)
    description = Column(Text)
    subject = Column(Text)
    creators = Column(Text)
    creation_date = Column(DateTime)
    modification_date = Column(DateTime)
    relations = relationship(Relation,
                             primaryjoin=('content.c.content_id==relations.c.source_id'),
                             backref=backref("source", remote_side=[relations.c.source_id]))
    __mapper_args__ = {'polymorphic_identity': 'content', 'polymorphic_on': object_type}

mapper(Relation, relations,
       properties={'target': relationship(Content, uselist=False,
                   primaryjoin=Content.content_id == relations.c.target_id)})


class Book(Content):
    __tablename__ = 'book'
    __mapper_args__ = {'polymorphic_identity': 'BookPeer',
                       'polymorphic_on': Content.object_type}
    content_id = Column(Integer, ForeignKey('content.content_id'), primary_key=True)
    pages = Column(Text)
    publisher = Column(Text)
    address = Column(Text)
    isbn = Column(Text)

    def authors(self):
        return [r.target for r in self.relations if r.relationship == 'book_author']


class Canon(Content):
    __tablename__ = 'canon'
    __mapper_args__ = {'polymorphic_identity': 'CanonPeer',
                       'polymorphic_on': Content.object_type}
    content_id = Column(Integer, ForeignKey('content.content_id'), primary_key=True)
    text = Column(Text)

    def books(self):
        books = [r.target for r in self.relations if r.relationship == 'canon_book']
        return sorted(books, key=lambda book: book.title)

    def authors(self):
        return [r.target for r in self.relations if r.relationship == 'canon_author']


class Author(Content):
    __tablename__ = 'person'
    __mapper_args__ = {'polymorphic_identity': 'PersonPeer',
                       'polymorphic_on': Content.object_type}
    content_id = Column(Integer, ForeignKey('content.content_id'), primary_key=True)
    biography = Column(Text)
    years = Column(Text)


group_books = Table("group_books", Base.metadata,
                    Column("group_id", Integer, ForeignKey('groups.id'), primary_key=True),
                    Column("book_id", Integer, ForeignKey('book.content_id'), primary_key=True))


class GroupMember(Base):
    implements(interfaces.IGroupMembership)

    __tablename__ = "group_members"
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    user_id = Column(String, ForeignKey('users.email'), primary_key=True)
    membership = Column(String(128))
    user = relationship(User, uselist=False, backref='groups')
    state = Column(String(64), default='nieaktywny')

    @property
    def state_css(self):
        if self.state == 'aktywny':
            return 'btn-success'
        else:
            return 'btn-danger'


class Group(Base):
    implements(interfaces.IGroup)

    __tablename__ = 'groups'
    id = Column('id', Integer, primary_key=True)
    name = Column(Text)
    logo_id = Column(Integer, ForeignKey('related_files.id'))
    logo = relationship(File, uselist=False)
    address = Column(Text)
    city = Column(Text)
    zip_code = Column(Text)
    members = relationship(GroupMember, backref='group')
    books = relationship(Book, secondary=group_books)
    end_date = Column(Date)
    state = Column(String(64), default='nieaktywna')
    activation = Column(String(36))

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.activation = str(uuid.uuid1())

    @property
    def full_address(self):
        return "%s, %s %s" % (self.address, self.zip_code, self.city)

    @property
    def printable_address(self):
        return "%s<br /> %s %s" % (self.address, self.zip_code, self.city)

    def add_book(self, book):
        if [b for b in self.books if b.content_id == book.content_id]:
            return
        self.books.append(book)

    def add_member(self, user, membership):
        if [u for u in self.members if u.user.email == user.email]:
            return
        group_membership = GroupMember(membership=membership)
        group_membership.user = user
        if membership == 'owner':
            group_membership.state = u'aktywny'
        self.members.append(group_membership)

    def get_owner(self):
        return [m.user for m in self.members if m.membership == 'owner'][0]

    @property
    def state_css(self):
        if self.state == 'aktywna':
            return 'label label-success'
        elif self.state == 'zablokowana':
            return 'label label-important'
        else:
            return 'label'
