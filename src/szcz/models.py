from sqlalchemy import (
    Column,
    Text,
    String,
    Integer,
    Boolean,
    )
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
