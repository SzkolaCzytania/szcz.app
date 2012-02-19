from sqlalchemy import Column, Text, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, backref, mapper
#from sqlalchemy.ext.declarative import declared_attr
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
    __table_args__ = {'autoload': True, 'extend_existing':True}
    object_type = Column(String(64))
    __mapper_args__ = {'polymorphic_identity': 'content', 'polymorphic_on': object_type}
    relations = relationship(Relation,
                             primaryjoin=('content.c.content_id==relations.c.source_id'),
                             backref=backref("source",remote_side=[relations.c.source_id]))


mapper(Relation, relations, 
       properties = {'target': relationship(
                     Content, uselist=False,
                     primaryjoin=Content.content_id==relations.c.target_id)})


class Book(Content):
    __tablename__ = 'book'
    __table_args__ = {'autoload': True}
    __mapper_args__ = {'polymorphic_identity': 'BookPeer',
                       'polymorphic_on': Content.object_type}

    def authors(self):
        return [r.target for r in self.relations if r.relationship=='book_author']


class Person(Content):
    __tablename__ = 'person'
    __table_args__ = {'autoload': True}
    __mapper_args__ = {'polymorphic_identity': 'PersonPeer',
                       'polymorphic_on': Content.object_type}

