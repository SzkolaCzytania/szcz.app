import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_zcml',
    'pyramid_mailer',
    'SQLAlchemy',
    'psycopg2',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_deform',
    'zope.sqlalchemy',
    'waitress',
    'velruse',
    'pyramid_fanstatic',
    'js.bootstrap',
    'js.lightbox',
    'pyramid_beaker',
    'deform_bootstrap',
    'deform',
    #'fanstaticdeform',
    'js.deform',
    'js.jquery_datatables',
    'js.deform_bootstrap',
    'repoze.workflow',
    ]

setup(name='szcz',
      version='0.0',
      description='szcz',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='szcz',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = szcz:main
      [console_scripts]
      populate_szcz = szcz.scripts.populate:main
      # Fanstatic resource library
      [fanstatic.libraries]
      szcz = szcz.resources:library
      """,
      )

