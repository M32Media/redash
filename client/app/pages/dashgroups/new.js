/* eslint-disable */
import template from './new.html';

function NewDashgroupCtrl($scope, $location, $http, toastr, currentUser, Events, Dashgroup) {
  Events.record('view', 'page', 'dashgroups/new');

  this.dashgroup_name = '';
  $scope.created = false;
  $scope.saveDashgroup = () => {
    if (!this.dashgroupForm.$valid || $scope.created) {
        return
    }
    Dashgroup.newDashgroup({name:this.dashgroup_name});
    $http.post('api/dashgroups/create', {
      dashgroup_name: this.dashgroup_name
    }).then(function(){
        $scope.created = true;
    });
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
