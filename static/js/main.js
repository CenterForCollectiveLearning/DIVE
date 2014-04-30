var app;

window.SC = function(selector) {
  return angular.element(selector).scope();
};

app = angular.module('engineApp', ['d3', 'ngRoute', 'engineControllers']);

app.config(function($interpolateProvider) {
  return $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
});
