/* eslint-disable */

function Dashgroup($resource, $http, currentUser) {

  const resource = $resource('api/dashgroups/:slug', {slug: '@slug'}, {
    groups: {
      method: 'get',
      isArray: true,
      url: 'api/dashgroups/groups'
    },
    userGroups: {
      method: 'get',
      isArray: true,
      url: 'api/dashgroups/user_groups',
    },
    //This should have a better name but I don't know what it should be.
    oneUserGroups: {
      method: 'get',
      isArray: true,
      url: 'api/dashgroups/user_groups/:id'
    },
    dashgroupDashboard: {
      method: 'get',
      isArray: true,
      url: 'api/dashgroups/dashboards'
    },
    newDashgroup: {
      //should probably be post
      method: 'get',
      url: 'api/dashgroups/create/:name'
    }
  });
  return resource;
}

export default function (ngModule) {
  ngModule.factory('Dashgroup', Dashgroup);
}
