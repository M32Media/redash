/* eslint-disable */
import { find } from 'underscore';
import template from './visualization-embed.html';
import logoUrl from '../../assets/images/m32-40x40.png';

const VisualizationEmbed = {
  template,
  bindings: {
    data: '<',
  },
  controller($routeParams, Query, QueryResult) {
    'ngInject';

    document.querySelector('body').classList.add('headless');
    const visualizationId = parseInt($routeParams.visualizationId, 10);
    this.showQueryDescription = $routeParams.showDescription;
    this.apiKey = $routeParams.api_key;
    this.logoUrl = logoUrl;
    this.query = new Query(this.data[0]);
    this.queryResult = new QueryResult(this.data[1]);
    this.visualization =
      find(this.query.visualizations, visualization => visualization.id === visualizationId);
  },
};

export default function (ngModule) {
  ngModule.component('visualizationEmbed', VisualizationEmbed);

  function loadData($http, $route, $q) {
    console.log(document.referrer);
    const queryToken = $route.current.params.queryToken;
    const visualizationId = $route.current.params.visualizationId;
    const query = $http.post(`/api/embeded/query/${visualizationId}/${queryToken}`, {referrer:document.referrer}).then(response => response.data);
    const queryResult = $http.post(`/api/embeded/result/${visualizationId}/${queryToken}`,{referrer:document.referrer}).then(response => response.data);
    return $q.all([query, queryResult]);
  }

  ngModule.config(($routeProvider) => {
    $routeProvider.when('/embed/:visualizationId/:queryToken', {
      template: '<visualization-embed data="$resolve.data"></visualization-embed>',
      resolve: {
        data: loadData,
      },
    });
  });
}
