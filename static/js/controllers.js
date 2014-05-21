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

controllers.controller('CreateVizCtrl', function($scope, $http, DataService, OverlapService, VizDataService, VizFromOntologyService) {

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
      attrs: dataset.column_attrs,
      unique_cols: dataset.unique_cols
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


  // TODO Pare down this UI stuff
  $scope.initNetwork = initNetwork;

  // TODO Don't be redundant
  $scope.vizType = 'treemap';
  $scope.selected_vizType = 'treemap';
  $scope.selected_vizType_index = 1;
  $scope.select_vizType = function(index) {
    $scope.selected_vizType = $scope.vizTypes[index].name;
    $scope.vizType = $scope.vizTypes[index].name;
    $scope.selected_vizType_index = index;

    // TODO: There must be a better way to do pretty much an ng-if on an object
    $scope.vizSpecs = $scope.allVizSpecs[$scope.selected_vizType];
    console.log('Selected vizType:', $scope.vizType);
  };

  $scope.selected_vizSpec_index = 0;
  $scope.select_vizSpec = function(index) {
    $scope.selected_vizSpec_index = index;
  };

  // TODO Abstract these to a global client-side ID reference
  $scope.getDatasetTitle = function(dataset_id) {
    return datasets[dataset_id].title;
  }

  $scope.getColumnName = function(dataset_id, column_id) {
    return datasets[dataset_id].column_attrs[column_id].name;
  }

  displayVisualization = function(vizSpec) {
    $http.get('get_treemap_data', {
      params: {
        condition: vizSpec.condition,
        aggregate: vizSpec.aggregate,
        query: '*',
        groupBy: vizSpec.groupBy
      }
    }).success(function(result) {
      $scope.$apply(function() {
        $scope.vizData = result.data.result;
      })
    })
  }

  // Correct way to handle argument passing to async service
  $scope.vizFromOntology = function() {
    // TODO Move parsing logic to server side...or just have it in the correct format anyways
    VizFromOntologyService.promise($scope.initNetwork, function(data) {
      var visualizations = data.visualizations;
      var vizTypes = []
      for (var visualization in visualizations) {
        vizTypes.push({
          'name': visualization,
          'count': visualizations[visualization].length
        })
      }
      $scope.vizTypes = vizTypes;
      $scope.vizSpecs = visualizations[$scope.selected_vizType];
      $scope.allVizSpecs = visualizations;
      console.log("vizSpecs:", $scope.vizSpecs)
    })
  }
  $scope.vizFromOntology()

  $scope.setVizData = function(vizSpec) {
    $scope.vizSpec = vizSpec;
    VizDataService.promise(vizSpec, function(result) {
      $scope.vizData = result.result;
    })
  }
});
