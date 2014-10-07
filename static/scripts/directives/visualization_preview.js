engineApp.directive("visualizationPreview", [
  "$window", "$timeout", "d3Service", function($window, $timeout, d3Service) {
    return {
      restrict: "EA",
      scope: {
        vizType: "=",
        vizSpec: "=",
        vizData: "=",
        conditionalData: "=",
        label: "@",
        onClick: "&"
      },
      link: function(scope, ele, attrs) {
        d3Service.d3().then(function(d3) {
          var renderTimeout;
          renderTimeout = void 0;
          $window.onresize = function() {
            scope.$apply();
          };
          scope.$watch((function() {
            return angular.element($window)[0].innerWidth;
          }), function() {
            scope.render(scope.vizType, scope.vizSpec, scope.vizData, scope.conditionalData);
          });
          scope.$watchCollection("[vizType,vizSpec,vizData,conditionalData]", (function(newData) {
            console.log("newdata", newData);
            return scope.render(newData[0], newData[1], newData[2], newData[3]);
          }), true);
          scope.render = function(vizType, vizSpec, vizData, conditionalData) {
            if (!(vizData && vizSpec && vizType && conditionalData)) {
              return;
            }
            if (renderTimeout) {
              clearTimeout(renderTimeout);
            }
            renderTimeout = $timeout(function() {
              var aggregate, condition, groupBy, selectFn, viz;
              condition = vizSpec.condition.title.toString();
              selectFn = function(d) {
                return console.log(d);
              };
              aggregate = vizSpec.aggregate.title.toString();
              groupBy = vizSpec.groupBy.title.toString();
              if (vizType === "treemap") {
                console.log('drawing treemap');
                viz = d3plus.viz().container("div#viz-container").margin("20px").height(600).data(vizData).type("tree_map").font({
                  family: "Karbon"
                }).title("Group all " + vizSpec.aggregate.title + " by " + groupBy + " given a " + condition).id(groupBy).size("count").draw();
              } else if (vizType === "geomap") {
                viz = d3plus.viz().container("div#viz-container").type("geo_map").data(vizData).coords("/static/assets/countries.json").id(groupBy).color("count").text("name").font({
                  family: "Karbon"
                }).style({
                  color: {
                    heatmap: ["grey", "purple"]
                  }
                }).draw();
              }
            }, 200);
          };
        });
      }
    };
  }
]);
