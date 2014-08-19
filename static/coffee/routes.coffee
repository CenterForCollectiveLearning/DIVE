diveApp.config([
  "$routeProvider", ($routeProvider) ->
    $routeProvider
    .when("/",
      templateUrl: "static/views/landing.html"
      resolve:
        allProjectsService: (AllProjectsService) ->
          AllProjectsService.promise
    )
    .when("/:uID/:pID",  # TODO Validate permissions first
      redirectTo: "/:uID/:pID/data"
    )
    .when("/:uID/:pID/data",
      templateUrl: "static/views/data_view.html"
      controller: "DatasetListCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise
    )
    .when("/:uID/:pID/ontology",
      templateUrl: "static/views/edit_ontology.html"
      controller: "OntologyEditorCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise

        overlapService: (OverlapService) ->
          OverlapService.promise
    )
    .when("/:uID/:pID/visualize",
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
    .when("/:uID/:pID/assemble",
      templateUrl: "static/views/assemble_engine.html"
      controller: "AssembleCtrl"
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