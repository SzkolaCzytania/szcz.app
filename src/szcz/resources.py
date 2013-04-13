from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group
from js.lightbox import lightbox
from js.bootstrap import bootstrap_responsive_css, bootstrap_js
from js.jquery_datatables import jquery_datatables_js
from js.jqueryui import ui_datepicker_locales
from js.deform import resource_mapping
from js.modernizr import modernizr
resource_mapping['modernizr'] = modernizr

library = Library('szcz', 'resources')
css_resource = Resource(library, 'main.css', depends=[bootstrap_responsive_css])
js_resource = Resource(library, 'main.js', depends=[bootstrap_js, ui_datepicker_locales['pl']])
paging = Resource(library, 'paging.js', depends=[jquery_datatables_js])

szcz_datatables_js = Resource(library, 'szcz_datatables.js', depends=[jquery_datatables_js])
szcz_datatables_css = Resource(library, 'szcz_datatables.css')

pnotify_js = Resource(library, 'jquery.pnotify.min.js')
pnotify_css = Resource(library, 'jquery.pnotify.default.css')
pnotify_icons = Resource(library, 'jquery.pnotify.default.icons.css')
pnotify = Group([pnotify_js, pnotify_css, pnotify_icons])

datatables = Group([paging, szcz_datatables_css, szcz_datatables_js])
szcz = Group([css_resource, js_resource, lightbox, pnotify])
