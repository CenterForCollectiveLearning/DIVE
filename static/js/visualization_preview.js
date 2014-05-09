app.directive('visualizationPreview', ['$window', '$timeout', 'd3Service', 
    function($window, $timeout, d3Service) {
    	return {
        restrict: 'EA',
        scope: {
            vizType: '=',
            vizSpec: '=',
            vizData: '=',
            label: '@',
            onClick: '&'
        },
        link: function(scope, ele, attrs) {
            d3Service.d3().then(function(d3) {

            console.log("Link scope:", scope);

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
                scope.render(scope.vizType, scope.vizSpec, scope.vizData);
            });
   
            scope.$watchCollection('[selected_vizType, vizSpec, vizData]', function(newData) {
                console.log("NEW DATA", newData)
                scope.render(newData[0], newData[1], newData[2]);
            }, true);
   
            scope.render = function(vizType, vizSpec, vizData) {
                console.log("vizType", vizType);
                console.log("vizSpec", vizSpec);
                console.log("vizData", vizData);
                svg.selectAll('*').remove();
     
                if (!vizData) return;
                if (renderTimeout) clearTimeout(renderTimeout);

                renderTimeout = $timeout(function() {
                   var viz = d3plus.viz()
                    .container('div#visualization-preview')
                    .data(vizData)
                    .type('tree_map')
                    .id(vizSpec.by)
                    .size('count')
                    .draw()
                }, 200);
            };
        })
	}}
}])