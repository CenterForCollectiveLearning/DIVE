diveApp.config([
  "$routeProvider", ($routeProvider) ->
    $routeProvider
    .when("/",
      templateUrl: "static/views/landing.html"
      resolve:
        allProjectsService: (AllProjectsService) ->
          AllProjectsService.promise
    )
    .when("/:formattedUserName/:formattedProjectTitle",  # TODO Validate permissions first
      redirectTo: "/:formattedUserName/:formattedProjectTitle/data"
    )
    .when("/:formattedUserName/:formattedProjectTitle/data",
      templateUrl: "static/views/data_view.html"
      controller: "DatasetListCtrl"
      resolve:
        projectIDService: (ProjectIDService) ->
          ProjectIDService.promise
        # This is dependent on projectIDService
        # initialData: (DataService) ->
        #   DataService.promise
    )
    .when("/:formattedUserName/:formattedProjectTitle/ontology",
      templateUrl: "static/views/edit_ontology.html"
      controller: "OntologyEditorCtrl"
      resolve:
        projectIDService: (ProjectIDService) ->
          ProjectIDService.promise

        initialData: (DataService) ->
          DataService.promise

        propertyService: (PropertyService) ->
          PropertyService.promise
    )
    .when("/:formattedUserName/:formattedProjectTitle/visualize",
      templateUrl: "static/views/create_viz.html"
      controller: "CreateVizCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise

        propertyService: (PropertyService) ->
          PropertyService.promise

        vizFromOntologyService: (VizFromOntologyService) ->
          VizFromOntologyService.promise

        vizDataService: (VizDataService) ->
          VizDataService.promise
    )
    .when("/:formattedUserName/:formattedProjectTitle/assemble",
      templateUrl: "static/views/assemble_engine.html"
      controller: "AssembleCtrl"
      resolve:
        initialData: (DataService) ->
          DataService.promise

        propertyService: (PropertyService) ->
          PropertyService.promise

        vizFromOntologyService: (VizFromOntologyService) ->
          VizFromOntologyService.promise

        vizDataService: (VizDataService) ->
          VizDataService.promise
    )
    .otherwise(redirectTo: "/")
])