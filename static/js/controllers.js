var controllers = angular.module('engineControllers', []);

controllers.controller('DatasetListCtrl', function($scope, $http, DataService) {
  var files;

  $('#data-file').on('change', function(event) {
    files = event.target.files;
  });

  $('#data-submit').click(function(event) {
    var data = new FormData();
    data.append('dataset', files[0]);

    $.ajax({
      url: '/upload',
      type: 'POST',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
    }).success(function(data) {
      if (data.status === "success") {
        delete data['status'];

        // update model with file data
        $scope.$apply(function() {
          data.title = data.filename;
          data.colAttrs = []
          for (var i=0; i<data.cols; i++) {
            data.colAttrs[i] = { name: data.header[i],
                                 type: data.types[i] };
          }
          delete data['header']
          delete data['types']
          $scope.datasets.push(data);
        });
      }
    });
  });

  $scope.selected_index = 0;
  $scope.select_dataset = function(index) {
    $scope.selected_index = index;
  };

  $scope.types = ['int', 'float', 'str'];

  // Initialize datasets
  $scope.datasets = DataService.getData();
});


// TODO Make this controller thin
controllers.controller('OntologyEditorCtrl', function($scope, $http, DataService, OverlapService) {
  // Initialize datasets
  $scope.datasets = DataService.getData();
  // Get non-zero overlaps between columns
  var relnData = OverlapService.getData();

  $scope.overlaps = relnData.overlaps;
  $scope.hierarchies = relnData.hierarchies;
});

controllers.controller('CreatVizCtrl', function($scope, $http, DataService, OverlapService) {

  // Initialize datasets
  var datasets = DataService.getData();
  $scope.datasets = datasets

  var relnData = OverlapService.getData();

  // Probably not the right place to put this
  $scope.overlaps = relnData.overlaps;
  $scope.hierarchies = relnData.hierarchies;

  // TODO Watch changes and propagate changes
  var nodes = [];
  var edges = [];

  // Populate nodes
  for (var i=0; i<datasets.length; i++) {
    var dataset = datasets[i];
    var node = {
      model: dataset.dataset_id,
      attrs: dataset.column_attrs
    }
    nodes.push(node);
  }

  for (var datasetPair in relnData.hierarchies) {
    var hierarchy = relnData.hierarchies[datasetPair];
    var datasetPairList = datasetPair.split('\t');

    for (var columnPair in hierarchy) {
      var type = hierarchy[columnPair];
      var columnPairList = columnPair.split('\t');

      var d =relnData.overlaps[datasetPair][columnPair];
      if (d > 0.5) {
        // Only add edge if overlap
        var edge = {
          source: [parseInt(datasetPairList[0]), parseInt(columnPairList[1])],
          target: [parseInt(datasetPairList[1]), parseInt(columnPairList[1])],
          type: type
        }
        edges.push(edge);
      }
    }
  }

  var initNetwork = {
    'nodes': nodes, 
    'edges': edges
  };

  $scope.initNetwork = initNetwork;

  $scope.selected_vizType = 3;
  $scope.select_vizType = function(index) {
    $scope.selected_vizType = index;
  };

  $scope.selected_vizSpec = 0;
  $scope.select_vizSpec = function(index) {
    $scope.selected_vizSpec = index;
  };

  console.log(datasets);

  $scope.getDatasetTitle = function(dataset_id) {
    return datasets[dataset_id].title;
  }

  $scope.getColumnName = function(dataset_id, column_id) {
    return datasets[dataset_id].column_attrs[column_id].name;
  }

  // TODO Put this into a service
  $.ajax({
      url: 'get_visualizations_from_ontology',
      type: 'POST',
      data: JSON.stringify(initNetwork),
      cache: false,
      processData: false,
      contentType: false,
    }).success(function(data) {
      if (data.status === "success") {

        $scope.$apply(function() {
          var visualizations = data.visualizations;
          var vizTypes = []
          for (var visualization in visualizations) {
            vizTypes.push({
              'name': visualization,
              'count': visualizations[visualization].length
            })
          }
          $scope.vizTypes = vizTypes;
          $scope.vizSpecs = visualizations[visualization];
        });
      }
    });
});
