import os
import sys

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
    from szcz import models; models
    Base.metadata.create_all()

#    with transaction.manager:
#        model = User(email=u'pippo@email.it')
#        DBSession.add(model)
