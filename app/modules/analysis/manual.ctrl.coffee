angular.module('diveApp.analysis').controller('ManualCtrl', ($scope, $rootScope, DataService, PropertiesService, StatisticsDataService, pIDRetrieved) ->

  @COUNT_ATTRIBUTE =
    label: "count"
    type: "int"
    unique: true

  @ATTRIBUTE_TYPES =
    NUMERIC: ["int", "float"]

  # UI Parameters
  @MODELS = [
      title: 'Linear Regression'
      value: 'lr'
    ,
      title: 'Discrete Regression'
      value: 'dr'
  ]

  @ESTIMATORS = [
      title: 'Ordinary Least Squares'
      value: 'ols'
  ]

  @availableOperations = @OPERATIONS
  @availableAggregationFunctions = @AGGREGATION_FUNCTIONS
  @conditional1IsNumeric = true

  @selectedDataset = null

  @selectedParams =
    dID: ''
    model: @MODELS[0].value
    arguments: 
      estimator: @ESTIMATORS[0].value

  @attributeB = @COUNT_ATTRIBUTE

  @selectedConditional =
    'and': []
    'or': []

  @conditional1 =
    field: null
    operation: null
    criteria: null

  @isGrouping = false

  @onSelectDataset = (d) ->
    @setDataset(d)
    return

  @setDataset = (d) ->
    @selectedDataset = d
    @selectedParams.dID = d.dID

    @retrieveProperties()
    return

  @onSelectAggregationFunction = () ->
    @refreshVisualization()

  @onChangeConditional = () ->
    if @conditional1.criteria
      @selectedConditional.and = [@conditional1]
    else
      @selectedConditional.and = []
    @refreshVisualization()

  @refreshVisualization = () ->
    if @attributeA and @attributeB
      _params =
        spec: @selectedParams
        conditional: @selectedConditional

      VisualizationDataService.getVisualizationData(_params).then((data) =>
        @visualizationData = data.viz_data
        @tableData = data.table_result
      )

  @onSelectFieldA = () ->
    @selectedParams['field_a'] = @attributeA.label

    @refreshOperations()
    @refreshVisualization()
    return

  @onSelectFieldB = () ->
    @selectedParams.arguments['field_b'] = @attributeB.label
    @refreshVisualization()
    return

  @getConditional1Values = () ->
    return _.findWhere(@properties, {'label': @conditional1.field})['values']

  @refreshOperations = () ->
    if @attributeA and (@attributeA.type in @ATTRIBUTE_TYPES.NUMERIC or @attributeA.unique)
      @availableOperations = _.reject(@OPERATIONS, (operation) -> operation.value is "group")

      if @selectedParams.operation is "group"
        @selectedParams.operation = @availableOperations[0].value

      @attributeB = undefined

    @isGrouping = @selectedParams.operation is "group"
    return

  @getAttributes = (type = {}) ->
    if @properties
      _attr = @properties.slice()

      if type.primary
        _attr = _.reject(_attr, (property) => property.type in @ATTRIBUTE_TYPES.NUMERIC)

      if type.secondary
        _attr = _.reject(_attr, (property) => property.label is @selectedParams.field_a)

        if @isGrouping
          _attr = _.filter(_attr, (property) => property.type in @ATTRIBUTE_TYPES.NUMERIC)

        _attr.unshift(@COUNT_ATTRIBUTE)

    return _attr

  @datasetsLoaded = false
  @propertiesLoaded = false

  @retrieveProperties = () ->
    PropertiesService.getProperties({ pID: $rootScope.pID, dID: @selectedDataset.dID }).then((properties) =>
      @propertiesLoaded = true
      @properties = properties
    )
    return

  pIDRetrieved.promise.then((r) =>
    DataService.getDatasets().then((datasets) =>
      @datasetsLoaded = true
      @datasets = datasets
      @setDataset(datasets[0])
      console.log("Datasets loaded!", @datasets)
    )
  )

  @
)
