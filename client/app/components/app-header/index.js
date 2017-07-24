/* eslint-disable */
import debug from 'debug';

import * as _ from 'underscore';
import template from './app-header.html';
import logoUrl from '../../assets/images/m32-40x40.png';
import './app-header.css';
import { message, language } from '../../i18n'
const logger = debug('redash:appHeader');

function controller($rootScope, $location, $uibModal, Auth, currentUser, Dashboard, Dashgroup) {
  // TODO: logoUrl should come from clientconfig
  this.logoUrl = logoUrl;
  this.currentUser = currentUser;

  this.showQueriesMenu = currentUser.hasPermission('view_query');
  this.showNewQueryMenu = currentUser.hasPermission('create_query');

  this.message = message;

  this.language = language;

  this.showSettingsMenu = currentUser.hasPermission('list_users');
  this.showDashboardsMenu = currentUser.hasPermission('list_dashboards');

  this.reloadDashboards = () => {
    logger('Reloading dashboards.');
    //This can probably be unperformant if the number of groups is very large.
    if(!currentUser.hasPermission("admin")) {
      Dashgroup.userGroups().$promise.then((dg_results) => {
        // We can have dashgroups that looks like publisher.subcategory.
        var unique_names = _.uniq(dg_results.map((index) => index.dashgroup_name.split(".")[0]));
        this.multigroups = unique_names.length === 1 ? false : true;
        this.dashgroupsDashboards = {};
        this.dashboardHierarchy = {};
        // Let me tell you about the very important difference between var and let. var will fuck things up when its closed over and the var is rewritten over later,
        // let wont. Use let if you intend on closing over something.
        for (let i = 0; i < dg_results.length; i++) {
          let catName = dg_results[i].dashgroup_name.split('.')[0];
          if (!(catName in this.dashboardHierarchy)) {
            this.dashboardHierarchy[catName] = {subcats:{}, name:catName};
            if (!this.multigroups) {
              this.catName = catName;
            }
          }
          Dashgroup.oneDashgroupDashboards({id:dg_results[i].dashgroup_id}).$promise.then((db_results => {
            for (let j = 0; j < db_results.length; j++) {
              //In a format group:subcat:dashboardname
              var name = language.getCurrentLanguage() === "En" ? db_results[j].name : db_results[j].fr_name;
              var subcatName = name.split(':')[1];
              if(this.dashboardHierarchy[catName].subcats[subcatName] === undefined) {
                this.dashboardHierarchy[catName].subcats[subcatName] = {name: subcatName, dashboards:[db_results[j]]};
              } else {
                this.dashboardHierarchy[catName].subcats[subcatName].dashboards.push(db_results[j]);
              }
            }
          }));
        }
      });
    }
    this.dashboards = Dashboard.recent();
  };

  this.reloadDashboards();

  $rootScope.$on('reloadDashboards', this.reloadDashboards);

  this.newDashboard = () => {
    $uibModal.open({
      component: 'editDashboardDialog',
      resolve: {
        dashboard: () => ({ name: null, layout: null }),
      },
    });
  };

  this.searchQueries = () => {
    $location.path('/queries/search').search({ q: this.term });
  };

  this.logout = () => {
    Auth.logout();
  };
}

export default function (ngModule) {
  ngModule.component('appHeader', {
    template,
    controller,
  });
}
