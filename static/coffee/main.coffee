# Utility Functions
window.SC = (selector) ->
  angular.element(selector).scope()

# diveApp is top-level encompassing the engineApp
window.diveApp = angular.module("diveApp", ["ngRoute", "engineApp"])
window.engineApp = angular.module("engineApp", ["d3", "d3Plus", "ngRoute", "engineControllers"])

diveApp.directive("landingTop", ->
	return {
		restrict: 'E',
		templateUrl: '/static/views/landing_top.html'
	}
)

diveApp.directive("landingProjects", ->
	return {
		restrict: 'E',
		scope: {}
		# TODO Bind to a call scoped by user
		controller: ($scope, $element, $attrs) ->
            $scope.projects = [
            	{ title: 'Pantheon' },
            	{ title: 'OEC' },
            	{ title: 'DataViva' },
            ]		
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
