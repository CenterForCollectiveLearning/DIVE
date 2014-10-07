window.SC = function(selector) {
  return angular.element(selector).scope();
};

window.objectToQueryString = function(obj) {
  var p, str;
  str = [];
  for (p in obj) {
    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
  }
  return str.join("&");
};

window.formatRouteParam = function(str) {
  return str.trim().replace(/"/g, "");
};

window.diveApp = angular.module("diveApp", ["ui.router", "engineApp"]);

window.engineApp = angular.module("engineApp", ["d3", "d3Plus", "ui.router", "angularFileUpload", "engineControllers"]);

engineApp.directive("engineTopBar", function() {
  return {
    restrict: 'E',
    templateUrl: '/static/views/engine_top_bar.html'
  };
});

engineApp.directive("loader", function() {
  return {
    restrict: 'E',
    templateUrl: '/static/views/loader.html'
  };
});

engineApp.directive("paneToggle", function() {
  return {
    restrict: 'E',
    templateUrl: '/static/views/engine_pane_toggle.html',
    controller: "PaneToggleCtrl"
  };
});

diveApp.directive("landingTop", function() {
  return {
    restrict: 'E',
    templateUrl: '/static/views/landing_top.html',
    controller: 'ProjectListCtrl'
  };
});

diveApp.directive("landingProjects", function() {
  return {
    restrict: 'E',
    scope: {},
    controller: "ProjectListCtrl",
    templateUrl: '/static/views/landing_projects.html'
  };
});

engineApp.directive("topBar", function() {
  return {
    restrict: "EA",
    scope: {},
    templateUrl: '/static/views/top_bar.html'
  };
});

diveApp.filter("capitalize", function() {
  return function(input, scope) {
    input = input.toLowerCase();
    return input.substring(0, 1).toUpperCase() + input.substring(1);
  };
});

angular.element(document).ready(function() {
  var mainViewHeight;
  mainViewHeight = $(window).height() - $("header").height();
  return $("div.wrapper").height(mainViewHeight);
});

window.onresize = function(e) {
  var mainViewHeight;
  mainViewHeight = $(window).height() - $("header").height();
  return $("div.wrapper").height(mainViewHeight);
};
