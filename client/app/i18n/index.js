/* eslint-disable */

//This file is a home solutions because the "built in" translation things that comes with angular
//are totally overkill for our purpose (and are XML based **shudder**)
import { cookies } from '../utils'

var messages = {
    "logOut": {"Fr":"Déconnection", "En": "Log out"},
    "dashboards": {"Fr":"Tableaux", "En": "Dashboards"},
    "recentDashboards": {"Fr":"Tableaux récents", "En": "Recent Dashboards"},
    "updated" : {"Fr":"Mis à jour", "En": "Updated"},
    "downloadAsCSV":{"Fr":"Télécharger en format CSV", "En": "Download as CSV File"},
    "downloadAsExcel":{"Fr":"Télécharger en format Excel", "En": "Download as Excel File"},
    "close" : {"Fr":"Fermer", "En": "Close"},

};

var language = {
    getCurrentLanguage: () => {
        var lang = cookies.readCookie("lang");
        //Default language is english.
        if(lang === null) {
          cookies.createCookie("lang", "En");
          return "En";
        }
        else return lang;
    },
    //javascript weirdness, `this` can't be accessed in litteral object definition so we need a function to reference previous entries.
    init: function() {
        this.getOtherLanguage = () => {
            console.log(this);
            return this.getCurrentLanguage() === "Fr" ? "En": "Fr";
        };
        this.swapLanguage = () => {
            cookies.createCookie("lang", this.getOtherLanguage());
            location.reload(true);
        };
        return this
    }
}.init();

function message(messageName) {
    return messages[messageName][language.getCurrentLanguage()];
}

export {message, language};