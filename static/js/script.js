var app;

window.SC = function(selector) {
  return angular.element(selector).scope();
};

app = angular.module('engineApp', ['ngRoute', 'engineControllers']);

app.config(function($interpolateProvider) {
  return $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
});

app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/data_view', {
      templateUrl: 'static/html/data_view.html',
      controller: 'DatasetListCtrl'
    }).
    otherwise({
      redirectTo: '/data_view'
    });
}]);
