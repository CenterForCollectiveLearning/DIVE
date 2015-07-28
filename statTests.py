#screwing pandas for now

from scipy import stats
import numpy as np
import statsmodels.api as sm

from operator import add

def dfParse(oneArray):
    moment= {
            'mean':np.mean(oneArray),
            'median':np.median(oneArray),
            'mode':stats.mode(oneArray)[0][0],
            'variance':np.var(oneArray),
            'standardDeviation':np.std(oneArray),
            'geometricMean':stats.gmean(oneArray),
            'harmonicMean':stats.hmean(oneArray),
            'kurtosis':stats.kurtosis(oneArray),
            'skew':stats.skew(oneArray)
            }

    result_df = {
                'dataType':type(oneArray[0]),
                'moment':moment,
                'noramlP':stats.normaltest(oneArray),
                }
    return result_df

#return a boolean, if p-value less than threshold, returns false
def variationsEqual(THRESHOLD, *args):
    return stats.levene(*args)[1]>THRESHOLD

#if normalP is less than threshold, not considered normal
def setsNormal(THRESHOLD, *args):
    normal = True;
    for arg in args:
        if stats.normaltest(arg)[1] < THRESHOLD:
            normal = False;
    return normal

def chooseN(array, number):
    theSolutions = []
    if number == 1:
        for x in array:
            theSolutions.append(tuple([x]))
        return theSolutions
    for i in range(len(array)-number+1):
        frstNumber = [[array[i]]];
        restNumber = array[i+1:]
        restNumbersTuple = chooseN(restNumber,number-1)
        restNumbersList = []
        for tupleT in restNumbersTuple:
            restNumbersList.append(list(tupleT))
        iterationNumbers = (map(add, frstNumber*len(restNumbersList), restNumbersList))
        for x in iterationNumbers:
            theSolutions.append(tuple(x))
    return theSolutions

#the input x is an array of arrays, the input y is just a regular array
def reg_m(y, x):
    ones = np.ones(len(x[0]))
    X = sm.add_constant(np.column_stack((x[0], ones)))
    for ele in x[1:]:
        X = sm.add_constant(np.column_stack((ele, X)))
    results = sm.OLS(y, X).fit()
    return results

def runValidTests_Linregress(residuals, yList):
    predictedY = np.array(residuals)+np.array(yList)
    validTests={'chisquare':stats.chisquare(predictedY,yList), 'kstest':stats.ks_2samp(predictedY, yList)}
    print residuals
    if len(set(residuals))>1:
        validTests['wilcoxon']=stats.wilcoxon(residuals)
    if setsNormal(0.2, residuals, yList):
        validTests['ttest']=stats.ttest_1samp(residuals)
    return validTests

#xDict is a dictionary of the different independent variables considered
def multipleLinearRegression(xDict,yList):
    regressionDict = {}
    xKeys = xDict.keys()
    for chooseX in range(1,len(xKeys)+1):
        chooseXKeys = chooseN(xKeys,chooseX)
        for consideredKeys in chooseXKeys:
            consideredData = []
            for key in consideredKeys:
                consideredData.append(xDict[key])
            model = reg_m(yList,consideredData)
            regressionDict[consideredKeys]={}
            regressionDict[consideredKeys]['params']= np.append(model.params,model.rsquared)
            regressionDict[consideredKeys]['stats']= runValidTests_Linregress(model.resid, yList)
    return regressionDict

print multipleLinearRegression({'bob':range(1,20),'mary':range(1,20)},range(1,20))

def getValidTests_noregress(equalVar, independent, normal, numDataSets):
    if numDataSets == 1:
        validTests = {'chisquare':stats.chisquare,'power_divergence':stats.power_divergence,'kstest':stats.kstest}
        if normal:
            validTests['ttest_1samp']=stats.ttest_1samp
        return validTests

    elif numDataSets == 2:
        if independent:
            validTests = {'mannwhitneyu':stats.mannwhitneyu,'kruskal':stats.kruskal, 'ks_2samp':stats.ks_2samp}
            if normal:
                validTests['ttest_ind']=stats.ttest_ind
                if equalVar:
                    validTests['f_oneway']=stats.f_oneway
            return validTests
        else:
            validTests = {'ks_2samp':stats.ks_2samp, 'wilcoxon':stats.wilcoxon}
            if normal:
                validTests['ttest_rel']=stats.ttest_rel
            return validTests

    elif numDataSets >= 3:
        if independent:
            validTests = {'kruskal':stats.kruskal}
            if normal and equalVar:
                validTests['f_oneway']=stats.f_oneway
            return validTests
        else:
            validTests = {'friedmanchisquare':stats.friedmanchisquare}
            return validTests

def runValidTests_noregress(userInput, independent, *args):
    results={}
    normal = setsNormal(.25,*args)
    numDataSets = len(args)

    if numDataSets>1:
        equalVar = variationsEqual(.25,*args)
    else:
        equalVar = True


    validTests = getValidTests_noregress(equalVar, independent, normal, numDataSets)
    for test in validTests:
        if numDataSets==1:
            results[test]=validTests[test](args[0], userInput)
        else:
            results[test]=validTests[test](*args)
    return results

# a=range(1,30)
# a[0]=3
# print runValidTests_noregress(None, False, range(1,30),a)
