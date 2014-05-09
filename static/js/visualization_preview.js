app.directive('visualizationPreview', ['$window', '$timeout', 'd3Service', 
    function($window, $timeout, d3Service, d3PlusService) {
    	return {
        restrict: 'EA',
        scope: {
            vizData: '=',
            vizType: '=',
            label: '@',
            onClick: '&'
        },
        link: function(scope, ele, attrs) {
            var renderTimeout;
   
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
                console.log(scope);
                scope.render(scope.vizData, scope.vizType);
            });
   
            scope.$watchCollection('[vizData, vizType]', function(newData) {
                console.log("NEWDATA", newData);
                scope.render(newData[0], newData[1]);
            }, true);
   
            scope.render = function(vizData, vizType) {
                console.log("IN VIZPREVIEW");
                console.log(vizData, vizType);
                svg.selectAll('*').remove();
     
                if (!vizData) return;
                if (renderTimeout) clearTimeout(renderTimeout);

                console.log("***", vizData, vizType)
                renderTimeout = $timeout(function() {
                	// console.log(d3plus);
                }, 200);
            };
	}}
}])