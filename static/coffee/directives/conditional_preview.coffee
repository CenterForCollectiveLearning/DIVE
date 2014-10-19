engineApp.directive "conditionalPreview", ["$window", "$timeout", "d3Service",
  ($window, $timeout, d3Service) ->
    return (
      restrict: "EA"
      scope:
        label: "@"
        onClick: "&"
      template: conditonalEditor

      link: (scope, ele, attrs) ->

    )
]