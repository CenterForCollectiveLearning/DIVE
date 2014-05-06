app.directive('ontologyEditor', ['$window', '$timeout', 'd3Service', 
    function($window, $timeout, d3Service) {
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

                    // Arrowhead marker definition
                    svg.append("defs").append("marker")
                        .attr("id", "arrowhead")
                        .attr("refX", 3) /*must be smarter way to calculate shift*/
                        .attr("refY", 2)
                        .attr("markerWidth", 6)
                        .attr("markerHeight", 4)
                        .attr("orient", "auto")
                        .append("path")
                            .attr("d", "M 0,0 V 4 L3,3 Z");

                    // Attribute overlap color scale
                    var colorScale = d3.scale.category10();
                    colorScale.domain(Object.keys(overlaps));

                    g = svg.selectAll('g')
                            .data(data)
                          .enter()
                            .append("g")
                            .attr('class', 'box')
                            .attr("transform", "translate(" + boxMargins.x + "," + boxMargins.y + ")")

                    // Box
                    rect = g.append('rect')
                        .attr('height', 500)
                        .attr('width', boxWidth)
                        .attr('x', function(d, i) { return i * (boxWidth + margins.left)})
                        .attr('rx', 3)
                        .attr('ry', 3)
                        .attr('stroke', '#000000')
                        .attr('stroke-width', 2)
                        .attr('fill', function(d) { return '#FFFFFF' })

                    // Header
                    text = g.append('text')
                        .attr('fill', "#000000")
                        .attr('x', function(d, i) { return i * (boxWidth + margins.left) + 10 })
                        .attr('y', 20)
                        .attr('font-size', 16)
                        .attr('font-weight', 'bold')
                        .text(function(d) { return d.filename })

                    // Attributes
                    tspan = g.append('g')
                            .attr('transform', function(d, i) {
                                var x = i * (boxWidth + margins.left) + 10;
                                var y = attributesYOffset;
                                return 'translate(' + x + ',' + y + ')'
                            })
                            .attr('class', 'attributes')
                            .each(function(d) {
                                var unique_cols = d.unique_cols;
                                texts = d3.select(this)
                                    .selectAll('g text')   
                                    .data(d.colAttrs)
                                    .enter()
                                  .append('g')
                                    .attr('class', 'attr')
                                  .append('text')
                                    .attr('y', function(d, i) { return i * 20; })
                                    .attr('fill', '#000000')
                                    .attr('font-size', 14)
                                    .attr('font-weight', 'bold')
                                    .text(function(d, i) { 
                                        // Add asterisk if column is unique
                                        var unique = unique_cols[i] ? '*' : '';
                                        return d.name + unique + ' (' + d.type + ')'; 
                                    })
                            })

                    // TODO DO THIS PROPERLY

                    /////////
                    // Visualize relationships
                    /////////

                    var attributePositions = {}

                    // Get left and right positions for each node (relative to parent)
                    d3.selectAll('g.attr').each(function(d, i) {
                        var attrName = d.name
                        var bbox = d3.select(this).node().getBBox();
                        var h = bbox.height;
                        var w = bbox.width;
                        var y = bbox.y;

                        // Top-level parent boxes
                        var parentBBox = d3.select(this.parentNode.parentNode).node().getBBox();
                        var parentLeft = parentBBox.x;
                        var parentTop = parentBBox.y;

                        // Final Positions
                        var finalLeftX = parentLeft + margins.left + 10;
                        var finalLeftY = parentTop + y + boxMargins.y + attributesYOffset + (h/2);
                        var finalRightX = parentLeft + margins.left + w + 10;
                        var finalRightY = parentTop + y + boxMargins.y + attributesYOffset + (h/2);

                        // // Left Circles
                        // svg.append('circle')
                        //     .attr('cx', finalLeftX)
                        //     .attr('cy', finalLeftY)
                        //     .attr('r', 2)
                        //     .attr('fill', 'black')

                        // // Right Circles
                        // svg.append('circle')
                        //     .attr('cx', finalRightX)
                        //     .attr('cy', finalRightY)
                        //     .attr('r', 2)
                        //     .attr('fill', 'black')
                        
                        var parentTitle = d3.select(this.parentNode).datum().title;

                        if (!(parentTitle in attributePositions)) {
                            attributePositions[parentTitle] = {}
                        }

                        attributePositions[parentTitle][attrName] = {
                            l: [finalLeftX, finalLeftY],
                            r: [finalRightX, finalRightY]
                        }
                    })

                    var links = [];
                    var OVERLAP_THRESHOLD = 0.5;

                    // Flatten overlaps into array
                    for (var datasetPair in overlaps) {
                        var datasets = datasetPair.split('\t')
                        var columnPairs = overlaps[datasetPair];

                        for (var columnPair in columnPairs) {
                            var columns = columnPair.split('\t')
                            var overlap = columnPairs[columnPair];
                            if (overlap > OVERLAP_THRESHOLD) {
                                links.push([[datasets[0], columns[0]], [datasets[1], columns[1]]]);
                            }
                        }
                    }

                    // TODO Generate this dynamically
                    var boxOrderings = {
                        "countries.csv": 0,
                        "people.csv": 1,
                        "domains.csv": 2
                    }

                    // Link overlapping attributes
                    for (var i=0; i<links.length; i++) {
                        var link = links[i];
                        var l = link[0];
                        var r = link[1];

                        // Necessary to not overlap edges with boxes
                        var tableL = l[0];
                        var tableR = r[0];

                        var attrPositionsA = attributePositions[l[0]][l[1]];
                        var attrPositionsB = attributePositions[r[0]][r[1]];

                        if(attrPositionsA && attrPositionsB) {
                            var attrAL = attrPositionsA.l;
                            var attrAR = attrPositionsA.r;
                            var attrBL = attrPositionsB.l;
                            var attrBR = attrPositionsB.r;

                            var finalAPos = attrAR;
                            var finalBPos = attrBL;
                            if (boxOrderings[tableL] > boxOrderings[tableR]) {
                                var finalAPos = attrAL;
                                var finalBPos = attrBR;
                            }

                            svg.append('path')
                                .attr('marker-end', 'url(#arrowhead)')
                                .attr('d', 'M' + finalAPos[0] + ',' + finalAPos[1] + 'L' + finalBPos[0] + ',' + finalBPos[1])  // TODO Create a wrapper for this
                                .attr('stroke', 'black')
                                .attr('stroke-width', 1)

                        }
                    }

                }, 200);
            };
        });
	}}
}])