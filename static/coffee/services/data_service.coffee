# Container for data services
diveApp.service "AllProjectsService", ($http) ->
  promise: (userName, callback) ->
   $http.get('/api/project',
      params:
        user_name: userName
    ).success((result) -> 
      callback(result)
    )

# TODO Eventually deprecate this in favor of real session handling
engineApp.service "ProjectIDService", ($http, $stateParams, $rootScope) ->
  promise: (formattedProjectTitle) ->
    console.log("Requesting projectID for project title:", formattedProjectTitle)
    $http.get("/api/getProjectID",
      params:
        formattedProjectTitle: formattedProjectTitle
    ).success((pID) ->
      $rootScope.pID = pID
    )

# Dataset Samples
engineApp.service "DataService", ($http, $rootScope) ->
  promise: (callback) ->
    $http.get("/api/data",
      params:
        pID: $rootScope.pID
        sample: true
    ).success((data) ->
      callback(data.datasets)
    )

engineApp.service "PropertyService", ($http, $rootScope) ->
  promise: (callback) ->
    $http.get("/api/property",
      params:
        pID: $rootScope.pID
    ).success((data) -> 
      callback(data)
    )

engineApp.service "VizFromOntologyService", ($http) ->
  # TODO Pass in vizType parameter
  promise: (initNetwork, callback) ->
    $.ajax(
      url: "get_visualizations_from_ontology"
      type: "POST"
      data: JSON.stringify(initNetwork)
      cache: false
      processData: false
      contentType: false
    ).success (result) ->
      callback result

engineApp.service "VizDataService", ($http) ->
  # TODO Generalize service for other vizTypes
  promise: (vizSpec, callback) ->
    $http.get("get_treemap_data",
      params:
        condition: vizSpec.condition
        aggregate: vizSpec.aggregate
        query: "*"
        groupBy: vizSpec.groupBy
    ).success (result) ->
      callback result
