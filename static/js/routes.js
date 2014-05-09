app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/data_view', {
      templateUrl: 'static/html/data_view.html',
      controller: 'DatasetListCtrl',
      resolve: {
        initialData: function(DataService) {
          return DataService.promise;
        }
      }
    }).
    when('/edit_ontology', {
      templateUrl: 'static/html/edit_ontology.html',
      controller: 'OntologyEditorCtrl',
      resolve: {
        initialData: function(DataService) {
          return DataService.promise;
        },
        overlapService: function(OverlapService) {
          return OverlapService.promise;
        }
      }
    }).
    when('/visualize', {
      templateUrl: 'static/html/create_viz.html',
      controller: 'CreateVizCtrl',
      resolve: {
        initialData: function(DataService) {
          return DataService.promise;
        },
        overlapService: function(OverlapService) {
          return OverlapService.promise;
        },
        vizFromOntologyService: function(VizFromOntologyService) {
          return VizFromOntologyService.promise;
        },
        vizDataService: function(VizDataService) {
          return VizDataService.promise;
        }
      }
    }).
    otherwise({
      redirectTo: '/data_view'
    });
}]);
