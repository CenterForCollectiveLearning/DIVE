// Generated by CoffeeScript 1.6.3
(function() {
  engineApp.service("DataService", function($http) {
    var myData, promise;
    myData = [];
    promise = $http.get("get_test_datasets").success(function(data) {
      myData = data.samples;
    });
    return {
      promise: promise,
      getData: function() {
        return myData;
      }
    };
  });

  engineApp.service("OverlapService", function($http) {
    var myData, promise;
    myData = void 0;
    promise = $http.get("get_relationships").success(function(data) {
      myData = data;
    });
    return {
      promise: promise,
      getData: function() {
        return myData;
      }
    };
  });

  engineApp.service("VizFromOntologyService", function($http) {
    var myData, promise;
    myData = void 0;
    promise = function(initNetwork, callback) {
      $.ajax({
        url: "get_visualizations_from_ontology",
        type: "POST",
        data: JSON.stringify(initNetwork),
        cache: false,
        processData: false,
        contentType: false
      }).success(function(result) {
        callback(result);
      });
    };
    return {
      promise: promise,
      getData: function() {
        return myData;
      }
    };
  });

  engineApp.service("VizDataService", function($http) {
    var myData, promise;
    myData = void 0;
    promise = function(vizSpec, callback) {
      $http.get("get_treemap_data", {
        params: {
          condition: vizSpec.condition,
          aggregate: vizSpec.aggregate,
          query: "*",
          groupBy: vizSpec.groupBy
        }
      }).success(function(result) {
        callback(result);
      });
    };
    return {
      promise: promise,
      getData: function() {
        return myData;
      }
    };
  });

}).call(this);
