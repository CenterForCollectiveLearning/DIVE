diveApp.service("AllProjectsService", function($http, $rootScope) {
  return {
    promise: function(userName, callback) {
      console.log("[REQUEST] all projects for user:", userName);
      return $http.get('http://localhost:8888/api/project', {
        params: {
          user_name: userName
        }
      }).success(function(result) {
        return callback(result);
      });
    }
  };
});

engineApp.service("ProjectIDService", function($http, $stateParams, $rootScope) {
  return {
    promise: function(formattedProjectTitle) {
      console.log("[REQUEST] projectID for project title:", formattedProjectTitle);
      return $http.get("http://localhost:8888/api/getProjectID", {
        params: {
          formattedProjectTitle: formattedProjectTitle
        }
      }).success(function(pID) {
        console.log("[DATA] projectID:", pID);
        return $rootScope.pID = pID;
      });
    }
  };
});

engineApp.service("DataService", function($http, $rootScope) {
  return {
    promise: function(callback) {
      console.log("[REQUEST] data for pID", $rootScope.pID);
      return $http.get("http://localhost:8888/api/data", {
        params: {
          pID: $rootScope.pID,
          sample: true
        }
      }).success(function(data) {
        console.log("[DATA] datasets:", data);
        return callback(data.datasets);
      });
    }
  };
});

engineApp.service("PropertyService", function($http, $rootScope) {
  return {
    promise: function(callback) {
      console.log("[REQUEST] properties for pID", $rootScope.pID);
      return $http.get("http://localhost:8888/api/property", {
        params: {
          pID: $rootScope.pID
        }
      }).success(function(data) {
        console.log("[DATA] properties:", data);
        return callback(data);
      });
    }
  };
});

engineApp.service("SpecificationService", function($http, $rootScope) {
  return {
    promise: function(callback) {
      console.log("[REQUEST] specifications for pID", $rootScope.pID);
      return $http.get("http://localhost:8888/api/specification", {
        params: {
          pID: $rootScope.pID
        }
      }).success(function(data) {
        console.log("[DATA] specifications:", data);
        return callback(data);
      });
    }
  };
});

engineApp.service("ConditionalDataService", function($http, $rootScope) {
  return {
    promise: function(type, spec, callback) {
      console.log('[REQUEST] Conditoinal Data for Type', type, 'and Specification ', spec);
      return $http.get("http://localhost:8888/api/conditional_data", {
        params: {
          pID: $rootScope.pID,
          type: type,
          spec: spec
        }
      }).success(function(data) {
        console.log("[DATA] Conditional Data:", data);
        return callback(data);
      });
    }
  };
});

engineApp.service("VizDataService", function($http, $rootScope) {
  return {
    promise: function(type, spec, callback) {
      console.log('[REQUEST] Viz Data for Type', type, 'and Specification ', spec);
      return $http.get("http://localhost:8888/api/visualization_data", {
        params: {
          pID: $rootScope.pID,
          type: type,
          spec: spec
        }
      }).success(function(data) {
        console.log("[DATA] Viz Data:", data);
        return callback(data);
      });
    }
  };
});
