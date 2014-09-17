angular.module("d3Plus", []).factory("d3PlusService", [
  "$document", "$window", "$q", "$rootScope", function($document, $window, $q, $rootScope) {
    var d, d3service, onScriptLoad, s, scriptTag;
    onScriptLoad = function() {
      $rootScope.$apply(function() {
        d.resolve($window.d3Plus);
      });
    };
    d = $q.defer();
    d3service = {
      d3Plus: function() {
        return d.promise;
      }
    };
    scriptTag = $document[0].createElement("script");
    scriptTag.type = "text/javascript";
    scriptTag.async = true;
    scriptTag.src = "https://raw.githubusercontent.com/alexandersimoes/d3plus/master/d3plus.js";
    scriptTag.onreadystatechange = function() {
      if (this.readyState === "complete") {
        onScriptLoad();
      }
    };
    scriptTag.onload = onScriptLoad;
    s = $document[0].getElementsByTagName("body")[0];
    s.appendChild(scriptTag);
    return d3service;
  }
]);
