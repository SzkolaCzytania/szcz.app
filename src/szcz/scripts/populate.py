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
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    from szcz import models
    Base.metadata.create_all()

    with transaction.manager:
        user = models.User(email=u'andrew@mleczko.net', given_name=u'Andrew', family_name=u'Mleczko')
        DBSession.add(user)

        all_books = DBSession.query(models.Book).all()
        group1 = models.Group(name=u'Grupa krakowska')
        for i in range(10):
            group1.add_book(random.choice(all_books))
        group1.add_member(user, 'owner')
        DBSession.add(group1)

        group2 = models.Group(name=u'Grupa z Ferrary')
        for i in range(10):
            group2.add_book(random.choice(all_books))
        group2.add_member(user, 'member')
        DBSession.add(group2)
