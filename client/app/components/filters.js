/* eslint-disable */
import template from './filters.html';
import { message } from '../i18n';

const FiltersComponent = {
  template,
  bindings: {
    onChange: '&',
    filters: '<',
  },
  controller() {
    'ngInject';
    this.message = message;
    this.filterChangeListener = (filter, modal) => {
      this.onChange({ filter, $modal: modal });
    };
  },
};


export default function (ngModule) {
  ngModule.component('filters', FiltersComponent);
}
