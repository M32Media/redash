import template from './permissions.html';

function PermissionsCtrl($scope, $routeParams, $http, $location, toastr,
                              currentUser, Events, Group) {
  Events.record('view', 'permissions', $scope.groupId);
  $scope.group = Group.get({ id: $routeParams.groupId });
}

export default function (ngModule) {
  ngModule.controller('PermissionsCtrl', PermissionsCtrl);

  return {
    '/groups/:groupId/permissions': {
      template,
      controller: 'PermissionsCtrl',
    },
  };
}
