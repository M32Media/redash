/* eslint-disable */
import multicounterTemplate from './multicounter.html';
import multicounterEditorTemplate from './multicounter-editor.html';
import { language } from '../../i18n'

//Number of counters
const counterNum = 4;

function multicounterRenderer() {
  return {
    restrict: 'E',
    template: multicounterTemplate,
    link($scope, element) {
      const refreshData = () => {
        const queryData = $scope.queryResult.getData();
        if (queryData) {
          var rowNumbers = [];
          var targetRowNumbers = [];
          var counterColNames = [];
          var targetColNames = [];
          for (var i = 0; i < counterNum; i++) {
            rowNumbers.push($scope.visualization.options[i].rowNumber - 1);
            targetRowNumbers.push($scope.visualization.options[i].targetRowNumber - 1);
            counterColNames.push($scope.visualization.options[i].counterColName);
            targetColNames.push($scope.visualization.options[i].targetColName);
          }
          $scope.counterValues = [];
          $scope.targetValues = [];
          $scope.deltas = [];
          $scope.trendsPositive = [];
          for (var i = 0; i < counterNum; i++) {
            if ($scope.visualization.options[i].countRow) {
              $scope.counterValues[i] = queryData.length;
            } else if (counterColNames[i]) {
              $scope.counterValues[i] = queryData[rowNumbers[i]][counterColNames[i]];
            }
            if (targetColNames[i]) {
              $scope.targetValues[i] = queryData[targetRowNumbers[i]][targetColNames[i]];

              if ($scope.targetValues[i]) {
                $scope.deltas[i] = $scope.counterValues[i] - $scope.targetValues[i];
                $scope.trendsPositive[i] = $scope.deltas[i] >= 0;
              }
            } else {
              $scope.targetValues[i] = null;
            }
          }
        }
      };
      $scope.refreshData = refreshData;

      $scope.shortens = [];
      //undefined is there to get the default behavior from angulars number filter.
      $scope.decimals = [];
      //If the currency option is set, we want 2 decimals no matter what.
      $scope.decimals = [];

      $scope.suffixes = [];
      $scope.displayNames = [];
      $scope.actives = [];

      for (var i = 0; i < counterNum; i++) {

        $scope.displayNames.push(language.getCurrentLanguage() === "Fr" ? $scope.visualization.options[i].counterNameFr: $scope.visualization.options[i].counterName);
        $scope.actives.push($scope.visualization.options[i].active === "true" ? "block": "none");
        $scope.shortens.push($scope.visualization.options[i].shorten === "true" ? true: false);
        $scope.decimals.push($scope.shortens[i] ? 1: undefined);
        $scope.decimals[i] = $scope.visualization.options[i].currency === "false" ? $scope.decimals[i] : 2;

        if($scope.visualization.options.currency === "false" || $scope.counterValue === null || $scope.counterValue === undefined){
          $scope.suffixes.push("");
        } else {
          $scope.suffixes.push($scope.visualization.options[i].currency === "CAD" ? " CAD" : " USD");
        }
        $scope.$watch('visualization.options['+1+']', refreshData, true);
      }

      $scope.$watch('queryResult && queryResult.getData()', refreshData);
    },
  };
}

function multicounterEditor() {
  return {
    restrict: 'E',
    template: multicounterEditorTemplate,
  };
}


export default function (ngModule) {
  ngModule.directive('multicounterEditor', multicounterEditor);
  ngModule.directive('multicounterRenderer', multicounterRenderer);

  ngModule.config((VisualizationProvider) => {
    const renderTemplate =
        '<multicounter-renderer ' +
        'options="visualization.options" query-result="queryResult">' +
        '</multicounter-renderer>';

    const editTemplate = '<multicounter-editor></multicounter-editor>';
    var defaultOptions = [];
    for (var i = 0; i < counterNum; i++) {
      defaultOptions.push({
        counterColName: 'subCounter ' + (i+1),
        rowNumber: 1,
        currency: "false",
        shorten: "false",
        //hack because angular doesn't do what I want it to.
        active: "true",
        counterName: "Counter #" + i,
        counterNameFr: "Compteur #" + i,
      });
    }
    VisualizationProvider.registerVisualization({
      type: 'MULTICOUNTER',
      name: 'Multicounter',
      renderTemplate,
      editorTemplate: editTemplate,
      defaultOptions,
    });
  });
}
