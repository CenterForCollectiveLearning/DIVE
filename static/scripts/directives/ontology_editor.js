engineApp.directive("ontologyEditor", [
  "$window", "$timeout", "d3Service", function($window, $timeout, d3Service) {
    return {
      restrict: "EA",
      scope: {
        data: "=",
        overlaps: "=",
        hierarchies: "=",
        label: "@",
        onClick: "&"
      },
      link: function(scope, ele, attrs) {
        return d3Service.d3().then(function(d3) {
          var barHeight, barPadding, margin, svg;
          margin = parseInt(attrs.margin) || 20;
          barHeight = parseInt(attrs.barHeight) || 20;
          barPadding = parseInt(attrs.barPadding) || 5;
          svg = d3.select(ele[0]).append("svg").style("width", "100%").style("height", "100%");
          $window.onresize = function() {
            scope.$apply();
          };
          scope.$watch((function() {
            return angular.element($window)[0].innerWidth;
          }), function() {
            return scope.render(scope.data, scope.overlaps, scope.hierarchies);
          });
          scope.$watchCollection("[data,overlaps,hierarchies]", (function(newData) {
            return scope.render(newData[0], newData[1], newData[2]);
          }), true);
          return scope.render = function(data, overlaps, hierarchies) {
            var attributesYOffset, boxMargins, boxWidth, margins, renderTimeout;
            svg.selectAll("*").remove();
            if (!(data && overlaps && hierarchies)) {
              return;
            }
            if (renderTimeout) {
              clearTimeout(renderTimeout);
            }
            boxWidth = 200;
            margins = {
              left: 20
            };
            boxMargins = {
              x: 20,
              y: 20
            };
            attributesYOffset = 60;
            return renderTimeout = $timeout(function() {
              var OVERLAP_THRESHOLD, attributePositions, colorScale, columnPair, columnPairs, columns, datasetPair, datasets, g, i, links, overlap, rect, text, tspan;
              svg.append("defs").append("marker").attr("id", "arrowhead").attr("refX", 3).attr("refY", 2).attr("markerWidth", 6).attr("markerHeight", 4).attr("orient", "auto").append("path").attr("d", "M 0,0 V 4 L3,3 Z");
              colorScale = d3.scale.category10();
              colorScale.domain(Object.keys(overlaps));
              g = svg.selectAll("g").data(data, function(d) {
                return d.column_attrs;
              }).enter().append("g").attr("class", "box").attr("transform", "translate(" + boxMargins.x + "," + boxMargins.y + ")");
              rect = g.append("rect").attr("height", 500).attr("width", boxWidth).attr("x", function(d, i) {
                return i * (boxWidth + margins.left);
              }).attr("rx", 3).attr("ry", 3).attr("stroke", "#AEAEAE").attr("stroke-width", 1).attr("fill", function(d) {
                return "#FFFFFF";
              });
              text = g.append("text").attr("fill", "#000000").attr("x", function(d, i) {
                return i * (boxWidth + margins.left) + 10;
              }).attr("y", 20).attr("font-size", 14).attr("font-weight", "light").text(function(d) {
                return d.filename;
              });
              tspan = g.append("g").attr("transform", function(d, i) {
                var x, y;
                x = i * (boxWidth + margins.left) + 10;
                y = attributesYOffset;
                return "translate(" + x + "," + y + ")";
              }).attr("class", "attributes").each(function(d) {
                var texts, unique_cols;
                unique_cols = d.unique_cols;
                return texts = d3.select(this).selectAll("g text").data(d.column_attrs).enter().append("g").attr("class", "attr").append("text").attr("y", function(d, i) {
                  return i * 20;
                }).attr("fill", "#000000").attr("font-size", 14).attr("font-weight", "light").text(function(d, i) {
                  return d.name;
                });
              });
              attributePositions = {};
              d3.selectAll("g.attr").each(function(d, i) {
                var attrName, bbox, column_id, dataset_id, finalLeftX, finalLeftY, finalRightX, finalRightY, h, parentBBox, parentLeft, parentTop, w, y;
                attrName = d.name;
                column_id = d.column_id;
                bbox = d3.select(this).node().getBBox();
                h = bbox.height;
                w = bbox.width;
                y = bbox.y;
                parentBBox = d3.select(this.parentNode.parentNode).node().getBBox();
                parentLeft = parentBBox.x;
                parentTop = parentBBox.y;
                finalLeftX = parentLeft + margins.left + 5;
                finalLeftY = parentTop + y + boxMargins.y + attributesYOffset + (h / 2);
                finalRightX = parentLeft + margins.left + w;
                finalRightY = parentTop + y + boxMargins.y + attributesYOffset + (h / 2);
                dataset_id = d3.select(this.parentNode).datum().dataset_id;
                if (!(dataset_id in attributePositions)) {
                  attributePositions[dataset_id] = {};
                }
                attributePositions[dataset_id][column_id] = {
                  l: [finalLeftX, finalLeftY],
                  r: [finalRightX, finalRightY]
                };
              });
              links = [];
              OVERLAP_THRESHOLD = 0.5;
              for (datasetPair in overlaps) {
                datasets = datasetPair.split("\t");
                columnPairs = overlaps[datasetPair];
                for (columnPair in columnPairs) {
                  columns = columnPair.split("\t");
                  overlap = columnPairs[columnPair];
                  if (overlap > OVERLAP_THRESHOLD) {
                    links.push([[parseInt(datasets[0]), parseInt(columns[0])], [parseInt(datasets[1]), parseInt(columns[1])]]);
                  }
                }
              }
              return i = 0;
            }, 200);
          };
        });
      }
    };
  }
]);
