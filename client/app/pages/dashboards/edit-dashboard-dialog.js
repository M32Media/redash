/* eslint-disable */
import { sortBy } from 'underscore';
import template from './edit-dashboard-dialog.html';


const EditDashboardDialog = {
  bindings: {
    resolve: '<',
    close: '&',
    dismiss: '&',
  },
  template,
  controller($rootScope, $location, $http, toastr, Events, Dashboard, Dashgroup) {
    'ngInject';
    this.dashgroups = Dashgroup.groups();
    this.dashboard = this.resolve.dashboard;
    this.dashgroup = null;
    this.gridsterOptions = {
      margins: [5, 5],
      rowHeight: 100,
      colWidth: 260,
      columns: 2,
      mobileModeEnabled: false,
      swapping: true,
      minRows: 1,
      draggable: {
        enabled: true,
      },
      resizable: {
        enabled: false,
      },
    };

    this.items = [];

    if (this.dashboard.widgets) {
      this.dashboard.widgets.forEach((row, rowIndex) => {
        row.forEach((widget, colIndex) => {
          this.items.push({
            id: widget.id,
            col: colIndex,
            row: rowIndex,
            sizeY: 1,
            sizeX: widget.width,
            name: widget.getName(), // visualization.query.name
          });
        });
      });
    }

    this.saveDashboard = () => {
      if(this.dashgroup === null) {
        this.dashgroup = {id:0, name:this.dashboard.name.split(':')[0]}
      } else {
        //Angular is weird. It works.
        this.dashgroup = {id:this.dashgroup};
      }
      this.saveInProgress = true;
      console.log("SAVING");
      console.log(JSON.stringify(this.dashgroup))
      if (this.dashboard.id) {
        sortedItems.forEach((item) => {
          layout[item.row] = layout[item.row] || [];
          if (item.col > 0 && layout[item.row][item.col - 1] === undefined) {
            layout[item.row][item.col - 1] = item.id;
          } else {
            layout[item.row][item.col] = item.id;
          }
        });

        const request = {
          slug: this.dashboard.id,
          name: this.dashboard.name,
          version: this.dashboard.version,
          layout: JSON.stringify(layout),
        };

        Dashboard.save(request, (dashboard) => {
          this.dashboard = dashboard;
          this.saveInProgress = false;
          this.close({ $value: this.dashboard });
          $rootScope.$broadcast('reloadDashboards');
        }, (error) => {
          this.saveInProgress = false;
          if (error.status === 403) {
            toastr.error('Unable to save dashboard: Permission denied.');
          } else if (error.status === 409) {
            toastr.error('It seems like the dashboard has been modified by another user. ' +
                'Please copy/backup your changes and reload this page.', { autoDismiss: false });
          }
        });
        Events.record('edit', 'dashboard', this.dashboard.id);
      } else {
        console.log("dashgroupppp : " + this.dashgroup);
        $http.post('api/dashboards', {
          name: this.dashboard.name, 
          dashgroup_id: this.dashgroup.id,
          dashgroup_name: this.dashgroup.name
        }).success((response) => {
          this.close();
          $location.path(`/dashboard/${response.slug}`).replace();
        });
        Events.record('create', 'dashboard');
      }
    };
  },
};

export default function (ngModule) {
  ngModule.component('editDashboardDialog', EditDashboardDialog);
}
