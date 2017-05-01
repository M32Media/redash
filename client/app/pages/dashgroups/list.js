/* eslint-disable */
import _ from 'underscore';

import template from './list.html';

function DashgroupsCtrl($scope, $location, $q, currentUser, Events, Dashgroup) {
  Events.record('view', 'page', 'admin/dashgroups');

  const promises = {
    groups: Dashgroup.groups(),
    dashgroupDashboard: Dashgroup.dashgroupDashboard()
  }

  $q.all(promises).then((results) => {
    
    _.each(results, function(result){
      console.log(result)
    })



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