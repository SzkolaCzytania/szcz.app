import os
import sys
import transaction
import random

from sqlalchemy import engine_from_config
from szcz import DBSession, Base

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, name='szcz')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    from szcz import models
    Base.metadata.create_all()

    with transaction.manager:
        user1 = models.User(email=u'andrew@mleczko.net', given_name=u'Andrew', family_name=u'Mleczko')
        DBSession.add(user1)
        user2 = models.User(email=u'a1@mleczko.net', given_name=u'Jan', family_name=u'Kowalski')
        DBSession.add(user2)
        user3 = models.User(email=u'a2@mleczko.net', given_name=u'Jan', family_name=u'Nowak')
        DBSession.add(user3)
        user4 = models.User(email=u'a3@mleczko.net', given_name=u'Piotr', family_name=u'Krauze')
        DBSession.add(user4)
        user5 = models.User(email=u'a4@mleczko.net', given_name=u'John', family_name=u'Smith')
        DBSession.add(user5)
        user6 = models.User(email=u'a5@mleczko.net', given_name=u'Marco', family_name=u'Rossi')
        DBSession.add(user6)
        user7 = models.User(email=u'a6@mleczko.net', given_name=u'Gustaw', family_name=u'Flawiusz')
        DBSession.add(user7)
        user8 = models.User(email=u'a7@mleczko.net', given_name=u'Roman', family_name=u'Kowalski')
        DBSession.add(user8)
        user9 = models.User(email=u'a8@mleczko.net', given_name=u'Marceli', family_name=u'Szpak')
        DBSession.add(user9)

        all_books = DBSession.query(models.Book).all()
        group1 = models.Group(name=u'Grupa krakowska')
        for i in range(10):
            group1.add_book(random.choice(all_books))
        group1.add_member(user1, 'owner')
        group1.add_member(user2, 'member')
        group1.add_member(user3, 'member')
        DBSession.add(group1)

        group2 = models.Group(name=u'Grupa z Ferrary')
        for i in range(10):
            group2.add_book(random.choice(all_books))
        group2.add_member(user1, 'member')
        group2.add_member(user4, 'member')
        group2.add_member(user5, 'member')
        group2.add_member(user6, 'member')
        group2.add_member(user7, 'member')
        group2.add_member(user8, 'member')
        group2.add_member(user9, 'member')
        DBSession.add(group2)

        group3 = models.Group(name=u'Grupa Lakoona')
        group3.add_member(user1, 'owner')
        for i in range(10):
            group3.add_book(random.choice(all_books))
        DBSession.add(group3)
