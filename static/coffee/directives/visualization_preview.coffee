engineApp.directive "visualizationPreview", [
  "$window"
  "$timeout"
  "d3Service"
  ($window, $timeout, d3Service) ->
    return (
      restrict: "EA"
      scope:
        vizType: "="
        vizSpec: "="
        vizData: "="
        label: "@"
        onClick: "&"

      link: (scope, ele, attrs) ->
        d3Service.d3().then (d3) ->
          renderTimeout = undefined
          $window.onresize = ->
            scope.$apply()
            return

          scope.$watch (->
            angular.element($window)[0].innerWidth
          ), ->
            scope.render scope.vizType, scope.vizSpec, scope.vizData
            return

          scope.$watchCollection "[vizType,vizSpec,vizData]", ((newData) ->
            scope.render newData[0], newData[1], newData[2]
            return
          ), true
          scope.render = (vizType, vizSpec, vizData) ->
            return  unless vizData
            clearTimeout renderTimeout  if renderTimeout
            renderTimeout = $timeout(->
              
              # TODO Reduce Redundancy in d3Plus
              groupBy = vizSpec.groupBy.toString()
              selectData = [
                {
                  value: "ar"
                  text: "Arabic"
                }
                {
                  value: "zh"
                  text: "Chinese"
                }
                {
                  value: "en"
                  text: "English"
                  selected: true
                }
                {
                  value: "de"
                  text: "German"
                }
                {
                  value: "pt"
                  text: "Portuguese"
                }
                {
                  value: "es"
                  text: "Spanish"
                }
              ]
              if vizType is "treemap"
                viz = d3plus.viz().container("div#viz-container").data(vizData).type("tree_map").font(family: "Karbon").id(groupBy).size("count").draw()
                
                # https://github.com/alexandersimoes/d3plus/wiki/Forms
                dropdown = d3plus.form().container("div#viz-container").data(selectData).title("Select Options").draw()
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