/* eslint-disable */
import template from './new.html';

function NewDashgroupCtrl($scope, $location, toastr, currentUser, Events, Dashgroup) {
  Events.record('view', 'page', 'dashgroups/new');

  this.dashgroup_name = '';
  $scope.created = false;
  $scope.saveDashgroup = () => {
    if (!this.dashgroupForm.$valid) {
      console.log("invalid form for new dashgroup");
    }
    Dashgroup.newDashgroup({name:this.dashgroup_name});
    $scope.created = true;
  };
}

export default function (ngModule) {
  ngModule.controller('NewDashgroupCtrl', NewDashgroupCtrl);

  return {
    '/dashgroups/new': {
      template,
      controller: 'NewDashgroupCtrl',
      controllerAs: '$ctrl',
      bindToController: 'true',
    },
  };
}
