engineApp.directive("ontologyEditor", [
  "$window", "$timeout", "d3Service", function($window, $timeout, d3Service) {
    return {
      restrict: "EA",
      scope: {
        data: "=",
        overlaps: "=",
        hierarchies: "=",
        uniques: "=",
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
            return scope.render(scope.data, scope.overlaps, scope.hierarchies, scope.uniques);
          });
          scope.$watchCollection("[data,overlaps,hierarchies,uniques]", (function(newData) {
            return scope.render(newData[0], newData[1], newData[2], newData[3]);
          }), true);
          return scope.render = function(data, overlaps, hierarchies, uniques) {
            var attributesYOffset, boxMargins, boxWidth, margins, renderTimeout;
            svg.selectAll("*").remove();
            if (!(data && overlaps && hierarchies && uniques)) {
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
            attributesYOffset = 80;
            return renderTimeout = $timeout(function() {
              var OVERLAP_THRESHOLD, attrAL, attrAR, attrBL, attrBR, attrPositionsA, attrPositionsB, attributePositions, colorScale, columnPair, columnPairs, columns, datasetPair, datasets, extractTransform, finalAPos, finalBPos, g, hoverArrow, i, l, l_col, l_dID, link, links, overlap, r, r_col, r_dID, rect, text, tspan, visibleArrow, _i, _len, _results;
              svg.append("defs").append("marker").attr("id", "arrowhead").attr("refX", 3).attr("refY", 2).attr("markerWidth", 6).attr("markerHeight", 4).attr("orient", "auto").append("path").attr("d", "M 0,0 V 4 L3,3 Z");
              colorScale = d3.scale.category10();
              colorScale.domain(Object.keys(overlaps));
              g = svg.selectAll("g").data(data).enter().append("g").attr("class", "box").attr("transform", "translate(" + boxMargins.x + "," + boxMargins.y + ")");
              rect = g.append("rect").attr("height", 500).attr("width", boxWidth).attr("x", function(d, i) {
                return i * (boxWidth + margins.left);
              }).attr("rx", 3).attr("ry", 3).attr("stroke", "#AEAEAE").attr("stroke-width", 1).attr("fill", function(d) {
                return "#FFFFFF";
              });
              text = g.append("text").attr("fill", "#000000").attr("x", function(d, i) {
                return (i * (boxWidth + margins.left)) + (boxWidth / 2);
              }).attr("y", 30).attr("text-anchor", "middle").attr("class", "title").text(function(d) {
                return d.title;
              });
              tspan = g.append("g").attr("transform", function(d, i) {
                var x, y;
                x = i * (boxWidth + margins.left);
                y = attributesYOffset;
                return "translate(" + x + "," + y + ")";
              }).attr("class", "attributes").each(function(d) {
                var dID, texts, unique_cols;
                dID = d.dID;
                unique_cols = uniques[dID];
                texts = d3.select(this).selectAll("g text").data(d.column_attrs).enter().append("g").attr("class", "attr").attr("transform", function(d, i) {
                  return "translate(0," + (i * 35) + ")";
                }).on("mousemove", function(p) {
                  return d3.select(this).selectAll('rect').classed("hover", true);
                }).on("mouseout", function(p) {
                  return d3.select(this).selectAll('rect').classed("hover", false);
                }).on("click", function(p) {
                  dID = d3.select(this.parentNode).datum().dID;
                  return d3.select(this).append("g").text("test").classed("expanded", true);
                });
                texts.append("rect").attr("height", 35).attr("width", boxWidth).attr("fill-opacity", 0.0).attr("stroke", "#AEAEAE");
                return texts.append("text").attr("x", 10).attr("y", 22).attr("fill", "#000000").attr("font-size", 14).attr("font-weight", "light").text(function(d, i) {
                  var unique;
                  unique = (unique_cols[i] ? "*" : "");
                  return d.name + unique + " (" + d.type + ")";
                });
              });
              attributePositions = {};
              extractTransform = function(str) {
                var split, x, y;
                split = str.split(',');
                x = split[0].split('(')[1];
                y = split[1].split(')')[0];
                return [parseInt(x), parseInt(y)];
              };
              d3.selectAll("g.attr").each(function(d, i) {
                var attrName, bbox, column_id, dID, finalLeftX, finalLeftY, finalRightX, finalRightY, h, parentBBox, parentLeft, parentTop, w, x, y, _ref;
                attrName = d.name;
                column_id = d.column_id;
                _ref = extractTransform(d3.select(this).attr("transform")), x = _ref[0], y = _ref[1];
                bbox = d3.select(this).node().getBBox();
                h = bbox.height;
                w = bbox.width;
                parentBBox = d3.select(this.parentNode.parentNode).node().getBBox();
                parentLeft = parentBBox.x;
                parentTop = parentBBox.y;
                finalLeftX = parentLeft + margins.left + 5;
                finalLeftY = parentTop + y + boxMargins.y + attributesYOffset + (h / 2);
                finalRightX = parentLeft + margins.left + w - 5;
                finalRightY = parentTop + y + boxMargins.y + attributesYOffset + (h / 2);
                dID = d3.select(this.parentNode).datum().dID;
                if (!(dID in attributePositions)) {
                  attributePositions[dID] = {};
                }
                attributePositions[dID][column_id] = {
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
                    links.push([[datasets[0], columns[0]], [datasets[1], columns[1]]]);
                  }
                }
              }
              _results = [];
              for (i = _i = 0, _len = links.length; _i < _len; i = ++_i) {
                link = links[i];
                l = link[0];
                r = link[1];
                l_dID = l[0], l_col = l[1];
                r_dID = r[0], r_col = r[1];
                attrPositionsA = attributePositions[l_dID][l_col];
                attrPositionsB = attributePositions[r_dID][r_col];
                if (attrPositionsA && attrPositionsB) {
                  attrAL = attrPositionsA.l;
                  attrAR = attrPositionsA.r;
                  attrBL = attrPositionsB.l;
                  attrBR = attrPositionsB.r;
                  finalAPos = attrAR;
                  finalBPos = attrBL;
                  g = svg.append("g").attr("class", "arrow-container");
                  visibleArrow = g.append("path").attr("marker-end", "url(#arrowhead)").attr("d", "M" + finalAPos[0] + "," + finalAPos[1] + "L" + finalBPos[0] + "," + finalBPos[1]).attr("stroke", "black").attr("stroke-width", 1).attr("class", "visible-arrow");
                  _results.push(hoverArrow = g.append("path").attr("marker-end", "url(#arrowhead)").attr("d", "M" + finalAPos[0] + "," + finalAPos[1] + "L" + finalBPos[0] + "," + finalBPos[1]).attr('shape-rendering', 'crispEdges').style('opacity', 0.0).attr("stroke-width", 7).attr("stroke", "white").on("mousemove", function(p) {
                    return d3.select(this.parentNode).select("path.visible-arrow").attr("stroke-width", 2);
                  }).on("mouseout", function(p) {
                    return d3.select(this.parentNode).select("path.visible-arrow").attr("stroke-width", 1);
                  }));
                } else {
                  _results.push(void 0);
                }
              }
              return _results;
            }, 200);
          };
        });
      }
    };
  }
]);
