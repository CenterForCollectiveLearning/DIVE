diveApp.service("AllProjectsService", function($http, $rootScope) {
  return {
    promise: function(userName, callback) {
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
      console.log("Requesting projectID for project title:", formattedProjectTitle);
      return $http.get("http://localhost:8888/api/getProjectID", {
        params: {
          formattedProjectTitle: formattedProjectTitle
        }
      }).success(function(pID) {
        console.log("Resolved projectID:", pID);
        return $rootScope.pID = pID;
      });
    }
  };
});

engineApp.service("DataService", function($http, $rootScope) {
  return {
    promise: function(callback) {
      return $http.get("http://localhost:8888/api/data", {
        params: {
          pID: $rootScope.pID,
          sample: true
        }
      }).success(function(data) {
        return callback(data.datasets);
      });
    }
  };
});

engineApp.service("PropertyService", function($http, $rootScope) {
  return {
    promise: function(callback) {
      return $http.get("http://localhost:8888/api/property", {
        params: {
          pID: $rootScope.pID
        }
      }).success(function(data) {
        return callback(data);
      });
    }
  };
});

engineApp.service("SpecificationService", function($http, $rootScope) {
  return {
    promise: function(callback) {
      return $http.get("http://localhost:8888/api/specification", {
        params: {
          pID: $rootScope.pID
        }
      }).success(function(data) {
        return callback(data);
      });
    }
  };
});

engineApp.service("VizDataService", function($http, $rootScope) {
  return {
    promise: function(type, spec, callback) {
      console.log('In VizDataService', type, spec);
      return $http.get("http://localhost:8888/api/visualization_data", {
        params: {
          pID: $rootScope.pID,
          type: type,
          spec: spec
        }
      }).success(function(result) {
        return callback(result);
      });
    }
  };
});
