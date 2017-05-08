/* eslint-disable */
import template from './widget.html';
import editTextBoxTemplate from './edit-text-box.html';

const EditTextBoxComponent = {
  template: editTextBoxTemplate,
  bindings: {
    resolve: '<',
    close: '&',
    dismiss: '&',
  },
  controller(toastr) {
    'ngInject';

    this.saveInProgress = false;
    this.widget = this.resolve.widget;
    this.saveWidget = () => {
      this.saveInProgress = true;
      this.widget.$save().then(() => {
        this.close();
      }).catch(() => {
        toastr.error('Widget can not be updated');
      }).finally(() => {
        this.saveInProgress = false;
      });
    };
  },
};

function DashboardWidgetCtrl($location, $uibModal, $window, Events, currentUser) {
  //A negative widget id means a spacer
  this.isSpacer = false;
  if(typeof this.widget === 'number') {
    //1 is 50%, 2 is 100%(unused), 3 is 25% and 4 is 75%
    const spacerIdToWidth = {'-1':3, '-2':1, '-3':4};

    var width = spacerIdToWidth[parseInt(this.widget)];
    this.widget = {};
    this.widget.width = width;
    this.isSpacer = true;
  }

  this.canViewQuery = currentUser.hasPermission('view_query');
  this.canViewQueryLink = currentUser.hasPermission('admin');

  this.editTextBox = () => {
    $uibModal.open({
      component: 'editTextBox',
      resolve: {
        widget: this.widget,
      },
    });
  };

  this.localParametersDefs = () => {
    if (!this.localParameters) {
      this.localParameters = this.widget.query.getParametersDefs().filter(p => !p.global);
    }
    return this.localParameters;
  };

  this.deleteWidget = () => {
    if (!$window.confirm(`Are you sure you want to remove "${this.widget.getName()}" from the dashboard?`)) {
      return;
    }

    Events.record('delete', 'widget', this.widget.id);

    this.widget.$delete((response) => {
      this.dashboard.widgets =
        this.dashboard.widgets.map(row => row.filter(widget => widget.id !== undefined));

      this.dashboard.widgets = this.dashboard.widgets.filter(row => row.length > 0);

      this.dashboard.layout = response.layout;
      this.dashboard.version = response.version;

      if (this.deleted) {
        this.deleted({});
      }
    });
  };

  Events.record('view', 'widget', this.widget.id);

  this.reload = (force) => {
    let maxAge = $location.search().maxAge;
    if (force) {
      maxAge = 0;
    }
    this.queryResult = this.query.getQueryResult(maxAge);
  };

  if (this.widget.visualization) {
    Events.record('view', 'query', this.widget.visualization.query.id);
    Events.record('view', 'visualization', this.widget.visualization.id);

    this.query = this.widget.getQuery();
    this.reload(false);

    this.type = 'visualization';
  } else if (this.widget.restricted) {
    this.type = 'restricted';
  } else {
    this.type = 'textbox';
  }
}

export default function (ngModule) {
  ngModule.component('editTextBox', EditTextBoxComponent);
  ngModule.component('dashboardWidget', {
    template,
    controller: DashboardWidgetCtrl,
    bindings: {
      widget: '<',
      public: '<',
      dashboard: '<',
      deleted: '&onDelete',
    },
  });
}
