// main js script for 
$(document).ready(function() {
   $('a.lightbox').lightBox({
    imageLoading: '/fanstatic/lightbox/img/lightbox-ico-loading.gif',
    imageBtnClose: '/fanstatic/lightbox/img/lightbox-btn-close.gif',
    imageBtnPrev: '/fanstatic/lightbox/img/lightbox-btn-prev.gif',
    imageBtnNext: '/fanstatic/lightbox/img/lightbox-btn-next.gif',
    imageBlank: '/fanstatic/lightbox/img/lightbox-blank.gif',
   });
   $.pnotify.defaults.history = false;
});
