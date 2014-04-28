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