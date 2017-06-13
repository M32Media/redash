/* eslint-disable */
import { language } from '../i18n'
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
        if(num === undefined || num === null) {
          return language.getCurrentLanguage() === 'En' ? "An error occured" : "Une erreur est survenue";
        }
        return numberFilter(num, decimals) + suffix;
      }
    });
}