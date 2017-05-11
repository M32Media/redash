/* eslint-disable */
import moment from 'moment';
import {language} from '../i18n';

export default function (ngModule) {
  ngModule.filter('toMilliseconds', () => value => value * 1000.0);

  ngModule.filter('dateTime', clientConfig =>
     function dateTime(value) {
       if (!value) {
         return '-';
       }
       return moment(value).locale(language.getCurrentLanguage().toLowerCase()).format(clientConfig.dateTimeFormat);
     }
  );
}
