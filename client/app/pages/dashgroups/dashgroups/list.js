/* eslint-disable */

import template from './list.html';

function DashgroupsCtrl($scope, $location, currentUser, Events) {
  Events.record('view', 'page', 'admin/dashgroups');

}

export default function (ngModule) {
  ngModule.controller('DashgroupsCtrl', DashgroupsCtrl);

  return {
    '/dashgroups': {
      template,
      controller: 'DashgroupsCtrl',
      title: 'Dashgroups',
    },
  };
}