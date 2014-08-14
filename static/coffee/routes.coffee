diveApp.config([
  "$routeProvider", ($routeProvider) ->
    $routeProvider
    .when("/",
      templateUrl: "static/views/landing.html"
    )
    .when("/data",
      templateUrl: "static/views/data_view.html"
      controller: "DatasetListCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise
    )
    .when("/ontology",
      templateUrl: "static/views/edit_ontology.html"
      controller: "OntologyEditorCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise

        overlapService: (OverlapService) ->
          OverlapService.promise
    )
    .when("/visualize",
      templateUrl: "static/views/create_viz.html"
      controller: "CreateVizCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise

        overlapService: (OverlapService) ->
          OverlapService.promise

        vizFromOntologyService: (VizFromOntologyService) ->
          VizFromOntologyService.promise

        vizDataService: (VizDataService) ->
          VizDataService.promise
    )
    .when("/assemble",
      templateUrl: "static/views/assemble_engine.html"
      controller: "AssembleEngineCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise

        overlapService: (OverlapService) ->
          OverlapService.promise

        vizFromOntologyService: (VizFromOntologyService) ->
          VizFromOntologyService.promise

        vizDataService: (VizDataService) ->
          VizDataService.promise
    )
    .otherwise(redirectTo: "/")
])