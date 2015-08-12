angular.module('diveApp.analysis').controller('ManualCtrl', ($scope, $rootScope, DataService, PropertiesService, StatisticsDataService, pIDRetrieved) ->

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
    ,
      title: 'Weighted Least Squares',
      value: 'wls',
    ,
      title: 'Generalized Least Squares',
      value: 'gls'
  ]

  @selectedDataset = null

  @selectedParams =
    dID: ''
    model: @MODELS[0].value
    arguments:
      estimator: @ESTIMATORS[0].value

  @onSelectDataset = (d) ->
    @setDataset(d)
    return

  @setDataset = (d) ->
    @selectedDataset = d
    @selectedParams.dID = d.dID

    @retrieveProperties()
    return

  @onSelectModel = () ->
    @refreshStatistics()

  @onSelectEstimator = () ->
    @refreshStatistics()

  @onSelectIndep = () ->
    if @indep
      @selectedParams.arguments.indep = [@indep.label]
    @refreshStatistics()

  @onSelectDep = () ->
    if @dep
      @selectedParams.arguments.dep = @dep.label
    @refreshStatistics()

  @refreshStatistics = () ->
    if @selectedParams['model']
      _params =
        spec: @selectedParams

      StatisticsDataService.getStatisticsData(_params).then((data) =>
        console.log("Got stats data", data)
        @statsData = data
        @formatTableDict()
      )

  @getAttributes = (type = {}) ->
    if @properties
      _attr = @properties.slice()

    return _attr

  @datasetsLoaded = false
  @propertiesLoaded = false

  @retrieveProperties = () ->
    PropertiesService.getProperties({ pID: $rootScope.pID, dID: @selectedDataset.dID }).then((properties) =>
      @propertiesLoaded = true
      @properties = properties
      console.log("Retrieved properties")
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

  @formattedData
  @formattedDataDict

  #separates statsData by the different keys (considers only std and regression coefficient)
  @separateStatDataByKeys = ()->
      indexi = Number.MAX_SAFE_INTEGER
      htmlDict = {}
      length = Object.keys(@statsData).length-1

      for key in @statsData['keys']
          htmlDict[key]={}
          htmlDict[key]['regCoeff']=[]
          htmlDict[key]['std']=[]

      for i in [0..length]
          key = Object.keys(@statsData)[i]
          for j in key.split('\'')
              if j=='keys'
                indexi=i

              else if !(j==', ') && !(j=='(') && !(j==')') && !(j==',)')  && !(j=='') && !(j=='(u')
                if i>indexi
                  htmlDict[j]['regCoeff'][i-1]=@statsData[key]['params']['x1']
                  htmlDict[j]['std'][i-1]=@statsData[key]['std']['x1']

                else
                  htmlDict[j]['regCoeff'][i]=@statsData[key]['params']['x1']
                  htmlDict[j]['std'][i]=@statsData[key]['std']['x1']

      @formattedData = htmlDict

#formats the separated data such that it could be implemented by the datatable
  @formatStatData = () ->
    data = []

    for key in @statsData['keys']
      block1 = [key]
      block2 = [key]
      for i in @formattedData[key]['std']
        if i == undefined
          block1.push("")

        else
          block1.push(i)

      for i in @formattedData[key]['regCoeff']
        if i == undefined
          block2.push("")

        else
          block2.push(i)

      data.push(block1)
      data.push(block2)

    return data


#creates a dicitionary of all of the information datatable requires to make a regression table
  @formatTableDict = () ->
    @separateStatDataByKeys()
    data = {}
    data['data']=@formatStatData()
    headers = ['VARIABLES']
    for i in [1..@formattedData[@statsData['keys'][0]]['regCoeff'].length]
      headers.push('('+String(i)+')')

    data['headers']=headers
    mergecells = []
    for i in [0..@statsData['keys'].length-1]
      mergecells.push({row: 2*i, col: 0, rowspan: 2, colspan:1})
      
    data['mergecells']=mergecells
    @formattedDataDict = data
    return true


  @
)
