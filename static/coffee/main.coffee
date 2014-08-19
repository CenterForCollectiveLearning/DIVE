# Utility Functions
window.user = 

window.SC = (selector) ->
  angular.element(selector).scope()

window.objectToQueryString = (obj) ->
	str = []
	for p of obj
		str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]))
	str.join("&")

# What's the purpose of two separate applications?
# diveApp is top-level encompassing the engineApp
window.diveApp = angular.module("diveApp", ["ngRoute", "engineApp"])
window.engineApp = angular.module("engineApp", ["d3", "d3Plus", "ngRoute", "angularFileUpload", "engineControllers"])

engineApp.directive("engineTopBar", ->
	return {
		restrict: 'E',
		templateUrl: '/static/views/engine_top_bar.html'
	}
)

engineApp.directive("paneToggle", ->
	return {
		restrict: 'E',
		templateUrl: '/static/views/engine_pane_toggle.html'
		controller: "PaneToggleCtrl"
	}
)

# TODO Refactor top-level directives into another module
diveApp.directive("landingTop", ->
	return {
		restrict: 'E',
		templateUrl: '/static/views/landing_top.html'
		controller: 'ProjectListCtrl'
	}
)

diveApp.directive("landingProjects", ->
	return {
		restrict: 'E',
		scope: {}
		# TODO Bind to a call scoped by user
		controller: "ProjectListCtrl"
		templateUrl: '/static/views/landing_projects.html'
	}
)

engineApp.directive("topBar", ->
	return {
		restrict: "EA"
		scope: {},
		templateUrl: '/static/views/top_bar.html'
	}
)

diveApp.config ($interpolateProvider) ->
  $interpolateProvider.startSymbol("{[{").endSymbol "}]}"

# Need to return function
diveApp.filter "capitalize", -> 
  (input, scope) ->
    input = input.toLowerCase()
    input.substring(0, 1).toUpperCase() + input.substring(1)

# Resizing viewport for no overflow
angular.element(document).ready ->
  mainViewHeight = $(window).height() - $("header").height()                             
  $("div.wrapper").height mainViewHeight

window.onresize = (e) ->
  mainViewHeight = $(window).height() - $("header").height()
  $("div.wrapper").height mainViewHeight
