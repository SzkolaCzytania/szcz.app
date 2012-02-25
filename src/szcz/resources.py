from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group
from js.lightbox import lightbox
from js.bootstrap import bootstrap_responsive_css, bootstrap_js
from js.jquery_datatables import jquery_datatables_js

library = Library('szcz', 'resources')
css_resource = Resource(library, 'main.css', depends=[bootstrap_responsive_css])
js_resource = Resource(library, 'main.js', depends=[bootstrap_js])
paging = Resource(library, 'paging.js', depends=[jquery_datatables_js])
szcz_datatables_js = Resource(library, 'szcz_datatables.js', depends=[jquery_datatables_js])
szcz_datatables_css = Resource(library, 'szcz_datatables.css')
datatables = Group([paging, szcz_datatables_css, szcz_datatables_js])
szcz = Group([css_resource, js_resource, lightbox])

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
