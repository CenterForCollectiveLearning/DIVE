app.service('DataService', function($http) {
  var myData = [];

  var promise = $http.get('get_test_datasets').success(function(data) {
    // Hardcoded ordering -- BAD
    // TODO Develop algo to minimize edge-crossings
    var temp = data.samples[2];
    data.samples[2] = data.samples[1];
    data.samples[1] = temp;

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

    // Parsing input -- not necessary for now
    // var initialOverlaps = data['overlaps'];
    // var initialHierarchy = data['hierarchies'];
    // var parsedResult = {};

    // // Parse overlap return
    // for (var datasetPair in initialResult) {
    //   var interDatasetOverlaps = {}

    //   var columnPairs = initialResult[datasetPair];
    //   for (var columnPair in columnPairs) {
    //     interDatasetOverlaps[columnPair.split('\t')] = columnPairs[columnPair];
    //   }
    //   parsedResult[datasetPair.split('\t')] = interDatasetOverlaps;
    // }

    myData = data;
  })

  return {
    promise: promise,
    getData: function() { 
      return myData;
    }
  }
})
