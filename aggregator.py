import sys, os, dash, csv
import pandas as pd
import numpy as np
import dash_core_components as dcc
import dash_html_components as html

def file_check(file):
    # check if file is 0 bytes
    if os.stat(sys.argv[1]).st_size == 0:
        return False

    try: 
        df = pd.read_csv(file)
        if df.columns[0] == 'Consumer IP':  # for 21.1 PCE version
            return True
        else:
            return False
    except Exception:
        return False

def csv_formatter(df):
    # update the column name to all lower cap and without space
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.lower()
   
    # fill value if the column is empty
    df.fillna({'consumer_role': 'NO_LABEL', 'consumer_app': 'NO_LABEL', 'consumer_env': 'NO_LABEL', 'consumer_loc': 'NO_LABEL'}, inplace=True)
    df.fillna({'provider_role': 'NO-LABEL', 'provider_app': 'NO_LABEL', 'provider_env': 'NO_LABEL', 'provider_loc': 'NO_LABEL'}, inplace=True)

def combine_aggroup_column(formatted_df):
    # create new columns to combine appgroup with location
    df['consumer_appgroup_combined'] = df['consumer_role'] + " | " + df['consumer_app'] + " | " + df['consumer_env'] + " | " + df['consumer_loc']
    df['provider_appgroup_combined'] = df['provider_role'] + " | " + df['provider_app'] + " | " + df['provider_env'] + " | " + df['provider_loc']
    
    # replace the column if 4 tuples are NO_LABEL, it means it is a IPList, replace it as NaN
    df['consumer_appgroup_combined'].replace(['NO_LABEL | NO_LABEL | NO_LABEL | NO_LABEL'], np.nan, regex=True, inplace=True)
    df['provider_appgroup_combined'].replace(['NO_LABEL | NO_LABEL | NO_LABEL | NO_LABEL'], np.nan, regex=True, inplace=True)

def determine_iplist_or_vens_rows(updated_df):
    # if either one column below is NaN, identify the row has iplist
    df_src_iplist = df.loc[(df['consumer_appgroup_combined'].isna()) & (df['provider_appgroup_combined'].notna())]
    df_dst_iplist = df.loc[(df['consumer_appgroup_combined'].notna()) & (df['provider_appgroup_combined'].isna())]

    # sanitize the output for consumer iplist rows
    df_src_iplist_result = df_src_iplist[['consumer_ip', 'consumer_iplist', 'provider_appgroup_combined', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by', 'num_flows']].copy()

    # sanitize the output for provider iplist rows
    df_dst_iplist_result = df_dst_iplist[['consumer_appgroup_combined', 'provider_ip', 'provider_iplist', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by', 'num_flows']].copy()

    # if either one column below is not NaN, identify the row is not contain iplist. both sides are VENs.
    df_both_vens_result = df.loc[(df['consumer_appgroup_combined'].notna()) & (df['provider_appgroup_combined'].notna())]

    # return both VENs fall under intrascope
    df_both_vens_intrascope_result = df.loc[(df['consumer_appgroup_combined']) == (df['provider_appgroup_combined'])]

    # return both VENs fall under extrascope
    df_both_vens_extrascope_result = df.loc[(df['consumer_appgroup_combined']) != (df['provider_appgroup_combined'])]

    return df_src_iplist_result, df_dst_iplist_result, df_both_vens_result, df_both_vens_intrascope_result, df_both_vens_extrascope_result

def consumer_as_iplist_result(df_src_iplist_result):
    # trim the last octet of IP address for better aggregate and dedup as subnet format instead of IP for consumer as iplist
    df_src_iplist_result['consumer_ip'] = df_src_iplist_result['consumer_ip'].str.replace(r'\.\d+$', '.0', regex=True)

    # sorting
    df_src_iplist_result.sort_values(["consumer_ip", "consumer_iplist", "provider_appgroup_combined", "transmission", "port", "protocol", "reported_policy_decision", "reported_by"], ascending=[True, True, True, True, True, True, True, True], inplace=True)

    # sum the num_of_flows when aggregating
    df_src_iplist_result = df_src_iplist_result.groupby(["consumer_ip", "consumer_iplist", "provider_appgroup_combined", "transmission", "port", "protocol", "reported_policy_decision", "reported_by"], axis=0, as_index=True).sum()

    return df_src_iplist_result

def provider_as_iplist_result(df_dst_iplist_result):
    # trim the last octet of IP address for better aggregate and dedup as subnet format instead of IP for provider as iplist
    df_dst_iplist_result['provider_ip'] = df_dst_iplist_result['provider_ip'].str.replace(r'\.\d+$', '.0', regex=True)

    # sorting
    df_dst_iplist_result.sort_values(['consumer_appgroup_combined', 'provider_ip', 'provider_iplist', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by'], ascending=[True, True, True, True, True, True, True, True], inplace=True)

    # sum the num_of_flows when aggregating
    df_dst_iplist_result = df_dst_iplist_result.groupby(['consumer_appgroup_combined', 'provider_ip', 'provider_iplist', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by'], axis=0, as_index=True).sum()

    return df_dst_iplist_result

def both_vens_result(df_both_vens):
    # sanitize the output for both sides are VENs
    df_both_vens_result = df_both_vens[['consumer_appgroup_combined', 'provider_appgroup_combined', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by', 'num_flows']].copy()

    # sorting
    df_both_vens_result.sort_values(['consumer_appgroup_combined', 'provider_appgroup_combined', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by'], ascending=[True, True, True, True, True, True, True], inplace=True)

    # sum the num_of_flows when aggregating
    df_both_vens_result = df_both_vens_result.groupby(['provider_appgroup_combined', 'consumer_appgroup_combined', 'transmission', 'port', 'protocol', 'reported_policy_decision', 'reported_by'], axis=0, as_index=True).sum()

    return df_both_vens_result


#pending
# if 21.2, there is backend report which not havin draft policy, but upto 200k
# explorer gernerated report has draft policy m, byt up to 100k

# might need 19.3 parser also
# first data seen and last data seen, even aggregate


if not file_check(sys.argv[1]):
    print("File is invalid or 0 byte.")
    exit(1)
else:
    df = pd.read_csv(sys.argv[1])
    
updated_df = combine_aggroup_column(csv_formatter(df))
df_src_iplist_result, df_dst_iplist_result, df_both_vens_result, df_both_vens_intrascope_result, df_both_vens_extrascope_result = determine_iplist_or_vens_rows(updated_df)

# reports
consumer_as_iplist_report = consumer_as_iplist_result(df_src_iplist_result)
provider_as_iplist_report = provider_as_iplist_result(df_dst_iplist_result)

# this report combines both intra/extrascope as raw
both_are_ven_report = both_vens_result(df_both_vens_result)
both_vens_intrascope = both_vens_result(df_both_vens_intrascope_result)
both_vens_extrascope = both_vens_result(df_both_vens_extrascope_result)

print(consumer_as_iplist_report)
consumer_as_iplist_report.to_csv('test.csv')
# export as HTML
# html_string = '''
# <html>
#   <head><title>Explorer Flows Report</title></head>
#   <link rel="stylesheet" type="text/css" href="styles.css"/>
#   <h1>{header}</h1>
#   <body>
#     {table}
#   </body>
# </html>
# '''

# with open('index.html', 'w') as f:
#     f.write(html_string.format(header="Consumer as IPList", table=df_src_iplist_result.to_html(classes='table_style')))

###

# source: https://community.plotly.com/t/how-to-populate-a-dropdown-from-unique-values-in-a-pandas-data-frame/5543

# def generate_table(dataframe, max_rows=100):
#     return html.Table(
#         # Header
#         [html.Tr([html.Th(col) for col in dataframe.columns])] +

#         # Body
#         [html.Tr([
#             html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#         ]) for i in range(min(len(dataframe), max_rows))]
#     )

# app = dash.Dash(__name__)

# app.layout = html.Div(children=[
#     html.H4(children='IPList as Consumer'),
#     dcc.Dropdown(id='ciplist_dropdown', options=[
#         {'label': i, 'value': i} for i in df_src_iplist_result.consumer_iplist.unique()
#     ], multi=True, placeholder='Filter Consumer IPList'),
    
#     dcc.Dropdown(id='dappgroups_dropdown', options=[
#     {'label': i, 'value': i} for i in df_src_iplist_result.dst_app_loc_combined.unique()
#     ], multi=True, placeholder='Filter Provider App Group'),
#     html.Div(id='table-container')
# ])

# @app.callback(
#     dash.dependencies.Output('table-container', 'children'),
#     [dash.dependencies.Input('ciplist_dropdown', 'value')]
#     )
# def display_table(ciplist_value):
#     if ciplist_value is None:
#         return generate_table(df_src_iplist_result)
#     dff = df_src_iplist_result[df_src_iplist_result.consumer_iplist.str.contains('|'.join(ciplist_value))]
#     return generate_table(dff)


# if __name__ == '__main__':
#     app.run_server()
