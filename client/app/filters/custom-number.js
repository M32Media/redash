/* eslint-disable */
import { language } from '../i18n'
export default function(ngModule){
    ngModule.filter("customNumbers", function($log, numberFilter) {
      return function formatNumber(num, shorten, decimals) {
        shorten = shorten == undefined ? false : shorten;
        var suffix = "";
        if(shorten) {
          if(num >= 999500) {
            num /= 1000000;
            suffix = "M";
          } else if (num >= 1000) {
            num /= 1000;
            suffix = "K";
          }
        }
        if(num === undefined || num === null) {
          // getDate() is the true way to get the day of the month. getDay returns the day of the week -_-
          if (new Date().getDate() !== 1) {
            // Some queries return an undefined result the first of each month...
            return "";
          }
          return language.getCurrentLanguage() === 'En' ? "An error occured" : "Une erreur est survenue";
        }
        return numberFilter(num, decimals) + suffix;
      }
    });
}