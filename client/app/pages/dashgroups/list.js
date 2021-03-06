/* eslint-disable */
import _ from 'underscore';

import template from './list.html';

function DashgroupsCtrl($scope, $http, $location, $q, currentUser, Events, Dashgroup) {
  Events.record('view', 'page', 'admin/dashgroups');

  $scope.showDetails = false;
  $scope.detailedDashgroups = [];
  this.currentUser = currentUser;
  this.showNewButton = currentUser.hasPermission("admin");

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


      $scope.detailedDashgroups.push(group);

    });

  });


  $scope.removeDashboard = (event, dgId, dbId) =>{


    const data = {};
    data.dbId = dbId;
    data.dgId = dgId;

    $http.delete(`api/dashgroups/${data.dgId}/dashboards/${data.dbId}`).success((response) => {
      event.target.parentElement.remove()
    })

  }

}

export default function (ngModule) {
  ngModule.controller('DashgroupsCtrl', DashgroupsCtrl);

  return {
    '/dashgroups': {
      template,
      controller: 'DashgroupsCtrl',
      controllerAs: '$ctrl',
      title: 'Dashgroups',
    },
  };
}