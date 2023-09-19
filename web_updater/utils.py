#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py - Neurainodes Website Data Updater.
#
# By Jeroz, 2019
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
This code contains a plot and table writer for the ravennodes.com website.
Although using a database (e.g. SQL) might be better suited for this purpose, I chose to keep everything in Python
for self-educational purposes.
"""

import re
import glob
import os.path
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as mapplot

pd.options.mode.chained_assignment = None


class CONF:
    # Filter out PGN nodes
    ignore_version_min = 70015
    ignore_version_max = 70035
    tables_export_folder = 'tables'
    html_export_folder = 'templates'
    country_dict = 'country_dict.csv'


def read_json_file(path_to_file):
    """
    Reads Json File into memory
    """
    with open(path_to_file) as p:
        # Read file
        df = pd.read_json(p)
        # Remove outdated versions
        df = df[df[2] > CONF.ignore_version_min]
        df = df[df[2] < CONF.ignore_version_max]
        
        # Get version
        version_string_split = [re.split('[()]', line) for line in df[3]]
        df[3] = [version_string[0].replace("/", "") for version_string in version_string_split]

        # Cast variables for memory efficiency
        df[1] = df[1].astype(np.int16)
        df[2] = df[2].astype(np.int32)
        df[3] = df[3].astype('category')
        df[4] = df[4].astype(np.uint32)
        df[5] = df[5].astype(np.int8)
        df[6] = df[6].astype(np.uint32)
        df[7] = df[7].astype('category')
        df[8] = df[8].astype('category')
        df[9] = df[9].astype('category')
        df[10] = df[10].astype(np.float16)
        df[11] = df[11].astype(np.float16)
        df[12] = df[12].astype('category')
        df[13] = df[13].astype('category')
        df[14] = df[14].astype('category')
        df[15] = os.path.splitext(os.path.basename(path_to_file))[0]
        df[15] = df[15].astype(np.uint32)
        
        # Rename columns
        df.columns = ['IP', 'Port', 'Codeversion', 'Version', 'Timefound', 'unknown', 'Block Height', 'rdns', 'City',
                      'Country ID', 'Latitude', 'Longitude', 'Locality', 'ASnumber', 'ISP', 'Crawl']

        # Add user agent comment
        df['uacomment'] = [version_string[1] if len(version_string) > 1 else '' for version_string in version_string_split]

        return df


def import_list(json_files):
    """
    Imports all json files into a list
    """
    return [read_json_file(path) for path in json_files]


def find_age(ip_list, json_data):
    """
    Imports all json files into a list
    """
    return [min(json_data['Crawl'][json_data['IP'] == IP]) for IP in ip_list]


def parse_data(json_folder, output_folder, json_data, new_file, init):
    """
    Creates all plots and tables
    """
    # Debugging:
    #json_folder = 'data'
    #output_folder = '.'

    json_files = glob.glob(json_folder + '/*.json')

    # Debugging
    #json_data = pd.concat(import_list(json_files))

    if init:
        # Read and return all available data
        return pd.concat(import_list(json_files))
    else:
        # Read new files
        print('reading new file: ' + new_file)
        json_data = pd.concat([json_data, read_json_file(new_file)])

        # Get total node count and crawl time of frames
        dfcount = pd.value_counts(json_data['Crawl']).to_frame().reset_index()
        dfcount.columns = ['Date', 'Node Count']

        # Get most recent data
        dfcurrent = json_data[json_data.Crawl == max(dfcount['Date'])]
        dfcurrent_info = dfcurrent.copy()

        # Add IDs
        dfcurrent_info.insert(0, 'ID', range(1, len(dfcurrent_info) + 1))
        # Add initial time
        dfcurrent_info['init'] = find_age(dfcurrent_info['IP'], json_data)
        # Add age in seconds
        dfcurrent_info['AgeSec'] = max(dfcount['Date']) - dfcurrent_info['init']
        # Add age
        day = dfcurrent_info['AgeSec'] // (24 * 3600)
        time = dfcurrent_info['AgeSec'] % (24 * 3600)
        hour = time // 3600
        dfcurrent_info['Age'] = day.astype(str) + ' days ' + hour.astype(str) + ' hours'

        # Get node frequency across all data points
        node_freq = json_data.groupby(['IP', 'Port']).size().reset_index(name="freq")
        # Add node frequency
        dfcurrent_info = dfcurrent_info.merge(node_freq, how='inner', left_on=['IP', 'Port'], right_on=['IP', 'Port'])
        # Add max possible node freq
        dfcurrent_info['freq_max'] = [len(dfcount[dfcount['Date'] >= init]) for init in dfcurrent_info['init']]
        # Calculate reachability
        dfcurrent_info['Reachability'] = round(dfcurrent_info['freq'] / dfcurrent_info['freq_max'] * 100, 2)

        # New today are:
        dfcurrent_info['24hNew'] = 'rgb(246, 147, 51)'
        #for i in range(len(dfcurrent)):
        #    if dfcurrent_info['AgeSec'][i] < 86400:
        #        dfcurrent_info['24hNew'][i] = 'rgb(246, 51, 223)'


        # Add full country and 3letter names
        dfcountry = pd.read_csv(CONF.country_dict, sep=',', dtype='category')
        dfcurrent = dfcurrent.merge(dfcountry, how='inner', left_on=['Country ID'], right_on=['2let'])

        """
        Tables
        """
        print("Building Tables...")
        # Order Count data
        dfcount['Date'] = pd.to_datetime(dfcount['Date'], unit='s')
        dfcount = dfcount.sort_values('Date')
        dfcount = dfcount.reset_index(drop=True)
        dfcount.to_csv(os.path.join(output_folder, CONF.tables_export_folder, 'node_count.csv'), index=False, sep=',')

        # Build table for presentation
        df = dfcurrent[['IP', 'Port', 'Version','uacomment', 'Block Height', 'City', 'Country ID', 'Latitude', 'Longitude',
                        'ISP', 'Country Name']]
        df = df.merge(dfcurrent_info[['IP', 'Port', 'Age', 'Reachability']], how='inner', left_on=['IP', 'Port'],
                      right_on=['IP', 'Port'])

        # Add counter
        df.insert(0, '#', range(1, len(df) + 1))
        df.to_csv(os.path.join(output_folder, CONF.tables_export_folder, 'all_nodes.csv'), index=False, sep=',')

        # Country Freq table
        country_freq = pd.value_counts(dfcurrent['Country Name']).to_frame().reset_index()
        country_freq.columns = ['Country', 'Nodes']
        country_freq.insert(0, 'Rank', range(1, len(country_freq) + 1))
        country_freq['%'] = round(country_freq.Nodes / len(df) * 100, 2)
        country_freq = country_freq.head(10)
        country_freq.to_csv(os.path.join(output_folder, CONF.tables_export_folder, 'country_frequency.csv'),
                            index=False, sep=',')

        # Version Freq table
        version_freq = pd.value_counts(dfcurrent['Version']).to_frame().reset_index()
        version_freq.columns = ['Version', 'Count']
        version_freq['%'] = round(version_freq.Count / len(df) * 100, 2)
        version_freq.to_csv(os.path.join(output_folder, CONF.tables_export_folder, 'version_frequency.csv'),
                            index=False, sep=',')

        # ISP Freq table
        isp_freq = pd.value_counts(dfcurrent['ISP']).to_frame().reset_index()
        isp_freq.columns = ['ISP', 'Count']
        isp_freq['%'] = round(isp_freq.Count / len(df) * 100, 2)
        isp_freq = isp_freq.head(10)
        isp_freq.to_csv(os.path.join(output_folder, CONF.tables_export_folder, 'ISP_frequency.csv'),
                        index=False, sep=',')

        """
        World Map
        """
        print("Building Plots...")
        dfcurrent = dfcurrent.merge(dfcurrent_info[['IP', 'Port', 'Age', 'Reachability', '24hNew']], how='inner',
                                    left_on=['IP', 'Port'],right_on=['IP', 'Port'])

        versions = sorted(list(version_freq['Version']))
        node_versions = []
        for i in range(len(versions)):
            df_version = dfcurrent[dfcurrent['Version'] == versions[i]]
            node_version = dict(
                type='scattergeo',
                lon=df_version['Longitude'],
                lat=df_version['Latitude'],
                text=df_version['Latitude'].astype(str) + ', ' + df_version['Longitude'].astype(str) + '<BR>' +
                     df_version['IP'] + '<BR>Port: ' + df_version['Port'].astype(str) + '<BR>' +
                     df_version['Version'].astype(str) + '<BR>' + df_version['City'].astype(str) + '<BR>'
                     + df_version['Country Name'].astype(str) + '<BR>Age: ' + df_version['Age'] +
                     '<BR>Reachability: ' + df_version['Reachability'].astype(str) + '%',
                hoverinfo='text',
                mode='markers',
                marker=dict(
                    size=5+0.1*df_version['Reachability'],
                    opacity=0.7,
                    color=df_version['24hNew'],
                    #line=dict(
                    #    color=new_node_color,
                    #    width=2
                    #)

                ),
                name=versions[i]
            )
            node_versions.append(node_version)

        # Add Crawler location
        node_version = dict(
            type='scattergeo',
            lon=[-77.4875],
            lat=[39.0437],
            text='39.0437, -77.4875 <BR> Neurainodes',
            hoverinfo='text',
            mode='markers',
            marker=dict(
                size=15,
                opacity=1,
                color='rgb(57, 65, 130)',

            ),
            name='Neurainodes'
        )
        node_versions.append(node_version)

        # Geo Styles
        theme1 = dict(
            showframe=False,
            showcoastlines=True,
            showcountries=False,
            coastlinecolor='rgb(57, 65, 130)')
        theme2 = dict(
            showframe=False,
            showcoastlines=False,
            showcountries=True,
            showland=True,
            landcolor='rgb(230, 230, 250)',
            countrycolor='rgb(255, 255, 255)',
            coastlinecolor='rgb(57, 65, 130)')
        theme3 = dict(
            showframe=False,
            showcoastlines=False,
            showcountries=True,
            showland=True,
            landcolor='rgb(68, 68, 68)',
            countrycolor='rgb(153, 153, 153)',
            showocean=True,
            oceancolor='rgb(0, 0, 0)',
            paper_bgcolor='rgb(0,0,0)')

        # Build layouts
        layout1 = dict(
            geo=theme1,
            showlegend=False,
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
        )
        layout2 = dict(
            geo=theme1,
            legend=dict(orientation="h"),
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
        )

        # Build Customization buttons
        updatemenus = list([
            dict(
                buttons=list([
                    dict(
                        args=['geo', theme1],
                        label='RVN-Continents',
                        method='relayout'
                    ),
                    dict(
                        args=['geo', theme2],
                        label='RVN-Countries',
                        method='relayout'
                    ),
                ]),
                direction='down',
                pad={'r': 10, 't': 10},
                showactive=True,
                x=0.1,
                xanchor='left',
                y=1.1,
                yanchor='top'
            ),
        ])

        annotations = list([
            dict(text='Theme:', x=0.06, y=1.08, yref='paper', align='left', showarrow=False),
            dict(text='Double click to isolate node versions:', x=0.008, y=-0.1, yref='paper', align='left',
                 showarrow=False)
        ])

        layout2['updatemenus'] = updatemenus
        layout2['annotations'] = annotations

        fig1 = dict(data=node_versions, layout=layout1)
        fig2 = dict(data=node_versions, layout=layout2)

        # Interactive Map
        mapplot.plot(fig1, auto_open=False,
                     filename=os.path.join(output_folder, CONF.html_export_folder, 'map_small.html'))
        mapplot.plot(fig2, auto_open=False,
                     filename=os.path.join(output_folder, CONF.html_export_folder, 'map_big.html'))

        """
        Node Count Plot
        """
        data = [go.Scatter(x=dfcount['Date'],
                           y=dfcount['Node Count'],
                           text='Date: ' + dfcount['Date'].astype('str') + '<BR>' +
                                'Node Count: ' + dfcount['Node Count'].astype('str'),
                           hoverinfo='text',
                           marker=dict(color='rgb(246, 147, 51)'),
                           showlegend=False)]

        layout = dict(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label='1d',
                             step='day',
                             stepmode='backward'),
                        dict(count=7,
                             label='7d',
                             step='day',
                             stepmode='backward'),
                        dict(step='all')
                    ])
                ),
                rangeslider=dict(
                    visible=True,
                    bordercolor='black',
                    activecolor='#444',
                    borderwidth=1
                ),
                type='date'
            )
        )

        fig = dict(data=data, layout=layout)

        mapplot.plot(fig, validate=False, auto_open=False,
                     filename=os.path.join(output_folder, CONF.html_export_folder, 'nodecount.html'))
        print("Done.")

        return json_data
