// Generated by CoffeeScript 1.6.3
(function() {
  var app;

  window.SC = function(selector) {
    return angular.element(selector).scope();
  };

  app = angular.module('app', []);

  app.config(function($interpolateProvider) {
    return $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
  });

  app.controller('DatasetListCtrl', function($scope) {
    $scope.datasets = [
      {
        title: "Dataset 1",
        rows: 100,
        cols: 1000,
        type: "CSV"
      }, {
        title: "Dataset 2",
        rows: 150,
        cols: 1500,
        type: "TSV"
      }
    ];
    return console.log($scope);
  });

}).call(this);
