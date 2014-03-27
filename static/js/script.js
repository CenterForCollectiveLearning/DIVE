var app;

window.SC = function(selector) {
  return angular.element(selector).scope();
};

app = angular.module('app', []);

app.config(function($interpolateProvider) {
  return $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
});

app.controller('DatasetListCtrl', function($scope, $http) {
  var files;

  $('#data-file').on('change', function(event) {
    files = event.target.files;
  });

  $('#data-submit').click(function(event) {
    var data = new FormData();
    data.append('dataset', files[0])

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
          $scope.datasets.push(data);
        });
      }
    });
  });

  $scope.select_dataset = function(index) {
    $scope.selected_index = index;
  }

  $scope.datasets = [
    {
      title: "Dataset 1",
      rows: 100,
      cols: 1000,
      type: "CSV"
    }, {
      title: "Dataset 2",
      rows: 150,
      cols: 1500,
      type: "TSV"
    }, {
      cols:3,
      filename:"student.csv",
      rows:6,
      sample:{
        "0":["vikas","student","mit"],
        "1":["kevin","graduate","mit"],
        "2":["alyssa","student","mit"],
        "3":["ben","student","mit"],
        "4":["alice","graduate","mit"],
        "5":["bob","graduate","mit"] },
      type:"csv",
      title:"student.csv"
    },
  ];

  return console.log($scope);
});
