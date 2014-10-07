engineApp.directive "visualizationPreview", ["$window", "$timeout", "d3Service",
  ($window, $timeout, d3Service) ->
    return (
      restrict: "EA"
      scope:
        vizType: "="
        vizSpec: "="
        vizData: "="
        conditionalData: "="
        label: "@"
        onClick: "&"

      link: (scope, ele, attrs) ->
        d3Service.d3().then (d3) ->
          renderTimeout = undefined
          $window.onresize = ->
            scope.$apply()
            return

          # Resizing
          scope.$watch ( ->
            angular.element($window)[0].innerWidth
          ), ->
            scope.render(scope.vizType, scope.vizSpec, scope.vizData, scope.conditionalData)
            return

          scope.$watchCollection("[vizType,vizSpec,vizData,conditionalData]", ((newData) ->
            console.log("newdata", newData)
            scope.render(newData[0], newData[1], newData[2], newData[3])
          ), true)

          scope.render = (vizType, vizSpec, vizData, conditionalData) ->
            unless (vizData and vizSpec and vizType and conditionalData)
              return

            clearTimeout renderTimeout if renderTimeout
            renderTimeout = $timeout(->

              condition = vizSpec.condition.title.toString()

              selectFn = (d) -> console.log(d)
              # dropdown = d3plus.form()
              #   .data(conditionalData)
              #   .title("Select Options")
              #   .id(condition)
              #   .text(condition)
              #   .type("drop")
              #   .draw()

              # TODO Reduce Redundancy in d3Plus
              aggregate = vizSpec.aggregate.title.toString()
              groupBy = vizSpec.groupBy.title.toString()

              if vizType is "treemap"
                console.log('drawing treemap')
                viz = d3plus.viz()
                  .container("div#viz-container")
                  .margin("20px")
                  .height(600)
                  .data(vizData)
                  .type("tree_map")
                  .font(family: "Karbon")
                  .title("Group all " + vizSpec.aggregate.title + " by " + groupBy + " given a " + condition)
                  .id(groupBy)
                  .size("count")
                  .draw()
                
              else if vizType is "geomap"
                viz = d3plus.viz().container("div#viz-container").type("geo_map").data(vizData).coords("/static/assets/countries.json").id(groupBy).color("count").text("name").font(family: "Karbon").style(color:
                  heatmap: [
                    "grey"
                    "purple"
                  ]
                ).draw()
              return
            , 200)
            return

          return

        return
    )
]