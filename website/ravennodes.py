#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ravennodes.py - Neurainodes website
#
# By Jeroz Feb, 2019
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

# Import Modules
import pandas as pd
from flask import Flask, render_template, jsonify

"""
Read generated tables
"""

dfnodes = pd.read_csv("tables/all_nodes.csv")
dfcountry = pd.read_csv("tables/country_frequency.csv")
dfisp = pd.read_csv("tables/ISP_frequency.csv")
dfversion = pd.read_csv("tables/version_frequency.csv")
dfcount = pd.read_csv("tables/node_count.csv")
last_update = dfcount['Date'].astype('str').iloc[-1] + ' GMT'

# Build Neurainodes website
ravennodes = Flask(__name__)

@ravennodes.route('/')
def home():
    """
    Home Page
    """
    return render_template('home.html', data=len(dfnodes),
                           json_time=last_update,
                           tables=[dfcountry.to_html(classes='table',index=False)])

# Build 24h Stats page
@ravennodes.route('/stats/')
def stats():
    """
    Nodes Page
    """
    return render_template('stats.html', tables=[dfcountry.to_html(classes='table',index=False),
                                                 dfisp.to_html(classes='table',index=False),
                                                 dfversion.to_html(classes='table',index=False),
                                                 ])


# Build Nodes page
@ravennodes.route('/nodes/')
def nodes():
    """
    Nodes Page
    """
    return render_template('nodes.html', tables=[dfnodes.to_html(classes='table',index=False)])


# Build Worldmap page
@ravennodes.route('/worldmap/')
def worldmap():
    """
    World Map page
    """
    return render_template('worldmap.html')

# APIs incoming!
# By RealBoktio, May 2022
@ravennodes.route('/api/v0.1/stats/count')
def api_node_count():
    """
    API: return current node count
    """
    count = {
        "count": len(dfnodes),
        "timestamp":last_update
    }
    return jsonify(count)

@ravennodes.route('/api/v0.1/stats/country_top10')
def api_country_top10():
    """
    API: return country Top10
    """
    return jsonify(dfcountry.to_dict(orient='records'))

@ravennodes.route('/api/v0.1/stats/isp_top10')
def api_isp_top10():
    """
    API: return ISP Top10
    """
    return jsonify(dfisp.to_dict(orient='records'))

@ravennodes.route('/api/v0.1/stats/versions')
def api_versions():
    """
    API: return node versions detected
    """
    return jsonify(dfversion.to_dict(orient='records'))

if __name__ == '__main__':
    ravennodes.jinja_env.auto_reload = True
    ravennodes.config['TEMPLATES_AUTO_RELOAD'] = True
    ravennodes.run(debug=False)





