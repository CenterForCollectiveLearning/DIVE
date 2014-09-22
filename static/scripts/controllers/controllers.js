var controllers,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

controllers = angular.module("engineControllers", ['ngAnimate']);

controllers.controller("CreateProjectFormController", function($scope, $http, $location) {
  return $scope.create_project = function() {
    var params;
    params = {
      title: $scope.newProjectData.title,
      description: $scope.newProjectData.description,
      user_name: $scope.user.userName
    };
    return $http({
      method: 'POST',
      url: 'http://localhost:8888/api/project',
      data: params,
      transformRequest: objectToQueryString,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).success(function(data, status) {
      return $location.path($scope.user.userName + '/' + data.formatted_title);
    }).error(function(data, status) {
      return $scope.titleTaken = true;
    });
  };
});

controllers.controller("ProjectListCtrl", function($scope, $http, $location, $rootScope, AllProjectsService) {
  console.log("[CONTROLLER] Project List");
  $scope.newProjectData = {};
  $scope.newProject = false;
  $scope.user = {
    userName: 'demo-user',
    displayName: 'Demo User'
  };
  AllProjectsService.promise($scope.user.userName, function(projects) {
    return $scope.projects = projects;
  });
  $scope.select_project = function(pID) {
    return $rootScope.pID = pID;
  };
  return $scope.new_project_toggle = function() {
    return $scope.newProject = !$scope.newProject;
  };
});

controllers.controller("OverviewCtrl", function($scope, $rootScope) {
  return console.log("[CONTROLLER] Overview");
});

controllers.controller("PaneToggleCtrl", function($scope) {
  $scope.leftClosed = false;
  $scope.rightClosed = false;
  $scope.toggleLeft = function() {
    return $scope.leftClosed = !$scope.leftClosed;
  };
  return $scope.toggleRight = function() {
    return $scope.rightClosed = !$scope.rightClosed;
  };
});

controllers.controller("TabsCtrl", function($scope, $state, $rootScope, $stateParams) {
  return $scope.tabs = [
    {
      route: "engine.data",
      label: "1. Manage Datasets"
    }, {
      route: "engine.ontology",
      label: "2. Edit Ontology"
    }, {
      route: "engine.visualize",
      label: "3. Select Visualizations"
    }, {
      route: "engine.assemble",
      label: "4. Assemble Engine"
    }
  ];
});

controllers.controller("DatasetListCtrl", function($scope, $rootScope, projectID, $http, $upload, $timeout, $stateParams, DataService) {
  $scope.selectedIndex = 0;
  $scope.currentPane = 'left';
  $scope.options = [
    {
      label: 'Upload File',
      inactive: false
    }, {
      label: 'Connect to Database',
      inactive: true
    }, {
      label: 'Connect to API',
      inactive: true
    }, {
      label: 'Search DIVE Datasets',
      inactive: true
    }
  ];
  $scope.select_option = function(index) {
    $scope.currentPane = 'left';
    if (!$scope.options[index].inactive) {
      return $scope.selectedIndex = index;
    }
  };
  $scope.select_dataset = function(index) {
    $scope.currentPane = 'right';
    return $scope.selectedIndex = index;
  };
  $scope.types = ["int", "float", "str"];
  DataService.promise(function(datasets) {
    return $scope.datasets = datasets;
  });
  $scope.onFileSelect = function($files) {
    var file, i, _results;
    i = 0;
    _results = [];
    while (i < $files.length) {
      file = $files[i];
      $scope.upload = $upload.upload({
        url: "http://localhost:8888/api/upload",
        data: {
          pID: $rootScope.pID
        },
        file: file
      }).progress(function(evt) {
        console.log("Percent loaded: " + parseInt(100.0 * evt.loaded / evt.total));
      }).success(function(data, status, headers, config) {
        return $scope.datasets.push(data);
      });
      _results.push(i++);
    }
    return _results;
  };
  return $scope.removeDataset = function(dID) {
    console.log('Removing dataset, dID:', dID);
    return $http["delete"]('http://localhost:8888/api/data', {
      params: {
        pID: $rootScope.pID,
        dID: dID
      }
    }).success(function(result) {
      var dataset, deleted_dIDs, newDatasets, _i, _len, _ref, _ref1;
      deleted_dIDs = result;
      newDatasets = [];
      _ref = $scope.datasets;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        dataset = _ref[_i];
        if (_ref1 = dataset.dID, __indexOf.call(deleted_dIDs, _ref1) < 0) {
          newDatasets.push(dataset);
        }
      }
      return $scope.datasets = newDatasets;
    });
  };
});

controllers.controller("OntologyEditorCtrl", function($scope, $http, DataService, PropertyService) {
  $scope.selectedLeftIndex = 0;
  $scope.selectedRightIndex = 0;
  $scope.currentPane = 'left';
  $scope.layoutOptions = [
    {
      label: 'Object',
      inactive: false
    }, {
      label: 'List',
      inactive: true
    }, {
      label: 'Hierarchy',
      inactive: true
    }
  ];
  $scope.editOptions = [
    {
      label: 'Add',
      inactive: true
    }, {
      label: 'Edit',
      inactive: true
    }, {
      label: 'Delete',
      inactive: true
    }
  ];
  $scope.select_left_option = function(index) {
    return $scope.selectedLeftIndex = index;
  };
  $scope.select_right_option = function(index) {
    return $scope.selectedRightIndex = index;
  };
  DataService.promise(function(datasets) {
    $scope.datasets = datasets;
    return console.log('Datasets dIDs:', _.pluck($scope.datasets, 'dID'));
  });
  $scope.loading = true;
  return PropertyService.promise(function(properties) {
    $scope.loading = false;
    $scope.properties = properties;
    $scope.overlaps = properties.overlaps;
    return $scope.hierarchies = properties.hierarchies;
  });
});

controllers.controller("AssembleCtrl", function($scope, $http) {});

controllers.controller("CreateVizCtrl", function($scope, $http, DataService, PropertyService, VizDataService, SpecificationService) {
  var type_name_from_index;
  DataService.promise(function(datasets) {
    console.log('Datasets dIDs:', _.pluck($scope.datasets, 'dID'));
    return $scope.datasets = datasets;
  });
  PropertyService.promise(function(properties) {
    $scope.properties = properties;
    $scope.overlaps = properties.overlaps;
    return $scope.hierarchies = properties.hierarchies;
  });
  $scope.selected_type = 0;
  $scope.selected_spec = 0;
  SpecificationService.promise(function(specs) {
    var k, v;
    $scope.types = (function() {
      var _results;
      _results = [];
      for (k in specs) {
        v = specs[k];
        _results.push({
          'name': k,
          'length': v.length
        });
      }
      return _results;
    })();
    $scope.allSpecs = specs;
    return $scope.specs = $scope.allSpecs[$scope.types[$scope.selected_type].name];
  });
  type_name_from_index = function(index) {
    return $scope.types[index].name;
  };
  $scope.select_type = function(index) {
    $scope.selected_type = index;
    return $scope.specs = $scope.allSpecs[$scope.types[$scope.selected_type].name];
  };
  return $scope.select_spec = function(index) {
    var spec, type;
    $scope.selected_spec = index;
    spec = $scope.specs[index];
    type = $scope.types[$scope.selected_type].name;
    console.log("Selected vizspec", spec);
    return VizDataService.promise(type, spec, function(result) {
      return $scope.vizData = result;
    });
  };
});
