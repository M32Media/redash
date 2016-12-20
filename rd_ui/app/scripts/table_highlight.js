var tableData = [
    {tableName: 'Sites (Top 10 impressions Lost) (DFP/AdX)',
     predicat: function(text){ return  text == '05 - Remnant' ||
                                text == '07 - Unsold';},
     elClass: 'losingHappy',
     columnTest: 0,
     columnChange: 5},
    {tableName: 'Sites (Top 10 Impressions Gain) (DFP/AdX)',
     predicat: function(text){ return text != '05 - Remnant' ||
                               text != '07 - Unsold';},
     elClass: 'losingSad',
     columnTest: 0,
     columnChange: 5}
];

function doHighlight(){
    $('table.smart-table').closest('.tile').find('a.query-link').each(function (i, el){
        var predicat = 0;
        for(var i = 0; i < tableData.length; i++){
            if($(el).text() == tableData[i].tableName){
                predicat = tableData[i].predicat;
                var elClass = tableData[i].elClass;
                var columnTest = tableData[i].columnTest;
                var columnChange = tableData[i].columnChange;
            }
        }
        if(predicat == 0)
            return;

        var table = $(this).closest('.tile').find('table.smart-table');
        table.find('tbody tr').each(function(i, el){
            $(el).find('td').not('.smart-table-global-search').each(function (i, el){
                if(i == columnTest && predicat($(el).text())){
                    $(el).parent().find('td')[columnChange].classList.add(elClass);
                }
            });
        });
    });
}
$(document).ready(function () {
    doHighlight();
});
