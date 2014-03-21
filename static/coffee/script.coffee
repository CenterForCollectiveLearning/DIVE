# Debug Helper
window.SC = (selector) -> angular.element(selector).scope()

app = angular.module('app', [])

# Use '{({' instead of '{{' to avoid collisions with Jinja
app.config(($interpolateProvider) -> $interpolateProvider.startSymbol('{[{').endSymbol('}]}'))

app.controller('DatasetListCtrl', ($scope) ->
    $scope.datasets = [
        title: "Dataset 1"
        rows: 100
        cols: 1000
        type: "CSV"
    , 
        title: "Dataset 2"
        rows: 150
        cols: 1500
        type: "TSV"    
    ]
    # $scope.datasets = [
    #     title: "Dataset 1"
    #     rows: 100
    #     cols: 1000
    #     type: "CSV"
    # ,
    #     title: "Dataset 2"
    #     rows: 150
    #     cols: 1500
    #     type: "TSV"    
    # ]
    console.log $scope
)