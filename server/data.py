'''
Functions for reading, sampling, and detecting types of datasets 

No manipulation or calculation, only description
'''

import os
import re
import xlrd
import codecs
import pandas as pd
import dateutil.parser as dparser
from flask import json
import csv

from config import config
from werkzeug.utils import secure_filename
from db import MongoInstance as MI


types = {
    'numeric': [
        'integer',
        'float',
        'complex',
        'datetime'
    ],
    'factor': [
        'string',
        'logical',
        'country',
        'continent',
    ]
}


# Return sample of dataset
def get_sample_data(path, start=0, inc=20) :
    end = start + inc  # Upper bound excluded
    header, df = read_file(path)
    df = df.fillna('')
    sample = map(list, df.iloc[start:end].values)

    n_rows, n_cols = df.shape
    types = get_column_types(df)
    extension = path.rsplit('.', 1)[1]
    column_attrs = [{'name': header[i], 'type': types[i], 'column_id': i} for i in range(0, n_cols)]

    result = {
        'column_attrs': column_attrs,
        'header': list(header),
        'sample': sample,  # json.loads(sample.to_json()),
        'rows': n_rows,
        'cols': n_cols,
        'filetype': extension
    }
    return result


# Dataflow: 
# 1. Save file in uploads/pID directory
# 2. Save file location in project data collection
# 3. Return sample
def upload_file(pID, file):
    # Save file as csv

    filename = secure_filename(file.filename)
    file_type = filename.rsplit('.', 1)[1]
    path = os.path.join(config['UPLOAD_FOLDER'], pID, filename)

    datasets = []

    if file_type in ['csv', 'tsv', 'txt'] :
        path2 = path + ".csv"
        filename2 = filename + ".csv"

        print "Saving file: ", filename
        file.save(path2)
        print "Saved file: ", filename

        dID = MI.insertDataset(pID, path2, filename2)

        result = get_sample_data(path2)
        result.update({
            'title' : filename2.rsplit('.', 1)[0],
            'filename' : filename2,
            'dID' : dID,
        })
        datasets.append(result)


    elif file_type.startswith('xls') :

        print "Saving file: ", filename
        file.save(path)
        print "Saved file: ", filename

        book = xlrd.open_workbook(path)
        sheet_names = book.sheet_names()

        for name in sheet_names :
            sheet = book.sheet_by_name(name)
            path2 = path + "_" + name + ".csv"
            filename2 = filename + "_" + name + ".csv"

            csv_file = open(path2, 'wb')
            wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            for rn in xrange(sheet.nrows) :
                wr.writerow([ unicode(v).encode('utf-8') for v in sheet.row_values(rn) ])
            csv_file.close()

            column_attrs, header, sample, rows, cols, extension = get_uploaded_file_data(path2)

            dID = MI.insertDataset(pID, path2, filename2)
            dataset = {
                'title' : filename2.rsplit('.', 1)[0],
                'filename' : filename2,
                'dID' : dID,
                'column_attrs' : column_attrs,
                'header' : header,
                'sample' : sample,
                'rows' : rows,
                'cols' : cols,
                'filetype' : extension
            }
            datasets.append(dataset)

    elif file_type == 'json' :

        print "Saving file: ", filename
        file.save(path)
        print "Saved file: ", filename

        f = open(path, 'rU')
        json_data = json.load(f)

        path2 = path + ".csv"
        filename2 = filename + ".csv"

        csv_file = open(path2, 'wb')
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        header = json_data[0].keys()

        wr.writerow([v.encode('utf-8') for v in header])

        for i in range(len(json_data)) :
            row = []
            for field in header :
                row.append(json_data[i][field])
            wr.writerow([unicode(v).encode('utf-8') for v in row])
        csv_file.close()

        dID = MI.insertDataset(pID, path + ".csv", filename2)
        column_attrs, header, sample, rows, cols, extension = get_uploaded_file_data(path2)

        dataset = {
            'title' : filename2.rsplit('.', 1)[0],
            'filename' : filename2,
            'dID' : dID,
            'column_attrs' : column_attrs,
            'header' : header,
            'sample' : sample,
            'rows' : rows,
            'cols' : cols,
            'filetype' : extension
        }

        datasets.append(dataset)
    return datasets

# Given a path, reads file and returns headers and a df
def read_file(path, nrows=None):
    extension = path.rsplit('.', 1)[1]

    if extension in ['csv', 'tsv', 'txt']:
        delim = get_delimiter(path)
        df = pd.read_table(path, sep=delim, error_bad_lines=False, nrows=nrows)
        return df.columns.values, df

        # columns = []

        # # TODO Is this the right thing to do?
        # # df[cols]'s are Pandas series? would making it into a list be easier?
        # for col in df :
        #     columns.append(df[col])

        # header = list(df.columns.values)

# Wrapper around read_file to return
# def get_sample_data(path, rows=20):
#     header, df = read_file(path)




# def get_sample_data(path):
#     f = open(path, 'rU')
#     filename = path.rsplit('/')[-1]
#     extension = filename.rsplit('.', 1)[1]

#     ## flat files
#     if extension in ['csv', 'tsv', 'txt'] :
#         delim = get_delimiter(path)
#         header = f.readline()
#         rows = 0
#         cols = 0
#         sample = {}
#         for i in range(20) :
#             line = f.readline()
#             if not line :
#                 break
#             else :
#                 sample[i] = [item.strip().strip('"') for item in line.strip().split(delim)]
#                 cols = max(cols, len(sample[i]))

#         with open(path, 'rU') as f:
#             for rows, l in enumerate(f) :
#                 pass
#         rows += 1

#         header = header.strip().split(delim)

    # ## excel files
    # elif extension.startswith('xls') :
    #     book = xlrd.open_workbook(path, on_demand=True)
    #     ## TODO: multiple sheets? right now only take first sheet

    #     sheet = book.sheet_by_name(sheet_name)
    #     header = sheet.row_values(0)
    #     rows = sheet.nrows
    #     cols = sheet.ncols

    #     sample = {}
    #     for i in range(min(20, sheet.nrows)) :

    #         sample[i] = []
    #         row = sheet.row(i+1)
    #         for cell in row :
    #             if cell.ctype == xlrd.XL_CELL_DATE :
    #                 year, month, day, hour, minute, second = xlrd.xldate_as_tuple(cell.value, book.datemode)
    #                 date_string = '/'.join([str(x) for x in [month, day, year]])
    #                 sample[i].append(date_string)
    #             else :
    #                 sample[i].append(cell.value)
    
    # elif extension == 'json':
    #     json_data = json.load(f)

    #     header = json_data[0].keys()
    #     rows = len(json_data) + 1 ## number of observations, or actual number of rows??
    #     cols = len(header)

    #     sample = {}
    #     for i in range(min(20, len(json_data))) :
    #         row = json_data[i]
    #         sample[i] = [row[field] for field in header]

    f.close()     
    return sample, rows, cols, extension, header


INT_REGEX = "^-?[0-9]+$"
FLOAT_REGEX = "[+-]?(\d+(\.\d*)|\.\d+)([eE][+-]?\d+)?"

COUNTRY_CODE_2 = ['AD', 'AE', 'AF', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AW', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BM', 'BN', 'BO', 'BR', 'BT', 'BW', 'BY', 'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ER', 'ES', 'ET', 'FI', 'FM', 'FO', 'FR', 'GA', 'GB', 'GE', 'GH', 'GI', 'GL', 'GM', 'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KN', 'KP', 'KR', 'KW', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MG', 'MK', 'ML', 'MM', 'MN', 'MR', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PH', 'PK', 'PL', 'PR', 'PS', 'PT', 'PY', 'QA', 'RO', 'RS', 'RU', 'RW', 'SA', 'SC', 'SD', 'SE', 'SG', 'SI', 'SK', 'SL', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SY', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TW', 'TZ', 'UA', 'UG', 'UNK', 'US', 'UY', 'UZ', 'VE', 'VI', 'VN', 'VU', 'WS', 'XK', 'YE', 'ZA', 'ZM', 'ZW']
COUNTRY_CODE_3 = ['AND', 'ARE', 'AFG', 'ATG', 'ALB', 'ARM', 'AGO', 'ARG', 'AUT', 'AUS', 'ABW', 'AZE', 'BIH', 'BRB', 'BGD', 'BEL', 'BFA', 'BGR', 'BHR', 'BDI', 'BEN', 'BMU', 'BRN', 'BOL', 'BRA', 'BTN', 'BWA', 'BLR', 'CAN', 'COD', 'CAF', 'COG', 'CHE', 'CIV', 'CHL', 'CMR', 'CHN', 'COL', 'CRI', 'CUB', 'CPV', 'CYP', 'CZE', 'DEU', 'DJI', 'DNK', 'DOM', 'DZA', 'ECU', 'EST', 'EGY', 'ERI', 'ESP', 'ETH', 'FIN', 'FSM', 'FRO', 'FRA', 'GAB', 'GBR', 'GEO', 'GHA', 'GIB', 'GRL', 'GMB', 'GIN', 'GNQ', 'GRC', 'GTM', 'GNB', 'GUY', 'HKG', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IRL', 'ISR', 'IMN', 'IND', 'IRQ', 'IRN', 'ISL', 'ITA', 'JEY', 'JAM', 'JOR', 'JPN', 'KEN', 'KGZ', 'KHM', 'KIR', 'KNA', 'PRK', 'KOR', 'KWT', 'KAZ', 'LAO', 'LBN', 'LCA', 'LIE', 'LKA', 'LBR', 'LSO', 'LTU', 'LUX', 'LVA', 'LBY', 'MAR', 'MCO', 'MDA', 'MNE', 'MDG', 'MKD', 'MLI', 'MMR', 'MNG', 'MRT', 'MLT', 'MUS', 'MDV', 'MWI', 'MEX', 'MYS', 'MOZ', 'NAM', 'NER', 'NGA', 'NIC', 'NLD', 'NOR', 'NPL', 'NRU', 'NZL', 'OMN', 'PAN', 'PER', 'PHL', 'PAK', 'POL', 'PRI', 'PSE', 'PRT', 'PRY', 'QAT', 'ROU', 'SRB', 'RUS', 'RWA', 'SAU', 'SYC', 'SDN', 'SWE', 'SGP', 'SVN', 'SVK', 'SLE', 'SEN', 'SOM', 'SUR', 'SSD', 'STP', 'SLV', 'SYR', 'SWZ', 'TCD', 'TGO', 'THA', 'TJK', 'TLS', 'TKM', 'TUN', 'TON', 'TUR', 'TTO', 'TWN', 'TZA', 'UKR', 'UGA', 'UNK', 'USA', 'URY', 'UZB', 'VEN', 'VIR', 'VNM', 'VUT', 'WSM', 'SCG', 'YEM', 'ZAF', 'ZMB', 'ZWE']
COUNTRY_NAMES = ['Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Albania', 'Armenia', 'Angola', 'Argentina', 'Austria', 'Australia', 'Aruba', 'Azerbaijan', 'Bosnia and Herzegovina', 'Barbados', 'Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 'Bahrain', 'Burundi', 'Benin', 'Bermuda', 'Brunei', 'Bolivia', 'Brazil', 'Bhutan', 'Botswana', 'Belarus', 'Canada', 'Democratic Republic of Congo', 'Central African Republic', 'Congo [Republic]', 'Switzerland', 'Chile', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cuba', 'Cape Verde', 'Cyprus', 'Czech Republic', 'Germany', 'Djibouti', 'Denmark', 'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Eritrea', 'Spain', 'Ethiopia', 'Finland', 'Micronesia', 'Faroe Islands', 'France', 'Gabon', 'United Kingdom', 'Georgia', 'Ghana', 'Gibraltar', 'Greenland', 'The Gambia', 'Guinea', 'Equatorial Guinea', 'Greece', 'Guatemala', 'Guinea-Bissau', 'Guyana', 'Hong Kong', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'Isle of Man', 'India', 'Iraq', 'Iran', 'Iceland', 'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Saint Kitts and Nevis', 'North Korea', 'South Korea', 'Kuwait', 'Kazakhstan', 'Laos', 'Lebanon', 'St. Lucia', 'Liechtenstein', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco', 'Monaco', 'Moldova', 'Montenegro', 'Madagascar', 'Republic of Macedonia', 'Mali', 'Myanmar [Burma]', 'Mongolia', 'Mauritania', 'Malta', 'Mauritius', 'Maldives', 'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'New Zealand', 'Oman', 'Panama', 'Peru', 'Philippines', 'Pakistan', 'Poland', 'Puerto Rico', 'Palestine', 'Portugal', 'Paraguay', 'Qatar', 'Romania', 'Serbia', 'Russia', 'Rwanda', 'Saudi Arabia', 'Seychelles', 'Sudan', 'Sweden', 'Singapore', 'Slovenia', 'Slovakia', 'Sierra Leone', 'Senegal', 'Somalia', 'Suriname', 'South Sudan', 'El Salvador', 'Syria', 'Swaziland', 'Chad', 'Togo', 'Thailand', 'Tajikistan', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Tonga', 'Turkey', 'Trinidad and Tobago', 'Taiwan', 'Tanzania', 'Ukraine', 'Uganda', 'Unknown', 'United States', 'Uruguay', 'Uzbekistan', 'Venezuela', 'U.S. Virgin Islands', 'Vietnam', 'Vanuatu', 'Samoa', 'Kosovo', 'Yemen', 'South Africa', 'Zambia', 'Zimbabwe']
CONTINENT_NAMES = ['Asia', 'Europe', 'North America', 'South America', 'Australia', 'Antarctica', 'Africa']

# Utility function to get the type of a variable
# TODO: Parse dates
# TODO: Write algorithm to get best estimate given a sample, not a single variable
def get_variable_type(v):
    v = str(v)
    # Numeric
    if re.match(INT_REGEX, v): 
        return "integer"
    elif re.match(FLOAT_REGEX, v):
        return "float"

    # Factors    
    else: 
        try:
            if dparser.parse(v):
                return "datetime"
        except:
            pass
        # if (v in COUNTRY_CODE_2) or (v in COUNTRY_CODE_3) or (v in COUNTRY_NAMES): r = 'country'
        if (v in COUNTRY_CODE_3): r = 'country'
        elif v in CONTINENT_NAMES: r = 'continent'
        else:
            r = "string"
    return r


# Utility function to detect extension and return delimiter
def get_delimiter(path):
    f = open(path, 'rU')
    filename = path.rsplit('/')[-1]
    extension = filename.rsplit('.', 1)[1]
    if extension == 'csv':
        delim = ','
    elif extension == 'tsv':
        delim = '\t'
    # TODO Detect separators intelligently
    elif extension == 'txt':
        delim = ','
    return delim


def is_numeric(x):
    if x in ['integer', 'float', 'datetime']: return True
    else: return False


# Get column types given a data frame (super naive)
def get_column_types(df):    
    sample_line = [x for x in df.iloc[0]]
    types = [get_variable_type(v) for v in sample_line]
    return types


