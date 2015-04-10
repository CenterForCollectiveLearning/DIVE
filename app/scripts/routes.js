var angular;

angular = require('angular');

require('angular-ui-router');

angular.module('diveApp.routes', ['ui.router']).config(function($stateProvider, $urlRouterProvider, $locationProvider) {
  var checkAuth;
  $urlRouterProvider.otherwise("/");
  checkAuth = function($rootScope, $state, $stateParams, UserService, ProjectService, formattedUserName, projectID) {
    var user;
    user = UserService.getCurrentUser();
    if ((user.userName === formattedUserName) && ($rootScope.pID === projectID.data)) {
      return ProjectService.promise($rootScope.pID, user.userName, function(project) {
        if (project.length) {

        }
      });
    } else {
      UserService.logoutUser();
      return $state.go('landing');
    }
  };

  $stateProvider
  .state('landing', {
    url: '/',
    templateUrl: 'modules/landing/landing.html'
  })
  .state('landing.create', {
    url: 'create',
    data: {
      'selectedIndex': 0
    },
    templateUrl: 'modules/landing/create.html'
  })
  .state('landing.projects', {
    url: 'projects',
    data: {
      'selectedIndex': 1
    },
    templateUrl: 'modules/landing/projects.html'
  })
  .state('landing.reports', {
    url: 'reports',
    data: {
      'selectedIndex': 2
    },
    templateUrl: 'modules/landing/reports.html'
  })
  .state('landing.about', {
    url: 'about',
    data: {
      'selectedIndex': 3
    },
    templateUrl: 'modules/landing/about.html'
  })
  .state('embed', {
    url: '/embed/:pID/:sID',
    templateUrl: 'modules/embed/embed.html',
    controller: 'EmbedCtrl',
    resolve: {
      vizDataService: function(VizDataService) {
        return VizDataService.promise;
      },
      exportedVizSpecService: function(ExportedVizSpecService) {
        return ExportedVizSpecService.promise;
      }
    }
  })
  .state('project', {
    url: '/:formattedUserName/:formattedProjectTitle',
    templateUrl: 'modules/project/project.html',
    onEnter: checkAuth,
    controller: function($scope, $rootScope, $state, $stateParams, $window, UserService, ProjectService, projectID) {
      $scope.projectTitle = $stateParams.formattedProjectTitle.split('-').join(' ');
      $scope.user = UserService.getCurrentUser();
      return $scope.logoutUser = function() {
        UserService.logoutUser();
        return $state.go('landing');
      };
    },
    resolve: {
      formattedUserName: function($stateParams) {
        return $stateParams.formattedUserName;
      },
      formattedProjectTitle: function($stateParams) {
        return $stateParams.formattedProjectTitle;
      },
      projectID: function($stateParams, UserService, ProjectIDService) {
        return ProjectIDService.promise($stateParams.formattedProjectTitle, UserService.getCurrentUser()['userName']);
      }
    }
  })
  .state('project.overview', {
    url: '/overview',
    templateUrl: 'modules/project/project_overview.html',
    controller: 'OverviewCtrl'
  })
  .state('project.data', {
    url: '/data',
    templateUrl: 'modules/data/data.html',
    controller: 'DataCtrl',
    resolve: {
      initialData: function(DataService) {
        return DataService.promise;
      }
    }
  })
  .state('project.ontology', {
    url: '/ontology',
    templateUrl: 'modules/property/property.html',
    controller: 'OntologyEditorCtrl',
    resolve: {
      initialData: function(DataService) {
        return DataService.promise;
      },
      propertyService: function(PropertyService) {
        return PropertyService.getProperties;
      }
    }
  })
  .state('project.visualize', {
    url: '/visualize',
    templateUrl: 'modules/visualization/visualization.html',
    controller: 'CreateVizCtrl',
    resolve: {
      specificationService: function(SpecificationService) {
        return SpecificationService.promise;
      },
      vizDataService: function(VizDataService) {
        return VizDataService.promise;
      },
      conditionalDataService: function(ConditionalDataService) {
        return ConditionalDataService.promise;
      }
    }
  })
  .state('project.assemble', {
    url: '/assemble',
    templateUrl: 'modules/export/export.html',
    controller: 'AssembleCtrl',
    resolve: {
      vizDataService: function(VizDataService) {
        return VizDataService.promise;
      },
      exportedVizSpecService: function(ExportedVizSpecService) {
        return ExportedVizSpecService.promise;
      }
    }
  });
});

// ---
// generated by coffee-script 1.9.0