// Container for data services

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

app.service('VizFromOntologyService', function($http) {
  var myData;

  var promise = function(initNetwork, callback) {
    $.ajax({
      url: 'get_visualizations_from_ontology',
      type: 'POST',
      data: JSON.stringify(initNetwork),
      cache: false,
      processData: false,
      contentType: false,
    }).success(function(result) {
      callback(result);
    });
  }

  return {
    promise: promise,
    getData: function() { 
      return myData;
    }
  }
})

app.service('VizDataService', function($http) {
  var myData;

  // TODO Generalize service for other vizTypes
  var promise = function(vizSpec, callback) {
    $http.get('get_treemap_data', {
      params: {
        condition: vizSpec.condition,
        aggregate: vizSpec.aggregate,
        query: '*',
        groupBy: vizSpec.groupBy
      }
    }).success(function(result) {
      callback(result);
    })
  }

  return {
    promise: promise,
    getData: function() { 
      return myData;
    }
  }
})