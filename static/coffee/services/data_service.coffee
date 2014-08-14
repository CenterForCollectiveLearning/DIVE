# Container for data services
engineApp.service "DataService", ($http) ->
  myData = []
  promise = $http.get("get_test_datasets").success((data) ->
    
    # var temp = data.samples[1];
    # data.samples[1] = data.samples[2];
    # data.samples[2] = temp;
    myData = data.samples
    return
  )
  promise: promise
  getData: ->
    myData

engineApp.service "OverlapService", ($http) ->
  myData = undefined
  promise = $http.get("get_relationships").success((data) ->
    myData = data
    return
  )
  promise: promise
  getData: ->
    myData

engineApp.service "VizFromOntologyService", ($http) ->
  myData = undefined
  
  # TODO Pass in vizType parameter
  promise = (initNetwork, callback) ->
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

  promise: promise
  getData: ->
    myData

engineApp.service "VizDataService", ($http) ->
  myData = undefined
  
  # TODO Generalize service for other vizTypes
  promise = (vizSpec, callback) ->
    $http.get("get_treemap_data",
      params:
        condition: vizSpec.condition
        aggregate: vizSpec.aggregate
        query: "*"
        groupBy: vizSpec.groupBy
    ).success (result) ->
      callback result
      return

    return

  promise: promise
  getData: ->
    myData
