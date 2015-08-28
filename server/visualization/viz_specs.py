from data.access import is_numeric
from itertools import combinations
from data.db import MongoInstance as MI
from viz_stats import *
from scipy import stats as sc_stats

from pprint import pprint
from time import time
import math

# Wrapper function
def get_viz_specs(pID):
    datasets = MI.getData(None, pID)
    properties = MI.getProperty(None, pID)
    ontologies = MI.getOntology(None, pID)

    existing_specs = MI.getSpecs(pID, {})
    enumerated_viz_specs = enumerate_viz_specs(datasets, properties, ontologies)
    filtered_viz_specs = filter_viz_specs(enumerated_viz_specs)
    scored_viz_specs = score_viz_specs(filtered_viz_specs)
    return scored_viz_specs

specific_to_general_type = {
    'float': 'q',
    'integer': 'q',
    'string': 'c',
    'continent': 'c',
    'countryName': 'c',
    'datetime': 'q'
}

# TODO How to document defaults?
aggregation_functions = {
    'sum': np.sum,
    'min': np.min,
    'max': np.max,
    'mean': np.mean,
    'count': np.size
}

elementwise_functions = {
    'add': '+',
    'subtract': '-',
    'multiply': '*',
    'divide': '/'
}

# Freedman-Diaconis rule
# width h = 2 * IQR * n^(-1/3)
# num_bins = (max - min) / h
###
# Get bin specifier (e.g. bin edges) given a numeric vector
###
def get_bin_edges(v, procedure='fd'):
    if procedure is 'fd':
        IQR = np.subtract(*np.percentile(v, [75, 25]))
        bin_width = 2 * IQR * len(v)**(-1/3)
        num_bins = math.floor((max(data) - min(data)) / bin_width)
        bin_edges = np.histogram(v, num_bins)[1]
    return bin_edges

###
# Functions providing only the new specs for each case (subsumed cases are taken care of elsewhere)
###
def A(q_field):
    specs = []

    q_label = q_field['label']

    # { Index: value }
    index_spec = {
        'structure': 'ind:val',
        'args': {
            'field_a': q_label
        },
        'meta': {
            'desc': 'Plot %s against its index' % (q_label)
        }
    }
    specs.append(index_spec)

    if not q_field['unique']:
        # { Value: count }
        count_spec = {
            'structure': 'val:count',
            'args': {
                'field_a': q_label
            },
            'meta': {
                'desc': 'Plot values of %s against count of occurrences' % q_label
            }
        }
        specs.append(count_spec)

    # TODO Implement binning algorithm
    # { Bins: Aggregate(binned values) }
    for agg_fn in aggregation_functions.keys():
        bin_spec = {
            'structure': 'bin:agg',
            'args': {
                'agg_fn': agg_fn,
                'agg_field_a': q_label,
                'binning_spec': 0,
                'binning_field': q_label
            },
            'meta': {
                'desc': 'Bin %s, then aggregate binned values by %s' % (q_label, agg_fn)
            }
        }
        specs.append(bin_spec)
    return specs

def B(q_fields):
    specs = []

    # Function on pairs of columns
    for (field_a, field_b) in combinations(q_fields, 2):
        label_a = field_a['label']
        label_b = field_b['label']
        for ew_fn, ew_op in elementwise_functions.iteritems():
            derived_column_field = {
                'transform': '2:1',
                'label': "%s %s %s" % (label_a, ew_op, label_b),
                'unique': False  # TODO Run property detection again?
            }
            A_specs = A(derived_column_field)
            specs.extend(A_specs)
    return specs

def C(c_field):
    specs = []
    c_label = c_field['label']

    # TODO Only create if values are non-unique
    spec = {
        'structure': 'val:count',
        'args': {
            'field_a': c_label
        },
        'meta': {
            'desc': 'Unique values of %s mapped to number of occurrences' % (c_label)
        }
    }
    specs.append(spec)
    return specs

def D(c_field, q_field):
    specs = []
    c_label = c_field['label']
    q_label = q_field['label']

    if c_field['unique']:
        spec = {
            'structure': 'val:val',
            'args': {
                'field_a': c_label,
                'field_b': q_label,
            },
            'meta': {
                'desc': 'Plotting raw values of %s against corresponding values of %s' % (c_label, q_label)
            }
        }
        specs.append(spec)
    else:
        for agg_fn in aggregation_functions.keys():
            spec = {
                'structure': 'val:agg',
                'args': {
                    'agg_fn': c_label,
                    'grouped_field': c_label,
                    'agg_field': q_label,
                },
                'meta': {
                    'desc': 'Plotting raw values of %s against corresponding values of %s, aggregated by %s' % (c_label, q_label, agg_fn)
                }
            }
            specs.append(spec)
    return specs

def E(c_field, q_fields):
    specs = []

    # Two-field agg:agg
    if not c_field['unique']:
        c_label = c_field['label']
        for (q_field_a, q_field_b) in combinations(q_fields, 2):
            q_label_a, q_label_b = q_field_a['label'], q_field_b['label']
            for agg_fn in aggregation_functions.keys():
                spec = {
                    'structure': 'agg:agg',
                    'args': {
                        'agg_fn': agg_fn,
                        'agg_field_a': q_label_a,
                        'agg_field_b': q_label_b,
                        'grouped_field': c_label
                    },
                    'meta': {
                        'desc': 'Plotting aggregated values of %s against aggregated values of %s, grouped by %s' % (q_label_a, q_label_b, c_label)
                    }
                }
    return specs

def F(c_fields):
    specs = []

    # Two-field val:val
    for (c_field_a, c_field_b) in combinations(c_fields, 2):
        c_label_a, c_label_b = c_field_a['label'], c_field_b['label']
        spec = {
            'structure': 'val:val',
            'args': {
                'field_a': c_label_a,
                'field_b': c_label_b
            },
            'meta': {
                'desc': 'Plotting values of %s against corresponding values of %s' % (c_label_a, c_label_b)
            }
        }
        specs.append(spec)
    return specs

def G(c_fields, q_field):
    specs = []
    # TODO How do you deal with this?
    # Two-field val:val:q with quantitative data
    for (c_field_a, c_field_b) in combinations(c_fields, 2):
        c_label_a, c_label_b = c_field_a['label'], c_field_b['label']
        q_label = q_field['label']
        spec = {
            'structure': 'val:val:q',
            'args': {
                'field_a': c_label_a,
                'field_b': c_label_b,
                'data_field_a': q_label
            },
            'meta': {
                'desc': 'Plotting values of %s against corresponding values of %s with attached data field %s' % (c_label_a, c_label_b, q_label)
            }
        }
        specs.append(spec)
    return specs

def H(c_fields, q_fields):
    specs = []
    # TODO How do you deal with this?
    # Two-field val:val:[q] with quantitative data
    for (c_field_a, c_field_b) in combinations(c_fields, 2):
        c_label_a, c_label_b = c_field_a['label'], c_field_b['label']
        q_labels = [ f['label'] for f in q_fields ]
        spec = {
            'structure': 'val:val:q',
            'args': {
                'field_a': c_label_a,
                'field_b': c_label_b,
                'data_fields': q_labels
            },
            'meta': {
                'desc': 'Plotting values of %s against corresponding values of %s with attached data fields %s' % (c_label_a, c_label_b, q_labels)
            }
        }
        specs.append(spec)
    return specs

def specs_to_viz_types(specs):
    result = []
    return result

def score_specs(specs):
    scored_specs = specs
    return scored_specs

# TODO Move the case classifying into dataset ingestion (doesn't need to be here!)
# 1) Enumerated viz specs given data, properties, and ontologies
def enumerate_viz_specs(datasets, properties, ontologies):
    dIDs = [ d['dID'] for d in datasets ]
    specs_by_dID = dict([(dID, []) for dID in dIDs])

    types_by_dID = {}
    fields_by_dID = {}

    for p in properties:
        dID = p['dID']
        relevant_fields = {
            'label': p['label'],
            'unique': p['unique'],
            'type': p['type'],
            'normality': p['normality'],
            'values': p['values']
        }
        if dID in fields_by_dID:
            # TODO Necessary to preserve the order of fields?
            fields_by_dID[dID].append(relevant_fields)
        else:
            fields_by_dID[dID] = [ relevant_fields ]

    # Iterate through datasets (no cross-dataset visualizations for now)
    for dID in fields_by_dID.keys():
        specs = []

        c_fields = []
        q_fields = []
        fields = fields_by_dID[dID]
        for f in fields:
            general_type = specific_to_general_type[f['type']]
            if general_type is 'q':
                q_fields.append(f)
            elif general_type is 'c':
                c_fields.append(f)

        c_count = len(c_fields)
        q_count = len(q_fields)


        # Cases A - B
        # Q > 0, C = 0
        # TODO Formalization for specs
        if q_count and not c_count:
            # Case A) Q = 1, C = 0
            if q_count == 1:
                print "Case A"
                q_field = q_fields[0]
                A_specs = A(q_field)
                specs.extend(A_specs)
            elif q_count >= 1:
                print "Case B"
                for q_field in q_fields:
                    A_specs = A(q_field)
                    specs.extend(A_specs)
                B_specs = B(q_fields)
                specs.extend(B_specs)

        # Cases C - E
        # C = 1
        elif c_count == 1:
            # Case C) C = 1, Q = 0
            if q_count == 0:
                print "Case C"
                c_field = c_fields[0]
                C_specs = C(c_field)
                specs.extend(C_specs)

            # Case D) C = 1, Q = 1
            elif q_count == 1:
                print "Case D"

                # One case of A
                q_field = q_fields[0]
                A_specs = A(q_field)
                specs.extend(A_specs)

                # One case of C
                c_field = c_fields[0]
                C_specs = C(c_field)
                specs.extend(C_specs)

                # One case of D
                c_field, q_field = c_fields[0], q_fields[0]
                D_specs = D(c_field, q_field)
                specs.extend(D_specs)

            # Case E) C = 1, Q >= 1
            elif q_count > 1:
                print "Case E"

                # N_Q cases of A
                for q_field in q_fields:
                    A_specs = A(q_field)
                    specs.extend(A_specs)

                # N_C cases of C
                for c_field in c_fields:
                    C_specs = C(c_field)
                    specs.extend(C_specs)

                # One case of B
                B_specs = B(q_fields)
                specs.extend(B_specs)

                # One case of E
                E_specs = E(c_field, q_fields)
                specs.extend(E_specs)

        # Cases F - H
        # C >= 1
        elif c_count >= 1:
            # Case F) C >= 1, Q = 0
            if q_count == 0:
                print "Case F"

                # N_C cases of C
                for c_field in c_fields:
                    C_specs = C(c_field)
                    specs.extend(C_specs)

                # One case of F
                F_specs = F(c_fields)
                specs.extend(F_specs)

            # Case G) C >= 1, Q = 1
            elif q_count == 1:
                print "Case G"
                q_field = q_fields[0]

                # N_C cases of D
                for c_field in c_fields:
                    D_specs = D(c_field, q_field)
                    specs.extend(D_specs)

                # One case of F
                F_specs = F(c_fields)
                specs.extend(F_specs)

                # One case of G
                G_specs = G(c_fields, q_field)
                specs.extend(G_specs)

            # Case H) C >= 1, Q > 1
            elif q_count > 1:
                print "Case H"

                # N_C cases of C
                # N_C cases of E
                for c_field in c_fields:
                    C_specs = C(c_field)
                    specs.extend(C_specs)

                    E_specs = E(c_field, q_fields)
                    specs.extend(E_specs)


                # N_Q cases of A
                # N_Q cases of G
                for q_field in q_fields:
                    A_specs = A(q_field)
                    specs.extend(A_specs)

                    G_specs = G(c_fields, q_field)
                    specs.extend(G_specs)

                # One case of B
                B_specs = B(q_fields)
                specs.extend(B_specs)

                # One case of F
                F_specs = F(c_fields)
                specs.extend(F_specs)

        specs_by_dID[dID] = specs

        print "\tN_c:", c_count
        print "\tN_q:", q_count
        print "\tNumber of specs:", len(specs_by_dID[dID])
        # pprint(specs_by_dID)
    return specs_by_dID
# 2) Filtering enumerated viz specs based on interpretability and renderability
def filter_viz_specs(enumerated_viz_specs):
    filtered_viz_specs = enumerated_viz_specs
    return filtered_viz_specs

# 3) Scoring viz specs based on effectiveness, expressiveness, and statistical properties
def score_viz_specs(filtered_viz_specs):
    scored_viz_specs = filtered_viz_specs
    return scored_viz_specs
