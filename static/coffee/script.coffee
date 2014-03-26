app = undefined
window.SC = (selector) ->
  angular.element(selector).scope()

app = angular.module("app", [])
app.config ($interpolateProvider) ->
  $interpolateProvider.startSymbol("{[{").endSymbol "}]}"

app.controller "DatasetListCtrl", ($scope, $http) ->
  window.onload = ->
    $("#data-file").on "change", (event) ->
      files = event.target.files
      return

    $("#data-submit").click (event) ->
      data = new FormData()
      data.append "dataset", files[0]
      $http(
        url: "/upload"
        method: "POST"
        data: data
        cache: false
        processData: false
        contentType: false
      ).success (data) ->
        alert data
        return

      return

    return

  $scope.datasets = [
    {
      title: "Dataset 1"
      rows: 100
      cols: 1000
      type: "CSV"
    }
    {
      title: "Dataset 2"
      rows: 150
      cols: 1500
      type: "TSV"
    }
  ]
  console.log $scope
