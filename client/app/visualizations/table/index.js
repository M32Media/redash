/* eslint-disable */
import moment from 'moment';
import { _, partial, isString } from 'underscore';
import { getColumnCleanName } from '../../services/query-result';
import template from './table.html';
import tableEditorTemplate from './table-editor.html';

function formatValue($filter, clientConfig, value, type) {
  let formattedValue = value;
  switch (type) {
    case 'integer':
      formattedValue = $filter('number')(value, 0);
      break;
    case 'float':
      formattedValue = $filter('number')(value, 2);
      break;
    case 'boolean':
      if (value !== undefined) {
        formattedValue = String(value);
      }
      break;
    case 'date':
      if (value && moment.isMoment(value)) {
        formattedValue = value.format(clientConfig.dateFormat);
      }
      break;
    case 'datetime':
      if (value && moment.isMoment(value)) {
        formattedValue = value.format(clientConfig.dateTimeFormat);
      }
      break;
    default:
      if (isString(value)) {
        formattedValue = $filter('linkify')(value);
      }
      break;
  }

  return formattedValue;
}

function GridRenderer(clientConfig) {
  return {
    restrict: 'E',
    scope: {
      queryResult: '=',
      itemsPerPage: '=',
      visualization: '=',
    },
    template,
    replace: false,
    controller($scope, $filter) {
      $scope.gridColumns = [];
      $scope.gridRows = [];
      if($scope.visualization !== undefined) {
        $scope.heightClass = $scope.visualization.options.format === 'short' ? 'short-dynamic-table' : '';
      }

      $scope.$watch('queryResult && queryResult.getData()', (queryResult) => {
        if (!queryResult) {
          return;
        }

        if ($scope.queryResult.getData() == null) {
          $scope.gridColumns = [];
          $scope.filters = [];
        } else {
          $scope.filters = $scope.queryResult.getFilters();

          const columns = $scope.queryResult.getColumns();
          columns.forEach((col) => {
            col.title = getColumnCleanName(col.name);
            col.formatFunction = partial(formatValue, $filter, clientConfig, _, col.type);
          });

          $scope.gridRows = $scope.queryResult.getData();
          $scope.gridColumns = columns;
        }
      });
    },
  };
}

function TableEditor() {
  return {
    restrict: 'E',
    template: tableEditorTemplate,
  };
}


export default function (ngModule) {
  ngModule.directive('tableEditor', TableEditor);
  ngModule.directive('gridRenderer', GridRenderer);
  const defaultOptions = {
    format: "short"
  };
  ngModule.config((VisualizationProvider) => {
    VisualizationProvider.registerVisualization({
      type: 'TABLE',
      name: 'Table',
      defaultOptions,
      renderTemplate: '<grid-renderer visualization="visualization" query-result="queryResult"></grid-renderer>',
      editorTemplate: '<table-editor></table-editor>',
    });
  });
}
