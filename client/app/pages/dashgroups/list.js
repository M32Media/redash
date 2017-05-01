import template from './list.html';

function DashgroupsCtrl($scope, $location, currentUser, Events, Dashgroup) {
  Events.record('view', 'page', 'admin/dashgroups');

  $scope.dashgroups = Dashgroup.groups();
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
