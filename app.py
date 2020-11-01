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
import json

# app initialize
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
server = app.server
app.config["suppress_callback_exceptions"] = True

# Load data
diplome_dut = pd.read_csv("fr-esr-insertion_professionnelle-dut_donnees_nationales.csv", sep=';',na_values=["ns", "nd"])
diplome_lp = pd.read_csv("fr-esr-insertion_professionnelle-lp.csv", sep=';', na_values=["ns", "nd"])
diplome_master = pd.read_csv("fr-esr-insertion_professionnelle-master.csv", sep=';', na_values=["ns", "nd"])

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
                        label="Statistiques par département",
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
                                            id="discipline_par_an",
                                            options=[
                                            {
                                                "label": "Sciences, technologies et santé",
                                                "value": "Sciences, technologies et santé"
                                                },
                                            {
                                                "label": "Droit, économie et gestion",
                                                "value": "Droit, économie et gestion"
                                                },
                                            {
                                                "label": "Sciences humaines et sociales",
                                                "value": "Sciences humaines et sociales"
                                                },
                                            {
                                                "label": "Lettres, langues, arts",
                                                "value": "Lettres, langues, arts"
                                                },
                                            {
                                                "label": "Masters enseignement",
                                                "value": "Masters enseignement"
                                                },
                                            {
                                                "label": "Ensemble des départements d'IUT",
                                                "value": "Ensemble des départements d'IUT"
                                                },                                                             
                                        ],
                                                value="Sciences, technologies et santé",
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
                                                    children=[
                                                        html.H3("Part des femmes"),
                                                        dcc.Graph(id = "part_femmes_par_an")
                                                        ]
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
                                                    children=[
                                                        html.H3("Taux d'insertion"), 
                                                        dcc.Graph(id = "taux_dinsertion_par_an")]
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
                                                    children=[
                                                        html.H3("Statistiques des emplois"),
                                                        dcc.Graph(id = "taux_emplois_cadre_par_an"),
                                                        html.H3("Statistiques des emplois"),
                                                        dcc.Graph(id = "taux_emplois_stables_par_an"),
                                                        html.H3("Statistiques des emplois"),
                                                        dcc.Graph(id = "taux_emplois_temps_plein_par_an")
                                                        ]
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
                                                    children=[
                                                        html.H3("Statistiques des salaires"),
                                                        dcc.Graph(id = "salaire_par_an")]
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

@app.callback(
    dash.dependencies.Output('part_femmes_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_part_femmes_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    part_femmes_par_an = pd.concat([dut[["Année", 'Diplôme', "Part des femmes"]].rename(columns={"Année" : "Annee", "Diplôme": "Diplome"}), 
                                        lp[["Annee", 'Diplôme', '% femmes']].rename(columns={"Diplôme": "Diplome", "% femmes" : "Part des femmes"}), 
                                        master[["annee", 'diplome', 'femmes']].rename(columns={"annee" : "Annee", "diplome": "Diplome", "femmes" : "Part des femmes"})], 
                                       axis = 0)
    part_femmes_par_an = part_femmes_par_an.dropna(axis=0,how='all')
    
    return px.scatter(part_femmes_par_an, x="Annee", y="Part des femmes", color = "Diplome",trendline="ols", marginal_y="box")

@app.callback(
    dash.dependencies.Output('taux_dinsertion_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_dinsertion_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_dinsertion_par_an = pd.concat([dut[["Année", 'Diplôme', "Taux d’insertion"]].rename(columns={"Année" : "Annee", "Diplôme": "Diplome"}), 
                                        lp[["Annee", 'Diplôme', "Taux d’insertion"]].rename(columns={"Diplôme": "Diplome"}), 
                                        master[["annee", 'diplome', "taux_dinsertion"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "taux_dinsertion" : "Taux d’insertion"})], 
                                       axis = 0)
    taux_dinsertion_par_an = taux_dinsertion_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_dinsertion_par_an, x="Annee", y="Taux d’insertion", color = "Diplome",trendline="ols", marginal_y="box")

@app.callback(
    dash.dependencies.Output('taux_emplois_cadre_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_emplois_cadre_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_emplois_cadre_par_an = pd.concat([dut[["Année", 'Diplôme', "Part des emplois de niveau cadre"]].rename(columns={"Année" : "Annee", "Diplôme": "Diplome", "Part des emplois de niveau cadre" : "Emplois cadre"}), 
                                        lp[["Annee", 'Diplôme', "% emplois cadre"]].rename(columns={"Diplôme": "Diplome", "% emplois cadre": "Emplois cadre"}), 
                                        master[["annee", 'diplome', "emplois_cadre"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "emplois_cadre" : "Emplois cadre"})], 
                                       axis = 0)
    taux_emplois_cadre_par_an = taux_emplois_cadre_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_emplois_cadre_par_an, x="Annee", y="Emplois cadre", color = "Diplome",trendline="ols", marginal_y="box")

@app.callback(
    dash.dependencies.Output('taux_emplois_stables_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_emplois_stables_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_emplois_stables_par_an = pd.concat([dut[["Année", 'Diplôme', "Part des emplois stables"]].rename(columns={"Année" : "Annee", "Diplôme": "Diplome", "Part des emplois stables" : "Emplois stables"}), 
                                        lp[["Annee", 'Diplôme', "% emplois stables"]].rename(columns={"Diplôme": "Diplome", "% emplois stables": "Emplois stables"}), 
                                        master[["annee", 'diplome', "emplois_stables"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "emplois_stables" : "Emplois stables"})], 
                                       axis = 0)
    taux_emplois_stables_par_an = taux_emplois_stables_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_emplois_stables_par_an, x="Annee", y="Emplois stables", color = "Diplome",trendline="ols", marginal_y="box")

@app.callback(
    dash.dependencies.Output('taux_emplois_temps_plein_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_emplois_temps_plein_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_emplois_temps_plein_par_an = pd.concat([dut[["Année", 'Diplôme', "Part des emplois à temps plein"]].rename(columns={"Année" : "Annee", "Diplôme": "Diplome", "Part des emplois à temps plein" : "Emplois à temps plein"}), 
                                        lp[["Annee", 'Diplôme', "% emplois à temps plein"]].rename(columns={"Diplôme": "Diplome", "% emplois à temps plein": "Emplois à temps plein"}), 
                                        master[["annee", 'diplome', "emplois_a_temps_plein"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "emplois_a_temps_plein" : "Emplois à temps plein"})], 
                                       axis = 0)
    taux_emplois_temps_plein_par_an = taux_emplois_temps_plein_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_emplois_temps_plein_par_an, x="Annee", y="Emplois à temps plein", color = "Diplome",trendline="ols", marginal_y="box")

@app.callback(
    dash.dependencies.Output('salaire_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_salaire_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    salaire_par_an = pd.concat([dut[["Année", 'Diplôme', "Salaire net mensuel médian des emplois à temps plein"]].rename(columns={"Année" : "Annee", "Diplôme": "Diplome", "Salaire net mensuel médian des emplois à temps plein" : "Salaire"}), 
                                        lp[["Annee", 'Diplôme', "Salaire net médian des emplois à temps plein"]].rename(columns={"Diplôme": "Diplome", "Salaire net médian des emplois à temps plein": "Salaire"}), 
                                        master[["annee", 'diplome', "salaire_net_median_des_emplois_a_temps_plein"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "salaire_net_median_des_emplois_a_temps_plein" : "Salaire"})], 
                                       axis = 0)
    salaire_par_an = salaire_par_an.dropna(axis=0,how='all')
    
    return px.scatter(salaire_par_an, x="Annee", y="Salaire", color = "Diplome",trendline="ols", marginal_y="box")



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
                                    id="discipline_par_domaine",
                                    options=[
                                        {
                                            "label": "Sciences, technologies et santé",
                                            "value": "Sciences, technologies et santé"
                                            },
                                        {
                                            "label": "Droit, économie et gestion",
                                            "value": "Droit, économie et gestion"
                                            },
                                        {
                                            "label": "Sciences humaines et sociales",
                                            "value": "Sciences humaines et sociales"
                                            },
                                        {
                                            "label": "Lettres, langues, arts",
                                            "value": "Lettres, langues, arts"
                                            },
                                        {
                                            "label": "Masters enseignement",
                                            "value": "Masters enseignement"
                                            },
                                        {
                                            "label": "Ensemble des départements d'IUT",
                                            "value": "Ensemble des départements d'IUT"
                                            },                                                             
                                    ],
                                    value = "Sciences, technologies et santé",
                                ),
                            ],
                        ),
                        html.Div(
                            id="header-container2",
                            children=[
                                build_graph_title("Année"),
                                dcc.Slider(
                                    id = "annee_par_domaine",
                                    min=2013,
                                    max=2016,
                                    step=None,
                                    marks={
                                        2013: '2013',
                                        2014: '2014',
                                        2015: '2015',
                                        2016: '2016'
                                    },
                                    value=2013
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
                                                
                                                # Formation des violins
                                                html.H3("Distribution des parts des femmes"),
                                                dcc.Graph(id = "part_femmes_par_domaine")
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
                                                # Formation des violins
                                                html.H3("Distribution des taux d'insertion"),
                                                dcc.Graph(id = "taux_dinsertion_par_domaine"),
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
                                                #html.H3("Statistiques des emplois"),
                                                # Formation des violins
                                                html.H3("Taux d'emplois cadre"),
                                                dcc.Graph(id = "taux_emplois_cadre_par_domaine"), 
                                                html.H3("Taux d'emplois stables"),
                                                dcc.Graph(id = "taux_emplois_stables_par_domaine"),
                                                html.H3("Taux d'emploi à temps plein"),
                                                dcc.Graph(id = "taux_emplois_temps_plein_par_domaine")
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
                                                html.H3("Salaires nets mensuels"),
                                                dcc.Graph(id = "salaire_par_domaine")
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

@app.callback(
    dash.dependencies.Output('taux_dinsertion_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_dinsertion_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_insertion_par_domaine = pd.concat([dut[['Diplôme', "Taux d’insertion"]].rename(columns={"Diplôme": "Diplome"}), 
                                        lp[['Diplôme', 'Taux d’insertion']].rename(columns={"Diplôme": "Diplome"}), 
                                        master[['diplome', 'taux_dinsertion']].rename(columns={"diplome": "Diplome", "taux_dinsertion" : "Taux d’insertion"})], 
                                       axis = 0)
    taux_insertion_par_domaine = taux_insertion_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_insertion_par_domaine, x="Diplome", y="Taux d’insertion", points="all", box = True, color = "Diplome")

@app.callback(
    dash.dependencies.Output('part_femmes_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_part_femmes_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    part_femmes_par_domaine = pd.concat([dut[['Diplôme', "Part des femmes"]].rename(columns={"Diplôme": "Diplome"}), 
                                        lp[['Diplôme', "% femmes"]].rename(columns={"Diplôme": "Diplome", "% femmes" : "Part des femmes"}), 
                                        master[['diplome', 'femmes']].rename(columns={"diplome": "Diplome", "femmes" : "Part des femmes"})], 
                                       axis = 0)
    part_femmes_par_domaine = part_femmes_par_domaine.dropna(axis=0,how='all')
    return px.violin(part_femmes_par_domaine, x="Diplome", y="Part des femmes", points="all", box = True, color = "Diplome")

@app.callback(
    dash.dependencies.Output('taux_emplois_cadre_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_emplois_cadre_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    emplois_cadre_par_domaine = pd.concat([dut[['Diplôme', "Part des emplois de niveau cadre"]].rename(columns={"Diplôme": "Diplome", "Part des emplois de niveau cadre": "Emplois cadre"}), 
                                        lp[['Diplôme', "% emplois cadre"]].rename(columns={"Diplôme": "Diplome", "% emplois cadre" : "Emplois cadre"}), 
                                        master[['diplome', 'emplois_cadre']].rename(columns={"diplome": "Diplome", "emplois_cadre" : "Emplois cadre"})], 
                                       axis = 0)
    emplois_cadre_par_domaine = emplois_cadre_par_domaine.dropna(axis=0,how='all')
    return px.violin(emplois_cadre_par_domaine, x="Diplome", y="Emplois cadre", points="all", box = True, color = "Diplome")

@app.callback(
    dash.dependencies.Output('taux_emplois_stables_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_emplois_stables_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_emplois_stables_par_domaine = pd.concat([dut[['Diplôme', "Part des emplois stables"]].rename(columns={"Diplôme": "Diplome", "Part des emplois stables": "Emplois stables"}), 
                                        lp[['Diplôme', "% emplois stables"]].rename(columns={"Diplôme": "Diplome", "% emplois stables" : "Emplois stables"}), 
                                        master[['diplome', 'emplois_stables']].rename(columns={"diplome": "Diplome", "emplois_stables" : "Emplois stables"})], 
                                       axis = 0)
    taux_emplois_stables_par_domaine = taux_emplois_stables_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_emplois_stables_par_domaine, x="Diplome", y="Emplois stables", points="all", box = True, color = "Diplome")

@app.callback(
    dash.dependencies.Output('taux_emplois_temps_plein_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_emplois_temps_plein_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_emplois_temps_plein_par_domaine = pd.concat([dut[['Diplôme', "Part des emplois à temps plein"]].rename(columns={"Diplôme": "Diplome", "Part des emplois à temps plein": "Emplois à temps plein"}), 
                                        lp[['Diplôme', "% emplois à temps plein"]].rename(columns={"Diplôme": "Diplome", "% emplois à temps plein" : "Emplois à temps plein"}), 
                                        master[['diplome', 'emplois_a_temps_plein']].rename(columns={"diplome": "Diplome", "emplois_a_temps_plein" : "Emplois à temps plein"})], 
                                       axis = 0)
    taux_emplois_temps_plein_par_domaine = taux_emplois_temps_plein_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_emplois_temps_plein_par_domaine, x="Diplome", y="Emplois à temps plein", points="all", box = True, color = "Diplome")

@app.callback(
    dash.dependencies.Output('salaire_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_salaire_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_emplois_temps_plein_par_domaine = pd.concat([dut[['Diplôme', "Salaire net mensuel médian des emplois à temps plein"]].rename(columns={"Diplôme": "Diplome", "Salaire net mensuel médian des emplois à temps plein": "Salaire"}), 
                                        lp[['Diplôme', "Salaire net médian des emplois à temps plein"]].rename(columns={"Diplôme": "Diplome", "Salaire net médian des emplois à temps plein" : "Salaire"}), 
                                        master[['diplome', 'salaire_net_median_des_emplois_a_temps_plein']].rename(columns={"diplome": "Diplome", "salaire_net_median_des_emplois_a_temps_plein" : "Salaire"})], 
                                       axis = 0)
    taux_emplois_temps_plein_par_domaine = taux_emplois_temps_plein_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_emplois_temps_plein_par_domaine, x="Diplome", y="Salaire", points="all", box = True, color = "Diplome")


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
                            id = "annee_carte",
                            min=2013,
                            max=2016,
                            step=None,
                            marks={
                                2013: '2013',
                                2014: '2014',
                                2015: '2015',
                                2016: '2016'
                            },
                            value=2013
                        ),
                        html.H3(
                            "Choisissez un diplôme :"
                        ),
                        dcc.RadioItems(
                            id="diplome_carte",
                            options=[
                                {"label": "LP", "value": "LP"},
                                {"label": "Master", "value": "Master"},                                
                            ],
                            value="LP",
                        ),
                        html.H3(
                            "Choisissez une discipline :"
                        ),
                        dcc.RadioItems(
                            id="discipline_carte",
                            options=[
                                        {
                                            "label": "Sciences, technologies et santé",
                                            "value": "Sciences, technologies et santé"
                                            },
                                        {
                                            "label": "Droit, économie et gestion",
                                            "value": "Droit, économie et gestion"
                                            },
                                        {
                                            "label": "Sciences humaines et sociales",
                                            "value": "Sciences humaines et sociales"
                                            },
                                        {
                                            "label": "Lettres, langues, arts",
                                            "value": "Lettres, langues, arts"
                                            },
                                        {
                                            "label": "Masters enseignement",
                                            "value": "Masters enseignement"
                                            }                                                            
                                    ],
                            value="Sciences, technologies et santé",
                        ),
                        html.H3(
                            "Choisissez une statistique :"
                        ),
                        dcc.RadioItems(
                            id="statistique_carte",
                            options=[
                                {
                                    "label": "Taux d'insertion",
                                    "value": "Taux d'insertion"
                                    },
                                {
                                    "label": "Part des femmes",
                                    "value": "Part des femmes"
                                    },
                                {
                                    "label": "Taux d'emplois cadres",
                                    "value": "Taux d'emplois cadres"
                                    },
                                {
                                    "label": "Taux d'emplois stables",
                                    "value": "Taux d'emplois stables"
                                    },
                                {
                                    "label": "Taux d'emplois temps plein",
                                    "value": "Taux d'emplois temps plein"
                                    },
                                {
                                    "label": "Salaire net mensuel médian des emplois à temps plein",
                                    "value": "Salaire net mensuel médian des emplois à temps plein"
                                    },                                                               
                            ],
                            value="Taux d'insertion",
                        ),
                        dcc.Graph(id = "carte")
                        # dcc.Graph(
                        #     id="carte"
                        #     """ figure={
                        #         "layout": {
                        #             "paper_bgcolor": "#192444",
                        #             "plot_bgcolor": "#192444",
                        #         } """
                            
                        #     #config={"scrollZoom": True, "displayModeBar": True},
                        # ),
                    ],
                ),
            ],
        ),          
    ]

@app.callback(
    dash.dependencies.Output('carte', 'figure'),
    [dash.dependencies.Input('annee_carte','value'),
    dash.dependencies.Input('diplome_carte','value'),
    dash.dependencies.Input('discipline_carte','value'),
    dash.dependencies.Input('statistique_carte','value')]
)
def get_carte(annee_value,diplome_value, discipline_value, statistique_value):
    if(diplome_value == "LP"):
        donnees_carte = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
        donnees_carte = donnees_carte.groupby(donnees_carte['Académie'], as_index = False)[["Taux d’insertion", "% femmes", "% emplois cadre", "% emplois stables", "% emplois à temps plein", "Salaire net médian des emplois à temps plein"]].median()
        donnees_carte = donnees_carte.rename(columns = {"Académie" : "Academie", 
                                                            "Taux d’insertion" : "Taux d'insertion",
                                                            "% femmes" : "Part des femmes", 
                                                            "% emplois cadre" : "Taux d'emplois cadres", 
                                                            "% emplois stables" : "Taux d'emplois stables", 
                                                            "% emplois à temps plein" : "Taux d'emplois temps plein", 
                                                            "Salaire net médian des emplois à temps plein" : "Salaire net mensuel médian des emplois à temps plein"})
    else:
        donnees_carte = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
        donnees_carte = donnees_carte.groupby(donnees_carte['academie'], as_index = False)[["taux_dinsertion", "femmes", "emplois_cadre", "emplois_stables", "emplois_a_temps_plein", "salaire_net_median_des_emplois_a_temps_plein"]].median()
        donnees_carte = donnees_carte.rename(columns = {"academie" : "Academie", 
                                                                "taux_dinsertion" : "Taux d'insertion",
                                                                "femmes" : "Part des femmes", 
                                                                "emplois_cadre" : "Taux d'emplois cadres", 
                                                                "emplois_stables" : "Taux d'emplois stables", 
                                                                "emplois_a_temps_plein" : "Taux d'emplois temps plein", 
                                                                "salaire_net_median_des_emplois_a_temps_plein" : "Salaire net mensuel médian des emplois à temps plein"})
    columns = ['Academie']
    columns.append(statistique_value)
    donnees_carte = pd.DataFrame(donnees_carte, columns = columns)

    import json
    with open("departements.geojson",'r') as load_f:
            departement = json.load(load_f)

    Academie = pd.DataFrame({'Academie' : ["Amiens","Reims","Normandie","Clermont-Ferrand","Orléans-Tours","Rennes","Besançon","Bordeaux","Lyon","Orléans-Tours",
                    "Bordeaux","Nancy-Metz","Normandie","Lille","Clermont-Ferrand","Strasbourg","Strasbourg","Normandie","Dijon","Créteil",
                    "Aix-Marseille","Aix-Marseille","Grenoble","Reims","Toulouse","Poitiers","Limoges","Bordeaux","Normandie","Orléans-Tours",
                    "Montpellier","Dijon","Amiens","Bordeaux","Lyon","Dijon","Paris","Versailles","Toulouse","Toulouse","Nice","Nantes",
                    "Limoges","Nancy-Metz","Versailles","Clermont-Ferrand","Nice","Montpellier","Corse","Rennes","Limoges","Besançon","Rennes",
                    "Montpellier","Bordeaux","Orléans-Tours","Grenoble","Reims","Reims","Nancy-Metz","Toulouse","Montpellier","Grenoble",
                    "Grenoble","Créteil","Aix-Marseille","Poitiers","Créteil","Lyon","Toulouse","Aix-Marseille","Poitiers","Orléans-Tours",
                    "Corse","Dijon","Grenoble","Toulouse","Toulouse","Montpellier","Clermont-Ferrand","Nantes","Toulouse","Nantes","Normandie",
                    "Rennes","Lille","Besançon","Nantes","Amiens","Versailles","Versailles","Orléans-Tours","Nantes","Nancy-Metz","Poitiers",
                    "Besançon"]})

    Academie = Academie.merge(donnees_carte, on='Academie')
    depts = []
    for i in range(len(Academie)) : 
        depts.append(departement["features"][i]["properties"]['nom'])

    Academie = pd.concat([pd.DataFrame({'Departement' : depts}),Academie], axis = 1)

    import plotly.graph_objects as go
    fig = go.Figure(go.Choroplethmapbox(geojson=departement, 
                                            featureidkey="properties.nom",
                                            locations=Academie["Departement"], z=Academie[statistique_value],
                                            zauto=True,
                                            colorscale='viridis',
                                            marker_opacity=0.8,
                                            marker_line_width=0.8,
                                            showscale=True))
    fig.update_layout(title_text="Statistique par département",
                        mapbox_style="carto-darkmatter",
                        mapbox_zoom=4, mapbox_center = {"lat": 48.856614, "lon": 2.3522219})
    return fig



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