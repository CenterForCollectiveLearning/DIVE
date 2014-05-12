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
   
            scope.$watchCollection('[vizType,vizSpec,vizData]', function(newData) {
                console.log(newData);
                scope.render(newData[0], newData[1], newData[2]);
            }, true);
   
            scope.render = function(vizType, vizSpec, vizData) {
                console.log("vizType", vizType);
                console.log("vizSpec", vizSpec);
                console.log("vizData", vizData);
     
                if (!vizData) return;
                if (renderTimeout) clearTimeout(renderTimeout);

                console.log(vizSpec.by)

                renderTimeout = $timeout(function() {
                   var viz = d3plus.viz()
                    .container('div#viz-container')
                    .data(vizData)
                    .type('tree_map')
                    .id(vizSpec.groupBy)
                    .size('count')
                    .draw()
                }, 200);
            };
        })
	}}
}])