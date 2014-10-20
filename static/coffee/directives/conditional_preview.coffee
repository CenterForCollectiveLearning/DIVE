engineApp.directive "conditionalPreview", ["$window", "$timeout", "d3Service",
  ($window, $timeout, d3Service) ->
    return (
      restrict: "EA"
      scope:
        datasets: "="
        label: "@"
        onClick: "&"
      templateUrl: 'dist/views/conditional_editor.html'

      link: (scope, ele, attrs) ->
        console.log("datasets in conditional", scope.datasets)
        scope.adding = false
        scope.conditionalData = [
          'one'
          'two'
        ]
        scope.selectedConditionals = {
          
        }
        scope.add_dropdown = ->
          scope.adding = true
          console.log("adding dropdown")

        d3plus.form()
    )
]