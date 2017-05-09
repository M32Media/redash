/* eslint-disable */
export default function(ngModule){
    ngModule.filter("customNumbers", function($log, numberFilter) {
      return function formatNumber(num, shorten, decimals) {
        shorten = shorten == undefined ? false : shorten;
        var suffix = "";
        if(shorten) {
          if(num >= 1000000) {
            num /= 1000000;
            suffix = "M";
          } else if (num >= 1000) {
            num /= 1000;
            suffix = "K";
          }
        }
        //We use the angular number filter to keep most of the old behavior intact

        //apparently, if you pass undefined to the number filter it still registers it as a parameter and it doesn't want to
        //do its default behavior...

        //if (decimals === undefined) {
        //  return numberFilter(num) + suffix;
        //} else {
          return numberFilter(num, decimals) + suffix;
        //}
      }
    });
}