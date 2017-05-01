/* eslint-disable */
import _ from 'underscore';

import template from './list.html';

function DashgroupsCtrl($scope, $location, $q, currentUser, Events, Dashgroup) {
  Events.record('view', 'page', 'admin/dashgroups');

  $scope.detailedDashgroups = [];

  const promises = {
    groups: Dashgroup.groups().$promise,
    dashgroupDashboard: Dashgroup.dashgroupDashboard().$promise
  }

  //To call multiple promises
  $q.all(promises).then((results) => {

    //For each dashgroup find dashboards
    _.each(results.groups, (group) => {

      var dashboards = [];

      //Find all dashboards inside dashgroup
      dashboards = _.filter(results.dashgroupDashboard, (dgdb) => {

        return group.id == dgdb.dashgroup_id
          
      });

      //Add 
      group.dashboards = dashboards;

      console.log(group.dashboards)

      $scope.detailedDashgroups.push(group);

    });

  });

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