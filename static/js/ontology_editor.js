app.directive('ontologyEditor', ['$window', '$timeout', 'd3Service', 
    function($window, $timeout, d3Service) {
    	return {
        restrict: 'EA',
        scope: {
            data: '=',
            label: '@',
            onClick: '&'
        },
        link: function(scope, ele, attrs) {
            d3Service.d3().then(function(d3) {
   
            var renderTimeout;
            var margin = parseInt(attrs.margin) || 20,
                barHeight = parseInt(attrs.barHeight) || 20,
                barPadding = parseInt(attrs.barPadding) || 5;
   
            var svg = d3.select(ele[0])
              .append('svg')
                .style('width', '100%')
                .style('height', '100%');
   
            $window.onresize = function() {
                scope.$apply();
            };
   
            scope.$watch(function() {
                return angular.element($window)[0].innerWidth;
            }, function() {
                scope.render(scope.data);
            });
   
            scope.$watch('data', function(newData) {
                scope.render(newData);
            }, true);
   
            scope.render = function(data) {
            	console.log(data);
                svg.selectAll('*').remove();
     
                if (!data) return;
                if (renderTimeout) clearTimeout(renderTimeout);
     
                renderTimeout = $timeout(function() {

              }, 200);
            };
        });
	}}
}])