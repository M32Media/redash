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
          return numberFilter(num, decimals) + suffix;
      }
    });
}