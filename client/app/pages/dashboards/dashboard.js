/* eslint-disable */
import * as _ from 'underscore';
import template from './dashboard.html';
import shareDashboardTemplate from './share-dashboard.html';
import moment from 'moment';
import {language, message} from '../../i18n';
import '../../assets/css/custom_animations.css';

function DashboardCtrl($rootScope, $routeParams, $location, $timeout, $q, $uibModal,
  Title, AlertDialog, Dashboard, currentUser, clientConfig, Events, Dashgroup) {
  this.isFullscreen = false;
  this.refreshRate = null;
  this.dashboard = {}
  this.showPermissionsControl = clientConfig.showPermissionsControl;
  this.currentUser = currentUser;
  this.retries = 0;
  this.globalParameters = [];
  this.refreshRates = [
    { name: '10 seconds', rate: 10 },
    { name: '30 seconds', rate: 30 },
    { name: '1 minute', rate: 60 },
    { name: '5 minutes', rate: 60 * 5 },
    { name: '10 minutes', rate: 60 * 10 },
    { name: '30 minutes', rate: 60 * 30 },
    { name: '1 hour', rate: 60 * 60 },
  ];
  this.message = message;
  this.setRefreshRate = (rate) => {
    this.refreshRate = rate;
    if (rate !== null) {
      this.loadDashboard(true);
      this.autoRefresh();
    }
  };

  //lol
  moment.locale(language.getCurrentLanguage().toLowerCase());

  if(!currentUser.hasPermission("admin")) {
    Dashgroup.userGroups().$promise.then((dg_results) => {
      this.multigroups = dg_results.length === 1 ? false : true;
    });
  }

  String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  }

  this.getDashboardName = () => {
    
    //We want the more formal name for viewers of many dashgroups
    var name = language.getCurrentLanguage() === "En" ? this.dashboard.name: this.dashboard.fr_name;
    // wat
    if(name === undefined) {
      return
    }
    if(this.multigroups || currentUser.hasPermission("admin")) {
      return name;
    } else {
      var parts = name.split(':');
      return parts[1].capitalize() + " - " + parts[2].capitalize() + " (" + parts[0].capitalize() +")";
    }
    
  }

  this.getMaxUpdateDate = () => {
    var update_dates = [];
    var widgets = _.flatten(this.dashboard.widgets);
    for (var i = 0; i < widgets.length; i++) {
      if(widgets[i].visualization !== undefined) {
        update_dates.push(widgets[i].query.queryResult.getUpdatedAt());
      }
    }
    return _.min(update_dates, function(time){return moment(time).millisecond()});
  }

  this.extractGlobalParameters = () => {
    let globalParams = {};
    this.dashboard.widgets.forEach(row =>
      row.forEach((widget) => {
        if (typeof widget === "number") {
          return
        }
        if (widget.getQuery()) {
          widget.getQuery().getParametersDefs().filter(p => p.global).forEach((param) => {
            const defaults = {};
            defaults[param.name] = _.create(Object.getPrototypeOf(param), param);
            defaults[param.name].locals = [];
            globalParams = _.defaults(globalParams, defaults);
            globalParams[param.name].locals.push(param);
          });
        }
      })
    );
    this.globalParameters = _.values(globalParams);
  };

  this.onGlobalParametersChange = () => {
    this.globalParameters.forEach((global) => {
      global.locals.forEach((local) => {
        local.value = global.value;
      });
    });
  };

  const renderDashboard = (dashboard, force) => {
    Title.set(dashboard.name);
    const promises = [];

    this.dashboard.widgets.forEach(row =>
       row.forEach((widget) => {
         if (widget.visualization) {
           const maxAge = force ? 0 : undefined;
           const queryResult = widget.getQuery().getQueryResult(maxAge);
           if (!_.isUndefined(queryResult)) {
             promises.push(queryResult.toPromise());
           }
         }
       })
    );

    this.extractGlobalParameters();

    $q.all(promises).then((queryResults) => {
      const filters = {};
      queryResults.forEach((queryResult) => {
        const queryFilters = queryResult.getFilters();
        queryFilters.forEach((queryFilter) => {
          const hasQueryStringValue = _.has($location.search(), queryFilter.name);

          if (!(hasQueryStringValue || dashboard.dashboard_filters_enabled)) {
            // If dashboard filters not enabled, or no query string value given,
            // skip filters linking.
            return;
          }

          if (hasQueryStringValue) {
            queryFilter.current = $location.search()[queryFilter.name];
          }

          if (!_.has(filters, queryFilter.name)) {
            const filter = _.extend({}, queryFilter);
            filters[filter.name] = filter;
            filters[filter.name].originFilters = [];
          }

          // TODO: merge values.
          filters[queryFilter.name].originFilters.push(queryFilter);
        });
      });

      this.filters = _.values(filters);
      //console.log(this.filters);
      //We want all the filters to get all the possible values.
      for (var i = 0; i < this.filters.length; i++) {
        this.filters[i].originFilters = _.sortBy(this.filters[i].originFilters, (origFilt) => -origFilt.values.length)
        this.filters[i].values = _.clone(this.filters[i].originFilters[0].values);
        for (var j = 0; j < this.filters[i].originFilters.length; j++) {
          this.filters[i].originFilters[j].values = _.clone(this.filters[i].originFilters[0].values);
        }
      }

      this.filtersOnChange = (filter) => {
        _.each(filter.originFilters, (originFilter) => {
          originFilter.current = filter.current;
        });
      };

      if(this.filters.length > 0) {
        this.filtersOnChange(this.filters[0]);
      }

    });
  };


  this.loadDashboard = (force) => {

    Dashboard.get({ slug: $routeParams.dashboardSlug }).$promise.then((dashboard) => {

      this.dashboard = dashboard

      Events.record('view', 'dashboard', dashboard.id);
      renderDashboard(dashboard, force);

    }).catch((error) => {

      console.log(error)

      window.location = "/"

    })

  }

  this.loadDashboard()

  this.autoRefresh = () => {
    $timeout(() => {
      this.loadDashboard(true);
    }, this.refreshRate.rate * 1000
    ).then(() => this.autoRefresh());
  };

  this.archiveDashboard = () => {
    const archive = () => {
      Events.record('archive', 'dashboard', this.dashboard.id);
      this.dashboard.$delete(() => {
        $rootScope.$broadcast('reloadDashboards');
      });
    };

    const title = 'Archive Dashboard';
    const message = `Are you sure you want to archive the "${this.dashboard.name}" dashboard?`;
    const confirm = { class: 'btn-warning', title: 'Archive' };

    AlertDialog.open(title, message, confirm).then(archive);
  };

  this.showManagePermissionsModal = () => {
    $uibModal.open({
      component: 'permissionsEditor',
      resolve: {
        aclUrl: { url: `api/dashboards/${this.dashboard.id}/acl` },
      },
    });
  };

  this.editDashboard = () => {
    $uibModal.open({
      component: 'editDashboardDialog',
      resolve: {
        dashboard: () => this.dashboard,
      },
    }).result.then((dashboard) => { this.dashboard = dashboard; });
  };

  this.addWidget = () => {
    $uibModal.open({
      component: 'addWidgetDialog',
      resolve: {
        dashboard: () => this.dashboard,
      },
    }).result.then(() => this.extractGlobalParameters());
  };

  this.toggleFullscreen = () => {
    this.isFullscreen = !this.isFullscreen;
    document.querySelector('body').classList.toggle('headless');

    if (this.isFullscreen) {
      $location.search('fullscreen', true);
    } else {
      $location.search('fullscreen', null);
    }
  };

  this.togglePublished = () => {
    Events.record('toggle_published', 'dashboard', this.dashboard.id);
    this.dashboard.is_draft = !this.dashboard.is_draft;
    this.saveInProgress = true;
    Dashboard.save({
      slug: this.dashboard.id,
      name: this.dashboard.name,
      layout: JSON.stringify(this.dashboard.layout),
      is_draft: this.dashboard.is_draft,
    }, (dashboard) => {
      this.saveInProgress = false;
      this.dashboard.version = dashboard.version;
      $rootScope.$broadcast('reloadDashboards');
    });
  };

  if (_.has($location.search(), 'fullscreen')) {
    this.toggleFullscreen();
  }

  this.openShareForm = () => {
    $uibModal.open({
      component: 'shareDashboard',
      resolve: {
        dashboard: this.dashboard,
      },
    });
  };
}

const ShareDashboardComponent = {
  template: shareDashboardTemplate,
  bindings: {
    resolve: '<',
    close: '&',
    dismiss: '&',
  },
  controller($http) {
    'ngInject';

    this.dashboard = this.resolve.dashboard;

    this.toggleSharing = () => {
      const url = `api/dashboards/${this.dashboard.id}/share`;

      if (!this.dashboard.publicAccessEnabled) {
        // disable
        $http.delete(url).success(() => {
          this.dashboard.publicAccessEnabled = false;
          delete this.dashboard.public_url;
        }).error(() => {
          this.dashboard.publicAccessEnabled = true;
          // TODO: show message
        });
      } else {
        $http.post(url).success((data) => {
          this.dashboard.publicAccessEnabled = true;
          this.dashboard.public_url = data.public_url;
        }).error(() => {
          this.dashboard.publicAccessEnabled = false;
          // TODO: show message
        });
      }
    };
  },
};

export default function (ngModule) {
  ngModule.component('shareDashboard', ShareDashboardComponent);
  ngModule.component('dashboardPage', {
    template,
    controller: DashboardCtrl,
  });

  return {
    '/dashboard/:dashboardSlug': {
      template: '<dashboard-page></dashboard-page>',
      reloadOnSearch: false,
    },
  };
}
