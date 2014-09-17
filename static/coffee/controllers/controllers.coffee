controllers = angular.module("engineControllers", ['ngAnimate'])

controllers.controller "CreateProjectFormController", ($scope, $http, $location) ->
  $scope.create_project = ->
    params = {
      title: $scope.newProjectData.title
      description: $scope.newProjectData.description
      user_name: $scope.user.userName
    }
    $http(
      method: 'POST'
      url: 'http://localhost:8888/api/project'
      data: params
      transformRequest: objectToQueryString
      headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    ).success((data, status) ->
      $location.path($scope.user.userName + '/' + data.formatted_title)
    ).error((data, status) ->
      # TODO Catch other types of errors
      $scope.titleTaken = true
      )

# Landing page project list / navigation
controllers.controller "ProjectListCtrl", ($scope, $http, $location, $rootScope, AllProjectsService) ->
  $scope.newProjectData = {}
  $scope.newProject = false
  $scope.user = {
    userName: 'demo-user'
    displayName: 'Demo User'
  }

  AllProjectsService.promise($scope.user.userName, (projects) ->
    $scope.projects = projects)

  $scope.select_project = (pID) ->
    $rootScope.pID = pID

  $scope.new_project_toggle = ->
    $scope.newProject = !$scope.newProject

controllers.controller "OverviewCtrl", ($scope, $rootScope) ->
  # TODO: How to deal with same method?
  DeleteProjectService

controllers.controller "PaneToggleCtrl", ($scope) ->
  $scope.leftClosed = false
  $scope.rightClosed = false
  $scope.toggleLeft = -> $scope.leftClosed = !$scope.leftClosed
  $scope.toggleRight = -> $scope.rightClosed = !$scope.rightClosed

# Stateful navigation (tabs)
controllers.controller "TabsCtrl", ($scope, $state, $rootScope, $stateParams) ->
  $scope.tabs = [
    {
      route: "engine.data"
      label: "1. Manage Datasets"
    }
    {
      route: "engine.ontology"
      label: "2. Edit Ontology"
    }
    {
      route: "engine.visualize"
      label: "3. Select Visualizations"
    }
    {
      route: "engine.assemble"
      label: "4. Assemble Engine"
    }
  ]

controllers.controller "DatasetListCtrl", ($scope, $rootScope, projectID, $http, $upload, $timeout, $stateParams, DataService) ->
  $scope.selectedIndex = 0
  $scope.currentPane = 'left'

  $scope.options = [
    {
      label: 'Upload File'
      inactive: false
    },
    {
      label: 'Connect to Database'
      inactive: true
    },
    {
      label: 'Connect to API'
      inactive: true
    },
    {
      label: 'Search DIVE Datasets'
      inactive: true
    }
  ]
  $scope.select_option = (index) ->
    $scope.currentPane = 'left'
    # Inactive options (for demo purposes)
    unless $scope.options[index].inactive
      $scope.selectedIndex = index

  $scope.select_dataset = (index) ->
    $scope.currentPane = 'right'
    $scope.selectedIndex = index

  $scope.types = [ "int", "float", "str" ]

  # Initialize datasets
  DataService.promise((datasets) ->
    $scope.datasets = datasets
  )

  ###############
  # File Upload
  ###############
  $scope.onFileSelect = ($files) ->
    i = 0
    while i < $files.length
      file = $files[i]
      $scope.upload = $upload.upload(
        url: "/api/upload"
        data:
          pID: $rootScope.pID
        file: file
      ).progress((evt) ->
        console.log "Percent loaded: " + parseInt(100.0 * evt.loaded / evt.total)
        return
      ).success((data, status, headers, config) ->
        # file is uploaded successfully
        $scope.datasets.push(data)
      )
      i++
  ###############
  # File Deletion
  ###############
  $scope.removeDataset = (dID) ->
    console.log('Removing dataset, dID:', dID)
    $http.delete('/api/data',
      params:
        pID: $rootScope.pID
        dID: dID
    ).success((result) ->
      deleted_dIDs = result
      newDatasets = []
      for dataset in $scope.datasets
        unless dataset.dID in deleted_dIDs
          newDatasets.push(dataset)
      $scope.datasets = newDatasets
    )

controllers.controller "OntologyEditorCtrl", ($scope, $http, DataService, PropertyService) ->
  # Interface elements
  $scope.selectedLeftIndex = 0
  $scope.selectedRightIndex = 0
  $scope.currentPane = 'left'
  $scope.layoutOptions = [
    {
      label: 'Object'
      inactive: false
    },
    {
      label: 'List'
      inactive: true
    },
    {
      label: 'Hierarchy'
      inactive: true
    }
  ]
  $scope.editOptions = [
    {
      label: 'Add'
      inactive: true
    },
    {
      label: 'Edit'
      inactive: true
    },
    {
      label: 'Delete'
      inactive: true
    }
  ]
  $scope.select_left_option = (index) ->
    $scope.selectedLeftIndex = index

  $scope.select_right_option = (index) ->
    $scope.selectedRightIndex = index


  # Initialize datasets
  DataService.promise((datasets) ->
    $scope.datasets = datasets
    console.log('Datasets dIDs:', _.pluck($scope.datasets, 'dID'))
  )

  $scope.loading = true

  PropertyService.promise((properties) ->
    $scope.loading = false
    $scope.properties = properties
    $scope.overlaps = properties.overlaps
    $scope.hierarchies = properties.hierarchies
  )

controllers.controller "AssembleCtrl", ($scope, $http) ->
  return

# TODO Make this controller thinner!
controllers.controller "CreateVizCtrl", ($scope, $http, DataService, PropertyService, VizDataService, SpecificationService) ->

  # Initialize datasets
  DataService.promise((datasets) ->
    console.log('Datasets dIDs:', _.pluck($scope.datasets, 'dID'))
    $scope.datasets = datasets
  )#

  PropertyService.promise((properties) ->
    $scope.properties = properties
    $scope.overlaps = properties.overlaps
    $scope.hierarchies = properties.hierarchies
  )

  $scope.selected_type = 0
  $scope.selected_spec = 0
  SpecificationService.promise((specs) ->
    $scope.types = ({'name': k, 'length': v.length} for k, v of specs)
    $scope.allSpecs = specs
    $scope.specs = $scope.allSpecs[$scope.types[$scope.selected_type].name]
  )

  type_name_from_index = (index) ->
    $scope.types[index].name

  $scope.select_type = (index) ->
    $scope.selected_type = index
    $scope.specs = $scope.allSpecs[$scope.types[$scope.selected_type].name]

  $scope.select_spec = (index) ->
    $scope.selected_spec = index
    spec = $scope.specs[index]
    type = $scope.types[$scope.selected_type].name
    console.log("Selected vizspec", spec)
    VizDataService.promise(type, spec, (result) ->
      $scope.vizData = result
    )

  #   # TODO Move parsing logic to server side...or just have it in the correct format anyways
  #   VizFromOntologyService.promise $scope.initNetwork, (data) ->
  #     visualizations = data.visualizations
  #     vizTypes = []
  #     for visualization of visualizations
  #       vizTypes.push
  #         name: visualization
  #         count: visualizations[visualization].length

  #     $scope.vizTypes = vizTypes
  #     $scope.vizSpecs = visualizations[$scope.vizType]
  #     $scope.allVizSpecs = visualizations
  #     return

  #   return

  # $scope.vizFromOntology()
  # $scope.setVizData = (vizSpec) ->
  #   $scope.vizSpec = vizSpec
  #   VizDataService.promise vizSpec, (result) ->
  #     $scope.vizData = result.result