from sqlalchemy import Column, Text, String, Integer, Boolean, ForeignKey, Table, DateTime
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


##################
# CONTENT-MIRROR #
##################

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
