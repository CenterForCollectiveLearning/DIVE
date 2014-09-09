diveApp.config(($stateProvider, $urlRouterProvider) ->
  $urlRouterProvider.otherwise("/")

  $stateProvider
    .state('landing',
      url: '/'
      templateUrl: 'static/views/landing.html'
      resolve:
        allProjectsService: (AllProjectsService) -> AllProjectsService.promise
    )
    .state('engine',
      url: '/:formattedUserName/:formattedProjectTitle'
      templateUrl: 'static/views/project.html'
      resolve:
        formattedUserName: ($stateParams) -> $stateParams.formattedUserName
        formattedProjectTitle: ($stateParams) -> $stateParams.formattedProjectTitle
        projectID: ($stateParams, ProjectIDService) -> ProjectIDService.promise($stateParams.formattedProjectTitle)
    )
    .state('engine.data'
      url: '/data'
      templateUrl: 'static/views/data_view.html'
      controller: 'DatasetListCtrl'
      resolve: 
        initialData: (DataService) -> DataService.promise
    )
    .state('engine.ontology'
      url: '/ontology'
      templateUrl: 'static/views/edit_ontology.html'
      controller: 'OntologyEditorCtrl'
      resolve:
        initialData: (DataService) -> DataService.promise
        propertyService: (PropertyService) -> PropertyService.promise
    )
    .state('engine.visualize'
      url: '/visualize'
      templateUrl: 'static/views/create_viz.html'
      controller: 'CreateVizCtrl'
      resolve:
        initialData: (DataService) -> DataService.promise
        propertyService: (PropertyService) -> PropertyService.promise
        specificationService: (SpecificationService) -> SpecificationService.promise
        vizDataService: (VizDataService) -> VizDataService.promise
    )
    .state('engine.assemble'
      url: '/assemble'
      templateUrl: 'static/views/assemble_engine.html'
      controller: 'AssembleCtrl'
    )
  )

# diveApp.config([
#   "$routeProvider", ($routeProvider) ->
#     $routeProvider
#     .when("/",
#       templateUrl: "static/views/landing.html"
#       resolve:
#         allProjectsService: (AllProjectsService) ->
#           AllProjectsService.promise
#     )
#     .when("/:formattedUserName/:formattedProjectTitle",  # TODO Validate permissions first
#       redirectTo: "/:formattedUserName/:formattedProjectTitle/data"
#     )
#     .when("/:formattedUserName/:formattedProjectTitle/data",
#       templateUrl: "static/views/data_view.html"
#       controller: "DatasetListCtrl"
#       resolve:
#         projectIDService: (ProjectIDService) ->
#           ProjectIDService.promise
#         # This is dependent on projectIDService
#         # initialData: (DataService) ->
#         #   DataService.promise
#     )
#     .when("/:formattedUserName/:formattedProjectTitle/ontology",
#       templateUrl: "static/views/edit_ontology.html"
#       controller: "OntologyEditorCtrl"
#       resolve:
#         projectIDService: (ProjectIDService) ->
#           ProjectIDService.promise

#         initialData: (DataService) ->
#           DataService.promise

#         propertyService: (PropertyService) ->
#           PropertyService.promise
#     )
#     .when("/:formattedUserName/:formattedProjectTitle/visualize",
#       templateUrl: "static/views/create_viz.html"
#       controller: "CreateVizCtrl"
#       resolve:
#         initialData: (DataService) ->
#           DataService.promise

#         propertyService: (PropertyService) ->
#           PropertyService.promise

#         vizFromOntologyService: (VizFromOntologyService) ->
#           VizFromOntologyService.promise

#         vizDataService: (VizDataService) ->
#           VizDataService.promise
#     )
#     .when("/:formattedUserName/:formattedProjectTitle/assemble",
#       templateUrl: "static/views/assemble_engine.html"
#       controller: "AssembleCtrl"
#       resolve:
#         initialData: (DataService) ->
#           DataService.promise

#         propertyService: (PropertyService) ->
#           PropertyService.promise

#         vizFromOntologyService: (VizFromOntologyService) ->
#           VizFromOntologyService.promise

#         vizDataService: (VizDataService) ->
#           VizDataService.promise
#     )
#     .otherwise(redirectTo: "/")
# ])