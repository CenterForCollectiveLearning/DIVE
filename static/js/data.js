app.service('DataService', function($http) {
  var myData = [];

  var promise = $http.get('get_test_datasets').success(function(data) {
    myData = data.samples;
    })

  return {
    promise: promise,
    getData: function() {
      return myData;
    }
  }
})

app.service('OverlapService', function($http) {
  var myData;

  var promise = $http.get('get_relationships').success(function(data) {
    myData = data;
  })

  return {
    promise: promise,
    getData: function() { 
      return myData;
    }
  }
})

app.service('VizDataService', function($http) {
  var myData;

  var promise = $http.get('get_treemap_data').success(function(data) {
    myData = data;
  })

  return {
    promise: promise,
    getData: function() { 
      return myData;
    }
  }
})
