# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# standard library
import os
import pathlib

# dash libs
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_daq as daq

import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.express as px
import flask

#import constants


# pydata stack
import pandas as pd
import numpy as np

# app initialize
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
server = app.server
app.config["suppress_callback_exceptions"] = True

# Load data
diplome_dut = pd.read_csv("fr-esr-insertion_professionnelle-dut_donnees_nationales.csv", sep=';', na_values = ['ns', 'nd'], na_filter=False)
diplome_lp = pd.read_csv("fr-esr-insertion_professionnelle-lp.csv", sep=';', na_values = ['ns', 'nd'], na_filter=False)
diplome_master = pd.read_csv("fr-esr-insertion_professionnelle-master.csv", sep=';', na_values = ['ns', 'nd'], na_filter=False)

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Insertion professionnelle")
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="à propos", n_clicks=0
                    ),
                ],
            ),
        ],
    )

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Echtls-tab",
                        label="Distribution des échantillons",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="An-tab",
                        label="Statistiques par an",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Disciplines-tab",
                        label="Distribution des disciplines",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Ville-tab",
                        label="Statistiques par ville",
                        value="tab4",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

def init_df():
    return 0

def build_graph_title(title):
    return html.P(className="graph-title", children=title)

def build_tab_1():
    return [
        html.Div(
            id="top-row-graphs",
            children=[
                html.Div(
                    className="row",
                    children=[
                        # Map
                        html.Div(
                            id="map-container",
                            children=[
                                html.H3(
                                    "Choisissez un diplôme :"
                                ),
                                dcc.RadioItems(
                                    id="mapbox-diplome-selector",
                                    options=[
                                        {"label": "LP", "value": "LP"},
                                        {"label": "Master", "value": "Master"},                                
                                    ],
                                    value="basic",
                                ),
                                html.H3(
                                    "Choisissez une discipline :"
                                ),
                                dcc.RadioItems(
                                    id="mapbox-discipline-selector",
                                    options=[
                                        {
                                            "label": "Sciences, technologies et santé",
                                            "value": "STS"
                                            },
                                        {
                                            "label": "Droit, économie et gestion",
                                            "value": "DEG"
                                            },
                                        {
                                            "label": "Sciences humaines et sociales",
                                            "value": "SHS"
                                            },
                                        {
                                            "label": "Lettres, langues, arts",
                                            "value": "LLA"
                                            },
                                        {
                                            "label": "Masters enseignement",
                                            "value": "ME"
                                            },                                                               
                                    ],
                                    value="basic",
                                ),
                                dcc.Graph(
                                    id="map",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    config={"scrollZoom": True, "displayModeBar": True},
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="row",
                    id="bottom-row",
                    children=[
                        html.H3("Année"),
                        dcc.Slider(
                            min=2013,
                            max=2016,
                            step=None,
                            marks={
                                2013: '2013',
                                2014: '2014',
                                2015: '2015',
                                2016: '2016'
                            },
                            value=4
                        ),
                        # Histogramme
                        html.Div(
                            id="histog-container",
                            className="six columns",
                            children=[
                                dcc.Graph(id="histog"),
                            ],
                        ),
                        html.Div(
                            # barplot
                            id="barplot-container",
                            className="six columns",
                            children=[
                                dcc.Graph(id="barplot"),
                            ],
                        ),
                    ],
                ),
            ]
        )
        
    ]

def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """                    
                                ###### De quoi parle cette application ?
                                Il s'agit de ...
                                ###### Que montre cette application ?
                                ...
                                """
                            )
                        ),
                    ),
                ],
            )
        ),
    )

def build_tab_2():
    return [
        html.Div(
            children=[
                html.Div(
                    id="top-row",
                    children=[
                        html.Div(
                            className="row",
                            id="top-row-header",
                            children=[
                                html.Div(
                                    id="header-container",
                                    children=[
                                        html.H3("Paramètres"),
                                        build_graph_title("Choisissez une discipline :"),
                                        dcc.RadioItems(
                                            id="mapbox-discipline-selector",
                                            options=[
                                                {
                                                    "label": "Sciences, technologies et santé",
                                                    "value": "STS"
                                                    },
                                                {
                                                    "label": "Droit, économie et gestion",
                                                    "value": "DEG"
                                                    },
                                                {
                                                    "label": "Sciences humaines et sociales",
                                                    "value": "SHS"
                                                    },
                                                {
                                                    "label": "Lettres, langues, arts",
                                                    "value": "LLA"
                                                    },
                                                {
                                                    "label": "Masters enseignement",
                                                    "value": "ME"
                                                    },                                                               
                                            ],
                                            value="basic",
                                        ),
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            id="tabs",
                            className="tabs",
                            children=[
                                dcc.Tabs(
                                    id="stats-an-tabs",
                                    value="tab2",
                                    className="custom-tabs",
                                    children=[
                                        dcc.Tab(
                                            id="Femme-an-tab",
                                            label="Part des femmes",
                                            children=[
                                                html.Div(
                                                    id="Femme-an-container",
                                                    children=html.H3("Part des femmes")
                                                    )
                                            ],
                                            value="tab21",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        dcc.Tab(
                                            id="Insertion-an-tab",
                                            label="Taux d'insertion",
                                            children=[
                                                html.Div(
                                                    id="Insertion-an-container",
                                                    children=html.H3("Taux d'insertion")
                                                    )
                                            ],
                                            value="tab22",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        dcc.Tab(
                                            id="Emploi-an-tab",
                                            label="Statistiques des emplois",
                                            children=[
                                                html.Div(
                                                    id="Emploi-an-container",
                                                    children=html.H3("Statistiques des emplois")
                                                    )
                                            ],
                                            value="tab23",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        dcc.Tab(
                                            id="Salaires-an-tab",
                                            label="Statistiques des salaires",
                                            children=[
                                                html.Div(
                                                    id="Salaires-an-container",
                                                    children=html.H3("Statistiques des salaires")
                                                    )
                                            ],
                                            value="tab24",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],            
        ),
    ]

def build_tab_3():
    return [
        html.Div(
            id="stats-an-graphs",
            children=[
                html.Div(
                    id="top-row",
                    children=[
                        html.H3("Paramètres"),
                        html.Div(
                            id="header-container",
                            children=[
                                build_graph_title("Choisissez une discipline :"),
                                dcc.RadioItems(
                                    id="mapbox-discipline-selector",
                                    options=[
                                        {
                                            "label": "Sciences, technologies et santé",
                                            "value": "STS"
                                            },
                                        {
                                            "label": "Droit, économie et gestion",
                                            "value": "DEG"
                                            },
                                        {
                                            "label": "Sciences humaines et sociales",
                                            "value": "SHS"
                                            },
                                        {
                                            "label": "Lettres, langues, arts",
                                            "value": "LLA"
                                            },
                                        {
                                            "label": "Masters enseignement",
                                                    "value": "ME"
                                            },                                                               
                                    ],
                                    value="basic",
                                ),
                            ],
                        ),
                        html.Div(
                            id="header-container2",
                            children=[
                                build_graph_title("Année"),
                                dcc.Slider(
                                    min=2013,
                                    max=2016,
                                    step=None,
                                    marks={
                                        2013: '2013',
                                        2014: '2014',
                                        2015: '2015',
                                        2016: '2016'
                                    },
                                    value=4
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="tabs",
                    className="tabs",
                    children=[
                        dcc.Tabs(
                            id="stats-discipline-tabs",
                            value="tab4",
                            className="custom-tabs",
                            children=[
                                dcc.Tab(
                                    id="Femme-discipline-tab",
                                    label="Part des femmes",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Femme-discipline-container",
                                            children=[
                                                # Formation des histogrammes
                                                html.H3("Part des femmes"),
                                                # Formation des violins
                                                html.H3("Part des femmes 2"),
                                                ],
                                            ),
                                        ],
                                    value="tab21",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                dcc.Tab(
                                    id="Insertion-discipline-tab",
                                    label="Taux d'insertion",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Insertion-discipline-container",
                                            children=[
                                                # Formation des histogrammes
                                                html.H3("Taux d'insertion"),
                                                # Formation des violins
                                                html.H3("Taux d'insertion 2"),
                                                ],
                                            ),
                                        ],
                                    value="tab22",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                dcc.Tab(
                                    id="Emploi-discipline-tab",
                                    label="Taux d'emplois",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Emploi-discipline-container",
                                            children=[
                                                # Formation des histogrammes
                                                html.H3("Statistiques des emplois"),
                                                # Formation des violins
                                                html.H3("Statistiques des emplois 2"),
                                                ],
                                            ),
                                        ],
                                    value="tab23",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                dcc.Tab(
                                    id="Salaires-discipline-tab",
                                    label="Salaires",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Salaires-discipline-container",
                                            children=[
                                                # Formation des histogrammes
                                                html.H3("Statistiques des salaires"),
                                                # Formation des violins
                                                html.H3("Statistiques des salaires 2"),
                                                ],
                                            ),
                                        ],
                                    value="tab24",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
    ]

def build_tab_4():
    return [
        html.Div(
            className="row",
            id="sats-ville-graphs",
            children=[
                # Map
                html.Div(
                    id="map-container",
                    children=[
                        html.H3("Année"),
                        dcc.Slider(
                            min=2013,
                            max=2016,
                            step=None,
                            marks={
                                2013: '2013',
                                2014: '2014',
                                2015: '2015',
                                2016: '2016'
                            },
                            value=4
                        ),
                        html.H3(
                            "Choisissez un diplôme :"
                        ),
                        dcc.RadioItems(
                            id="mapbox-diplome-selector",
                            options=[
                                {"label": "LP", "value": "LP"},
                                {"label": "Master", "value": "Master"},                                
                            ],
                            value="basic",
                        ),
                        html.H3(
                            "Choisissez une discipline :"
                        ),
                        dcc.RadioItems(
                            id="mapbox-discipline-selector",
                            options=[
                                {
                                    "label": "Sciences, technologies et santé",
                                    "value": "STS"
                                    },
                                {
                                    "label": "Droit, économie et gestion",
                                    "value": "DEG"
                                    },
                                {
                                    "label": "Sciences humaines et sociales",
                                    "value": "SHS"
                                    },
                                {
                                    "label": "Lettres, langues, arts",
                                    "value": "LLA"
                                    },
                                {
                                    "label": "Masters enseignement",
                                    "value": "ME"
                                    },
                                {
                                    "label": "Ensemble des départements d'IUT",
                                    "value": "EDI"
                                    },                                                               
                            ],
                            value="basic",
                        ),
                        html.H3(
                            "Choisissez une statistique :"
                        ),
                        dcc.RadioItems(
                            id="mapbox-stat-selector",
                            options=[
                                {
                                    "label": "Taux d'insertion",
                                    "value": "TI"
                                    },
                                {
                                    "label": "Part des femmes",
                                    "value": "PF"
                                    },
                                {
                                    "label": "Taux d'emplois cadres",
                                    "value": "TEC"
                                    },
                                {
                                    "label": "Taux d'emplois stables",
                                    "value": "TES"
                                    },
                                {
                                    "label": "Taux d'emplois temps plein",
                                    "value": "TETP"
                                    },
                                {
                                    "label": "Salaire net mensuel médian des emplois à temps plein",
                                    "value": "SNMMETP"
                                    },                                                               
                            ],
                            value="basic",
                        ),
                        dcc.Graph(
                            id="map",
                            figure={
                                "layout": {
                                    "paper_bgcolor": "#192444",
                                    "plot_bgcolor": "#192444",
                                }
                            },
                            config={"scrollZoom": True, "displayModeBar": True},
                        ),
                    ],
                ),
            ],
        ),          
    ]

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
    generate_modal(),
        ],
    )

#############################################
# Interaction Between Components / Controller
#############################################

# Template
@app.callback(
    [Output("app-content", "children")],
    [Input("app-tabs", "value")],
)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return build_tab_1()
    elif tab_switch == "tab2":
        return build_tab_2()
    elif tab_switch == "tab3":
        return build_tab_3()
    elif tab_switch == "tab4":
        return build_tab_4()

# ======= Callbacks for modal popup =======
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}

# Running the server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        port=8050
    )