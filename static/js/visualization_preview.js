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

            var renderTimeout;
            $window.onresize = function() {
                scope.$apply();
            };
   
            scope.$watch(function() {
                return angular.element($window)[0].innerWidth;
            }, function() {
                scope.render(scope.vizType, scope.vizSpec, scope.vizData);
            });
   
            scope.$watchCollection('[vizType,vizSpec,vizData]', function(newData) {
                scope.render(newData[0], newData[1], newData[2]);
            }, true);
   
            scope.render = function(vizType, vizSpec, vizData) {
                if (!vizData) return;
                if (renderTimeout) clearTimeout(renderTimeout);

                renderTimeout = $timeout(function() {
                    // TODO Reduce Redundancy in d3Plus calls
                    if (vizType == 'treemap') {
                        var viz = d3plus.viz()
                            .container('div#viz-container')
                            .data(vizData)
                            .type('tree_map')
                            .style({
                                font: { 
                                    family: 'Karbon'
                                }
                            })
                            .id(vizSpec.groupBy)
                            .size('count')
                            .draw()
                    }

                    else if (vizType == 'geomap') {
                        var viz = d3plus.viz()
                            .container('div#viz-container')
                            .type('geo_map')
                            .data(vizData)
                            .coords('/static/js/countries.json')
                            .id(vizSpec.groupBy)
                            .color('count')
                            .text('name')
                            .style({
                                font: { 
                                    family: 'Karbon'
                                },
                                color: {
                                    "heatmap": ["grey","purple"]
                                }
                            })
                            .draw()
                    }
                   
                }, 200);
            };
        })
	}}
}])