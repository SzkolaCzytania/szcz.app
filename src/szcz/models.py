from sqlalchemy import Column, Text, String, Integer, Boolean, ForeignKey, Table, DateTime, LargeBinary, Unicode
from sqlalchemy.orm import relationship, backref, mapper
from szcz import Base


class User(Base):
    __tablename__ = 'users'
    email = Column(String, primary_key=True)
    given_name = Column(Text)
    family_name = Column(Text)
    address = Column(Text)
    age = Column(Integer)
    sex = Column(String)
    terms = Column(Boolean, default=False)

    @property
    def fullname(self):
        return '%s %s' % (self.given_name, self.family_name)


class File(Base):
    __tablename__ = 'related_files'
    file_id = Column('id', Integer, primary_key=True)
    data = Column(LargeBinary())
    filename = Column(Unicode(100))
    mimetype = Column(String(100))
    size = Column(Integer())


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
                             backref=backref("source",remote_side=[relations.c.source_id]))
    __mapper_args__ = {'polymorphic_identity': 'content', 'polymorphic_on': object_type}

mapper(Relation, relations, 
       properties = {'target': relationship(Content, uselist=False,
                                            primaryjoin=Content.content_id==relations.c.target_id)})


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
        return [r.target for r in self.relations if r.relationship=='book_author']


class Person(Content):
    __tablename__ = 'person'
    __mapper_args__ = {'polymorphic_identity': 'PersonPeer',
                       'polymorphic_on': Content.object_type}
    content_id = Column(Integer, ForeignKey('content.content_id'), primary_key=True)
    biography = Column(Text)
    years = Column(Text)


group_members = Table("group_members", Base.metadata,
                      Column("group_id", Integer, ForeignKey('groups.id'), primary_key=True),
                      Column("user_id", Integer, ForeignKey('users.email'), primary_key=True),
                      Column("membership", String(128), primary_key=True))


group_books = Table("group_books", Base.metadata,
                      Column("group_id", Integer, ForeignKey('groups.id'), primary_key=True),
                      Column("book_id", Integer, ForeignKey('book.content_id'), primary_key=True))


class Group(Base):
    __tablename__ = 'groups'
    group_id = Column('id', Integer, primary_key=True)
    name = Column(Text)
    logo_id = Column(Integer, ForeignKey('related_files.id'))
    logo = relationship(File, uselist=False)
    address = Column(Text)
    members = relationship(User, secondaryjoin=group_members)
    books = relationship(Book, secondaryjoin=group_books)
    end_date = Column(DateTime)
