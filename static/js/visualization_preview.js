app.directive('visualizationPreview', ['$window', '$timeout', 'd3Service', 
    function($window, $timeout, d3Service, d3PlusService) {
    	return {
        restrict: 'EA',
        scope: {
            data: '=',
            overlaps: '=',  // What does this do??
            hierarchies: '=',
            label: '@',
            onClick: '&'
        },
        link: function(scope, ele, attrs) {
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
                scope.render(scope.data, scope.overlaps, scope.hierarchies);
            });
   
            scope.$watchCollection('[data,overlaps,hierarchies]', function(newData) {
                scope.render(newData[0], newData[1], newData[2]);
            }, true);
   
            scope.render = function(data, overlaps, hierarchies) {

                svg.selectAll('*').remove();
     
                if (!data) return;
                if (renderTimeout) clearTimeout(renderTimeout);

                // Margins and Positioning
                var boxWidth = 220;
                var margins = {
                    left: 20
                }

                var boxMargins = {
                    x: 20,
                    y: 20
                }

                var attributesYOffset = 60;

                renderTimeout = $timeout(function() {
                	// console.log(d3plus);
                }, 200);
            };
	}}
}])