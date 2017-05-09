/* eslint-disable */
import counterTemplate from './counter.html';
import counterEditorTemplate from './counter-editor.html';

function CounterRenderer() {
  return {
    restrict: 'E',
    template: counterTemplate,
    link($scope, element) {
      const refreshData = () => {
        const queryData = $scope.queryResult.getData();
        if (queryData) {
          const rowNumber = $scope.visualization.options.rowNumber - 1;
          const targetRowNumber = $scope.visualization.options.targetRowNumber - 1;
          const counterColName = $scope.visualization.options.counterColName;
          const targetColName = $scope.visualization.options.targetColName;

          if ($scope.visualization.options.countRow) {
            $scope.counterValue = queryData.length;
          } else if (counterColName) {
            $scope.counterValue = queryData[rowNumber][counterColName];
          }
          if (targetColName) {
            $scope.targetValue = queryData[targetRowNumber][targetColName];

            if ($scope.targetValue) {
              $scope.delta = $scope.counterValue - $scope.targetValue;
              $scope.trendPositive = $scope.delta >= 0;
            }
          } else {
            $scope.targetValue = null;
          }
        }
        //Fix for when the data doesnt change but the filter parameter does.
        var tmp = $scope.counterValue;
        $scope.counterValue = 0;
        $scope.counterValue = tmp;
      };
      $scope.refreshData = refreshData;

      //Fixes for visualizations that have been created before this code.
      if($scope.visualization.options.shorten === undefined) {
        $scope.visualization.options.shorten = "false";
      }
      if($scope.visualization.options.currency === undefined) {
        $scope.visualization.options.currency = "false";
      }

      $scope.shorten = JSON.parse($scope.visualization.options.shorten);
      //undefined is there to get the default behavior from angulars number filter.
      $scope.decimals = $scope.shorten ? 1: undefined;
      //If the currency option is set, we want 2 decimals no matter what.
      $scope.decimals = $scope.visualization.options.currency === "false" ? $scope.decimals : 2;

      if($scope.visualization.options.currency === "false"){
        $scope.suffix = "";
      } else {
        $scope.suffix = $scope.visualization.options.currency === "CAD" ? " CAD" : " USD";
      }

      $scope.$watch('visualization.options', refreshData, true);
      $scope.$watch('visualization.options.shorten', refreshData, true);
      $scope.$watch('queryResult && queryResult.getData()', refreshData);
    },
  };
}

function CounterEditor() {
  return {
    restrict: 'E',
    template: counterEditorTemplate,
  };
}


export default function (ngModule) {
  ngModule.directive('counterEditor', CounterEditor);
  ngModule.directive('counterRenderer', CounterRenderer);

  ngModule.config((VisualizationProvider) => {
    const renderTemplate =
        '<counter-renderer ' +
        'options="visualization.options" query-result="queryResult">' +
        '</counter-renderer>';

    const editTemplate = '<counter-editor></counter-editor>';
    const defaultOptions = {
      counterColName: 'counter',
      rowNumber: 1,
      targetRowNumber: 1,
    };

    VisualizationProvider.registerVisualization({
      type: 'COUNTER',
      name: 'Counter',
      renderTemplate,
      editorTemplate: editTemplate,
      defaultOptions,
    });
  });
}
