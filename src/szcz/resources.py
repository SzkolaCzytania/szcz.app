from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group
from js.lightbox import lightbox
from js.bootstrap import bootstrap_responsive_css, bootstrap_js
from js.jquery_datatables import jquery_datatables_js
from js.jqueryui import ui_datepicker_locales

library = Library('szcz', 'resources')
css_resource = Resource(library, 'main.css', depends=[bootstrap_responsive_css])
js_resource = Resource(library, 'main.js', depends=[bootstrap_js, ui_datepicker_locales['pl']])
paging = Resource(library, 'paging.js', depends=[jquery_datatables_js])
szcz_datatables_js = Resource(library, 'szcz_datatables.js', depends=[jquery_datatables_js])
szcz_datatables_css = Resource(library, 'szcz_datatables.css')
datatables = Group([paging, szcz_datatables_css, szcz_datatables_js])
szcz = Group([css_resource, js_resource, lightbox])
