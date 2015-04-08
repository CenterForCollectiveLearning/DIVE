import numpy as np
import pandas as pd
import scipy
from scipy.stats import norm, mstats, skew, linregress, chisquare
from visualization_data import getVisualizationData, getRawData

def getVisualizationStats(viz_type, spec, conditional, pID):
    stats = {}

    raw_data = getRawData(spec, conditional, pID, viz_type)

    if viz_type == "treemap" :
        return getTreemapStats(pID, spec, raw_data)
    elif viz_type == "piechart" :
        return getPiechartStats(pID, spec, raw_data)
    elif viz_type == "geomap" :
        return getGeomapStats(pID, spec, raw_data)
    elif viz_type == "barchart" :
        return getScatterplotStats(pID, spec, raw_data)
    elif viz_type == "linechart" :
        return getScatterplotStats(pID, spec, raw_data)
    elif viz_type == "scatterplot" :
        return getScatterplotStats(pID, spec, raw_data)

def getPiechartStats(pID, spec, raw_data) :
    return getTreemapStats(pID, spec, raw_data)

def getGeomapStats(pID, spec, raw_data) :
    return getTreemapStats(pID, spec, raw_data)

def getTreemapStats(pID, spec, raw_data) :
    cond_df = raw_data.dropna()
    groupby = spec['groupBy']['title']

    stats = {}

    group_obj = cond_df.groupby(groupby)
    finalSeries = group_obj.size()

    print "TREEMAP STATS"
    # print finalSeries.values
    # print finalSeries.describe().to_dict()
    # print cond_df[groupby].describe().to_dict()

    chisq = chisquare(finalSeries.values)
    stats['chisq'] = {
        'chisq' : chisq[0],
        'p' : chisq[1]
    }

    stats['describe'] = dict(finalSeries.describe().to_dict().items() + cond_df[groupby].describe().to_dict().items())

    # print finalSeries.shape
    stats['count'] = finalSeries.shape[0]
    return stats

def getScatterplotStats(pID, spec, raw_data) :
    agg = spec['aggregation']
    x = spec['x']['title']
    cond_df = raw_data.dropna()

    stats = {}

    if agg :
        group_obj = cond_df.groupby(x)
        finalSeries = group_obj.size()

        x_vals = cond_df[x].values
        # print finalSeries.shape
        stats['count'] = finalSeries.shape[0]

        ## descriptive stats
        stats['describe'] = cond_df[x].describe().to_dict()

        # print finalSeries
        # print "TIME SERIES? ", cond_df[x].is_time_series

        ## OTHERWISE ITS A TIME SERIES VHAT TO DO YO?!
        if (type(finalSeries.index[0]) != str) :
            # linear regression
            lin = linregress(finalSeries.index, finalSeries.values)
            stats['linregress'] = {
                'slope' : lin[0],
                'intercept' : lin[1],
                'r' : lin[2], 
                'p' : lin[3],
                'std_err' : lin[4]
            }

            # normal test
            norm_fit = norm.fit(x_vals)
            gaussian_test = mstats.normaltest(x_vals)
            skewness = skew(x_vals)
            stats['gaussian'] = {
                'mean' : norm_fit[0],
                'std' : norm_fit[1],
                'p' : gaussian_test[1],
                'skewness' : skewness
            }

        else :
            print "TIME SERIES HOHOHO"

    return stats