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

  var nodes = [];
  var edges = [];

  // Populate nodes
  for (var i=0; i<datasets.length; i++) {
    var dataset = datasets[i];
    var node = {
      _id: dataset._id,
      model: dataset.title,
      attrs: dataset.colattrs
    }
    nodes.push(node);
  }

  for (var datasetPair in relnData.hierarchies) {
    var hierarchy = relnData.hierarchies[datasetPair];
    var datasetPairList = datasetPair.split('\t');

    for (var columnPair in hierarchy) {
      var type = hierarchy[columnPair];
      var columnPairList = columnPair.split('\t');

      var edge = {
        source: [datasetPairList[0], columnPairList[1]],
        target: [datasetPairList[1], columnPairList[1]],
        type: type
      }
      edges.push(edge);
    }
  }

  var initNetwork = {
    'nodes': nodes, 
    'edges': edges
  };

  $scope.initNetwork = initNetwork;
});
