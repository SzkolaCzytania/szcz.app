$.extend( $.fn.dataTableExt.oStdClasses, {
        "sWrapper": "dataTables_wrapper form-inline"
} );

$(document).ready(function() {
   $('.data_table').dataTable( {
      "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
      "sPaginationType": "bootstrap",
      "oLanguage": {"sProcessing":   "Proszę czekać...",
                    "sLengthMenu":   "Pokaż _MENU_ pozycji",
                    "sZeroRecords":  "Nie znaleziono żadnych pasujących indeksów",
                    "sInfo":         "Pozycje od _START_ do _END_ z _TOTAL_ łącznie",
                    "sInfoEmpty":    "Pozycji 0 z 0 dostępnych",
                    "sInfoFiltered": "(filtrowanie spośród _MAX_ dostępnych pozycji)",
                    "sInfoPostFix":  "",
                    "sSearch":       "Szukaj:",
                    "sUrl":          "",
                    "oPaginate": {
                            "sFirst":    "Pierwsza",
                            "sPrevious": "Poprzednia",
                            "sNext":     "Następna",
                            "sLast":     "Ostatnia"}}
    } );
} );
