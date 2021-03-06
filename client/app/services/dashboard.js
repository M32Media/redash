/* eslint-disable */
import { map, isArray } from 'underscore';

function Dashboard($resource, $http, currentUser, Widget) {
  function transformSingle(dashboard) {
    dashboard.widgets = map(dashboard.widgets, row => row.map((widget) => {
      if(typeof widget === "object"){
        return new Widget(widget);
      } else if(typeof widget === 'number'){
        return widget;
      }
    }));
    dashboard.publicAccessEnabled = dashboard.public_url !== undefined;
  }

  const transform = $http.defaults.transformResponse.concat((data) => {

    if(!data){
      return undefined
    }
    else if (isArray(data)) {
      data.forEach(transformSingle);
    } else {
      transformSingle(data);
    }
    return data;
  });

  const resource = $resource('api/dashboards/:slug', { slug: '@slug' }, {
    get: { method: 'GET', transformResponse: transform },
    save: { method: 'POST', transformResponse: transform },
    query: { method: 'GET', isArray: true, transformResponse: transform },
    recent: {
      method: 'get',
      isArray: true,
      url: 'api/dashboards/recent',
      transformResponse: transform,
    },
    groups: {
      method: 'get',
      isArray: true,
      url: 'api/dashboards/groups',
    },
  });

  resource.prototype.canEdit = function canEdit() {
    return currentUser.canEdit(this) || this.can_edit;
  };


  return resource;
}

export default function (ngModule) {
  ngModule.factory('Dashboard', Dashboard);
}
