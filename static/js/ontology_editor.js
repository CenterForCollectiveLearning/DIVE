// TODO Find out where to put this code

app.directive('ontologyEditor', function() {
	return {
		require: 'DatasetListCtrl',
		link: function(scope) {
			console.log($scope)
		}
	}
	// var margin = {
	// 	top: 0,
	// 	left: 0
	// }

	// var container = d3.select("div#ontology-editor");

	// console.log($scope.datasets);

	// var svg = container.append("svg")
	//                    .attr("width", 1000)
	//                    .attr("height", 500)
	//                  .append("g")
	//                    .attr("transform", "translate(" + margin.left + "," + margin.top+ ")")
})