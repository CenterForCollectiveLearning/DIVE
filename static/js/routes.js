app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/data_view', {
      templateUrl: 'static/html/data_view.html',
      controller: 'DatasetListCtrl',
      activetab: 'data_view',
      resolve: {
        initialData: function(DataService) {
          return DataService.promise;
        }
      }
    }).
    when('/edit_ontology', {
      templateUrl: 'static/html/edit_ontology.html',
      controller: 'OntologyEditorCtrl',
      activetab: 'edit_ontology',
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
      controller: 'CreatVizCtrl',
      activetab: 'create_viz',
      resolve: {
        initialData: function(DataService) {
          return DataService.promise;
        },
        overlapService: function(OverlapService) {
          return OverlapService.promise;
        }
      }
    }).
    otherwise({
      redirectTo: '/data_view'
    });
}]);
