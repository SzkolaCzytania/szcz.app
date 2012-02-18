from sqlalchemy import (
    Column,
    Text,
    String,
    Integer,
    Boolean,
    )
from sqlalchemy.orm import relationship

from szcz import MirrorBase


class Book(MirrorBase):
    __tablename__ = 'book'
    __table_args__ = {'autoload': True}
    content = relationship("Content")

    @property
    def title(self):
        return self.content.title

    @property
    def description(self):
        return self.content.description


class Content(MirrorBase):
    __tablename__ = 'content'
    __table_args__ = {'autoload': True}
