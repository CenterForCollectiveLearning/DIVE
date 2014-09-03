# Container for data services
diveApp.service "AllProjectsService", ($http) ->
  myProjects = []
  promise: (userName, callback) ->
   $http.get('/api/project',
      params:
        user_name: userName
    ).success((result) -> 
      callback(result)
    )
  getProjects: -> myProjects

# TODO Eventually deprecate this in favor of real session handling
engineApp.service "ProjectIDService", ($http, $rootScope, $route) ->
  promise: $http.get("/api/getProjectID",
    params:
      formattedProjectTitle: $route.current.params.formattedProjectTitle
  ).success((pID) ->
    # TODO Error handling
    $rootScope.pID = pID
  )

# Dataset Samples
engineApp.service "DataService", ($http, $rootScope) ->
  console.log('DataService', $rootScope.pID)
  myData = []
  promise: (callback) ->
    $http.get("/api/data",
      params:
        pID: $rootScope.pID
        sample: true
    ).success((data) ->
      callback data.datasets
    )
  getData: -> myData

engineApp.service "PropertyService", ($http, $rootScope) ->
  myData = undefined
  promise: (callback) ->
    $http.get("/api/property",
      params:
        pID: $rootScope.pID
    ).success((data) -> 
      console.log('Property service success!')
      console.log('Properties', data)
      callback data
    )
  getData: -> myData

engineApp.service "VizFromOntologyService", ($http) ->
  myData = undefined
  
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
      return

    return

  getData: -> myData

engineApp.service "VizDataService", ($http) ->
  myData = undefined
  
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
  getData: -> myData
