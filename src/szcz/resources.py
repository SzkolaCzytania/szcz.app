from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group
from js.bootstrap import bootstrap_responsive_css, bootstrap_js

library = Library('szcz', 'resources')
css_resource = Resource(library, 'main.css', depends=[bootstrap_responsive_css])
js_resource = Resource(library, 'main.js', depends=[bootstrap_js])
szcz = Group([css_resource, js_resource,])

def pserve():
    """A script aware of static resource"""
    import pyramid.scripts.pserve
    import pyramid_fanstatic
    import os

    dirname = os.path.dirname(__file__)
    dirname = os.path.join(dirname, 'resources')
    pyramid.scripts.pserve.add_file_callback(
                pyramid_fanstatic.file_callback(dirname))
    pyramid.scripts.pserve.main()
