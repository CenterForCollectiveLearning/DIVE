app.service('DataService', function($http) {
  var myData = [];

  var promise = $http.get('get_test_datasets').success(function(data) {
    for (var i=0; i<data.samples.length; i++) {
      var d = data.samples[i];
      d.title = d.filename;
      d.colAttrs = [];
      for (var j=0; j<d.cols; j++) {
        d.colAttrs[j] = {
          name: d.header[j],
          type: d.types[j]};
        }
        delete d['header']
        delete d['types']
        myData.push(d);
      }
    })

  return {
    promise: promise,
    getData: function() {
      return myData;
    }
  }
})

app.service('overlapService', function($http) {
  var myData = null;

  var promise = $http.get('get_relationships').success(function(data) {
    myData = data['result']
    })

  return {
    promise: promise,
    getData: myData
  }
})
