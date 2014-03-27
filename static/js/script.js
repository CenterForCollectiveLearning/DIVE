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
          data.attrs = []
          for (i=0; i<data.cols; i++) {
            data.attrs[i] = { name:"name_"+i,
                              type:"type_"+i };
          }
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
      type: "CSV",
    }, {
      title: "Dataset 2",
      rows: 150,
      cols: 1500,
      type: "TSV",
    }, {
      title:"student.csv",
      rows:6,
      cols:3,
      type:"csv",
      filename:"student.csv",
      sample: {
        "0":["vikas","student","mit"],
        "1":["kevin","graduate","mit"],
        "2":["alyssa","student","mit"],
        "3":["ben","student","mit"],
        "4":["alice","graduate","mit"],
        "5":["bob","graduate","mit"] },
      attrs: [
        { name:"name_0",
          type:"type_0" },
        { name:"name_1",
          type:"type_1" },
        { name:"name_2",
          type:"type_2" }, ],
    },
  ];

  return console.log($scope);
});
