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
    this.dashgroup = '0';
    this.gridsterOptions = {
      margins: [5, 5],
      rowHeight: 100,
      colWidth: 130,
      columns: 4,
      minColumns: 4,
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

    const widgetWidthToGridsterWidth = {'1':2, '2':4, '3':1, '4':3};

    if (this.dashboard.widgets) {
      this.dashboard.widgets.forEach((row, rowIndex) => {
        //Extra space caused by elements with a width > 1;
        var extra_space = 0;
        row.forEach((widget, colIndex) => {
          if(typeof widget === 'number') {
            console.log("passes");
            //the space a spacer takes is -(spacer_id)
            extra_space += (-widget) - 1;
            return
          }
          this.items.push({
            id: widget.id,
            col: colIndex + extra_space,
            row: rowIndex,
            sizeY: 1,
            sizeX: widgetWidthToGridsterWidth[parseInt(widget.width)],
            name: widget.getName(), // visualization.query.name
          });
          extra_space += this.items[this.items.length -1 ].sizeX - 1;
          console.log(this.items[this.items.length -1 ]);
        });
      });
    }
    console.log(this.items);

    this.saveDashboard = () => {
      if(this.dashgroup == '-1') {
        this.dashgroup = {id:-1, name:this.dashboard.name.split(':')[0]}
      } else {
        //Angular is weird. It works.
        this.dashgroup = {id:this.dashgroup};
      }
      this.saveInProgress = true;
      if (this.dashboard.id) {
        const layout = [];
        const sortedItems = sortBy(this.items, item => item.row * 10 + item.col);


        //This new code takes gaps in account and saves them in the layout.
        var last_item = {}
        sortedItems.forEach(function(item){
          const padding_needed_mapping = {'0':[],'1':[-1], '2': [-2], '3': [-3]};
          var padding_needed;
          if(layout[item.row] === undefined) {
            layout[item.row] = [];
            //If the starting col is not 0, there is a gap
            padding_needed = padding_needed_mapping[parseInt(item.col)];
          } else {
            //If the row already exists, we are guaranteed to have another item in the row.
            //If this is not 0, there is a gap between the two items
            var size_difference = item.col - (last_item.sizeX + last_item.col);
            padding_needed = padding_needed_mapping[parseInt(size_difference)];
          }
          //put all the padding
          padding_needed.forEach(function(i){layout[item.row].push(i)});
          //then puts the item.
          layout[item.row].push(item.id);
          //saves the last item
          last_item = item;
        });

        //Old code without saved spacers.
        /*sortedItems.forEach((item) => {
          layout[item.row] = layout[item.row] || [];
          if (item.col > 0 && layout[item.row][item.col - 1] === undefined) {
            layout[item.row][item.col - 1] = item.id;
          } else {
            layout[item.row][item.col] = item.id;
          }
        });*/

        const request = {
          slug: this.dashboard.id,
          name: this.dashboard.name,
          version: this.dashboard.version,
          layout: JSON.stringify(layout),
          dashgroup_id: this.dashgroup.id,
          dashgroup_name: this.dashgroup.name,
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
