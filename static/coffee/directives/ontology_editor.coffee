engineApp.directive "ontologyEditor", [
  "$window"
  "$timeout"
  "d3Service"
  ($window, $timeout, d3Service) ->
    return (
      restrict: "EA"
      scope:
        data: "="
        overlaps: "="
        hierarchies: "="
        label: "@"
        onClick: "&"
      link: (scope, ele, attrs) ->
        d3Service.d3().then (d3) ->

          margin = parseInt(attrs.margin) or 20
          barHeight = parseInt(attrs.barHeight) or 20
          barPadding = parseInt(attrs.barPadding) or 5
          svg = d3.select(ele[0]).append("svg").style("width", "100%").style("height", "100%")
          $window.onresize = ->
            scope.$apply()
            return

          scope.$watch (->
            angular.element($window)
          ), ->
            scope.render scope.data, scope.overlaps, scope.hierarchies

          scope.$watchCollection "[data,overlaps,hierarchies]", ((newData) ->
            scope.render newData[0], newData[1], newData[2]
          ), true
          scope.render = (data, overlaps, hierarchies) ->
            svg.selectAll("*").remove()
            unless (data and overlaps and hierarchies)
              return
            if renderTimeout
              clearTimeout(renderTimeout)
            
            # Margins and Positioning
            boxWidth = 200
            margins = 
              left: 20
            boxMargins =
              x: 20
              y: 20
            attributesYOffset = 60

            renderTimeout = $timeout( ->
              # Arrowhead marker definition
              svg.append("defs").append("marker").attr("id", "arrowhead").attr("refX", 3).attr("refY", 2).attr("markerWidth", 6).attr("markerHeight", 4).attr("orient", "auto").append("path").attr("d", "M 0,0 V 4 L3,3 Z")
              
              # Attribute overlap color scale
              colorScale = d3.scale.category10()
              colorScale.domain(Object.keys(overlaps))
              g = svg.selectAll("g")
                .data(data, (d) -> d.column_attrs)
              .enter()
                .append("g")
                .attr("class", "box")
                .attr("transform", "translate(" + boxMargins.x + "," + boxMargins.y + ")")
              
              # Box
              rect = g.append("rect")
                .attr("height", 500)
                .attr("width", boxWidth)
                .attr("x", (d, i) -> i * (boxWidth + margins.left))
                .attr("rx", 3)
                .attr("ry", 3)
                .attr("stroke", "#AEAEAE")
                .attr("stroke-width", 1)
                .attr("fill", (d) -> "#FFFFFF")
              
              # Header
              text = g.append("text")
                .attr("fill", "#000000")
                .attr("x", (d, i) -> i * (boxWidth + margins.left) + 10)
                .attr("y", 20)
                .attr("font-size", 14)
                .attr("font-weight", "light")
                .text((d) -> d.filename)  # TODO make this a title responsive to user input
              
              # Attributes
              tspan = g.append("g").attr("transform", (d, i) ->
                x = i * (boxWidth + margins.left) + 10
                y = attributesYOffset
                "translate(" + x + "," + y + ")"
              ).attr("class", "attributes").each((d) ->
                unique_cols = d.unique_cols
                texts = d3.select(this)
                  .selectAll("g text")
                  .data(d.column_attrs)
                .enter()
                  .append("g")
                  .attr("class", "attr")
                  .append("text").attr("y", (d, i) -> i * 20)
                  .attr("fill", "#000000")
                  .attr("font-size", 14)
                  .attr("font-weight", "light").text((d, i) ->
                    # Add asterisk if column is unique
                    # unique = (if unique_cols[i] then "*" else "")
                    # d.name + unique + " (" + d.type + ")"
                    d.name
                  )
              )
              
              # TODO DO THIS PROPERLY
              
              #///////
              # Visualize relationships
              #///////
              attributePositions = {}
              
              # Get left and right positions for each node (relative to parent)
              d3.selectAll("g.attr").each (d, i) ->
                attrName = d.name
                column_id = d.column_id
                bbox = d3.select(this).node().getBBox()
                h = bbox.height
                w = bbox.width
                y = bbox.y
                
                # Top-level parent boxes
                parentBBox = d3.select(@parentNode.parentNode).node().getBBox()
                parentLeft = parentBBox.x
                parentTop = parentBBox.y
                
                # Final Positions
                finalLeftX = parentLeft + margins.left + 5
                finalLeftY = parentTop + y + boxMargins.y + attributesYOffset + (h / 2)
                finalRightX = parentLeft + margins.left + w
                finalRightY = parentTop + y + boxMargins.y + attributesYOffset + (h / 2)
                
                dataset_id = d3.select(@parentNode).datum().dataset_id
                attributePositions[dataset_id] = {}  unless dataset_id of attributePositions
                attributePositions[dataset_id][column_id] =
                  l: [
                    finalLeftX
                    finalLeftY
                  ]
                  r: [
                    finalRightX
                    finalRightY
                  ]

                return

              links = []
              OVERLAP_THRESHOLD = 0.5
              
              # Flatten overlaps into array
              for datasetPair of overlaps
                datasets = datasetPair.split("\t")
                columnPairs = overlaps[datasetPair]
                for columnPair of columnPairs
                  columns = columnPair.split("\t")
                  overlap = columnPairs[columnPair]
                  if overlap > OVERLAP_THRESHOLD
                    links.push [
                      [
                        parseInt(datasets[0])
                        parseInt(columns[0])
                      ]
                      [
                        parseInt(datasets[1])
                        parseInt(columns[1])
                      ]
                    ]
              
              # TODO Generate this dynamically

              # Link overlapping attributes
              i = 0

              # while i < links.length
              #   link = links[i]
              #   l = link[0]
              #   r = link[1]
              #   console.log(l, r)

              #   # Necessary to not overlap edges with boxes
              #   tableL = l[0]
              #   tableR = r[0]
              #   attrPositionsA = attributePositions[l[0]][l[1]]
              #   attrPositionsB = attributePositions[r[0]][r[1]]
              #   if attrPositionsA and attrPositionsB
              #     attrAL = attrPositionsA.l
              #     attrAR = attrPositionsA.r
              #     attrBL = attrPositionsB.l
              #     attrBR = attrPositionsB.r
              #     finalAPos = attrAR
              #     finalBPos = attrBL
              #     # TODO Create a wrapper for this
              #     svg.append("path").attr("marker-end", "url(#arrowhead)").attr("d", "M" + finalAPos[0] + "," + finalAPos[1] + "L" + finalBPos[0] + "," + finalBPos[1]).attr("stroke", "black").attr "stroke-width", 1
              #   i++
            , 200)
    )
]