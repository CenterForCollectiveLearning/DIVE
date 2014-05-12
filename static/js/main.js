var app;

window.SC = function(selector) {
    return angular.element(selector).scope();
};

app = angular.module('engineApp', ['d3', 'd3Plus', 'ngRoute', 'engineControllers']);

app.config(function($interpolateProvider) {
    return $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
});

app.filter('capitalize', function() {
    return function(input, scope) {
        if (input != null) {
        	input = input.toLowerCase();
            return input.substring(0,1).toUpperCase()+input.substring(1);
        }
    }
});

// Resizing viewport for no overflow
angular.element(document).ready(function () {
	var mainViewHeight = $(window).height() - $('header').height()
    $('div.wrapper').height(mainViewHeight)
});