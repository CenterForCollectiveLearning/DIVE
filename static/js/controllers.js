var controllers = angular.module('engineControllers', []);

controllers.controller('DatasetListCtrl', function($scope, $http, initialDataService) {
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
          data.attrs = []
          for (var i=0; i<data.cols; i++) {
            data.attrs[i] = { name:"name_"+i,
                              type:"type_"+i };
          }
          $scope.datasets.push(data);
        });
      }
    });
  });

  $scope.selected_index = 0;
  $scope.select_dataset = function(index) {
    $scope.selected_index = index;
    console.log()
  }

  $scope.datasets = initialDataService.getData();
  return console.log($scope);
});
