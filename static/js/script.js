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
      controller: 'DatasetListCtrl',
      resolve: {
        initialData: function(initialDataService) {
          return initialDataService.promise;
        }
      }
    }).
    when('/edit_ontology', {
      templateUrl: 'static/html/edit_ontology.html',
      controller: 'DatasetListCtrl'
    }).
    when('/visualize', {
      templateUrl: 'static/html/create_viz.html',
      controller: 'DatasetListCtrl'
    }).
    otherwise({
      redirectTo: '/data_view'
    });
}]);

app.service('initialDataService', function($http) {
  var myData = [];

  var promise = $http.get('get_test_datasets').success(function(data) {
    for (var i=0; i<data.samples.length; i++) {
      var d = data.samples[i];
      d.title = d.filename;
      d.colAttrs = [];
      for (var j=0; j<d.cols; j++) {
        d.colAttrs[j] = { name: d.header[j], type: d.types[j]};
      }
      myData.push(d);
    }
  })

  return {
    promise: promise,
    getData: function() {
      return myData;
    }
  }
})