# -*- coding: utf-8 -*-

# Run this app with `python main.py` and
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

# pydata stack
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go

# Initialisation de l'application
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
server = app.server
app.config["suppress_callback_exceptions"] = True

# Lecture des fichiers de source
diplome_dut = pd.read_csv("fr-esr-insertion_professionnelle-dut_donnees_nationales.csv", sep=';',na_values=["ns", "nd"])
diplome_lp = pd.read_csv("fr-esr-insertion_professionnelle-lp.csv", sep=';', na_values=["ns", "nd"])
diplome_master = pd.read_csv("fr-esr-insertion_professionnelle-master.csv", sep=';', na_values=["ns", "nd"])

# Construction du titre de page
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H1("Insertion professionnelle")
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                ],
            ),
        ],
    )

# Construction des onglets principaux
def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab1",
                className="custom-tabs",
                children=[
                    # Premier onglet "Distribution des échantillons"
                    dcc.Tab(
                        id="Echtls-tab",
                        label="Distribution des échantillons",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # Deuxième onglet "Statistiques par an"
                    dcc.Tab(
                        id="An-tab",
                        label="Statistiques par an",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # Troisième onglet "Distribution des disciplines"
                    dcc.Tab(
                        id="Disciplines-tab",
                        label="Distribution des disciplines",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # Quatrième onglet "Statistiques par département"
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

# Construction des titres html
def build_graph_title(title):
    return html.P(className="graph-title", children=title)

# Construction du premier onglet "Distribution des échantillons"
# Dans un premier temps nous vous montrons la distribution de l'ensemble de notre jeu de données en l'illustrant 
# un histogramme des nombres d'échantillons de chaque diplôme, 
# et un graphe camembert des pourcentages d'échantillons des disciplines dans chaque diplôme 
def build_tab_1():
    return [
        html.Div(
            id="top-row-graphs",
            children=[
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            id="map-container",
                            children=[
                                # les deux graphes sont alimentés en fonction de l'année par le Slider qui filtre les données
                                html.H3("Paramètres"),
                                html.Div(
                                    id="header-container2",
                                    children=[
                                        build_graph_title("Année"),
                                        dcc.Slider(
                                            id = "annee_par_diplome",
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
                                html.Div([
                                    # Le graphe des nombres d'échantillons de chaque diplôme(DUT, Licence professionnel et Master)
                                    html.Div([
                                        dcc.Graph(id = "histo_diplome")
                                    ], style={'width': '50%','display': 'inline-block'}),
                                    # Le graphe des pourcentages d'échantillons de chaque discipline dans chaque diplôme(DUT, Licence professionnelle et Master)
                                    html.Div([
                                        dcc.Graph(id = "diplome")
                                    ], style={'width': '45%','display': 'inline-block'})
                                ], style={'width': '100%', 'display': 'inline-block'})
                            ],
                        ),
                    ],
                )
            ]
        )
    ]
# L'histogramme du nombre d'échantillons de chaque diplôme en fonction de l'année choisie 
@app.callback(
    dash.dependencies.Output('histo_diplome', 'figure'),
    [dash.dependencies.Input('annee_par_diplome','value')]
)
def get_histo_par_diplome(annee_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value]
    master = diplome_master[diplome_master["annee"]==annee_value]

    nbr_echantillons = pd.DataFrame({"Diplome" : ["DUT", "LP", "Master"], 
                                     "Nombre" : [dut["Nombre de réponses"].sum(), lp["Nombre de réponses"].sum(), master["nombre_de_reponses"].sum()]})

    return px.histogram(nbr_echantillons, x="Diplome", y="Nombre", title="Nombre d'échantillons de chaque diplôme de l'année choisie", labels={'Diplome':'Diplômes', 'Nombre':"Nombre d'échantillons de chaque diplôme"})

# Le graphe en camembert représente les pourcentages de chaque discipline dans chaque diplôme 
@app.callback(
    dash.dependencies.Output('diplome', 'figure'),
    [dash.dependencies.Input('annee_par_diplome','value')]
)
def get_diplome(annee_value):
    dut = diplome_dut[diplome_dut["Année"]==annee_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value]
    master = diplome_master[diplome_master["annee"]==annee_value]

    diplome = pd.concat([dut[['Diplôme', 'Domaine', "Nombre de réponses"]].rename(columns={"Diplôme": "Diplome"}), 
                        lp[['Diplôme', 'Domaine', 'Nombre de réponses']].rename(columns={"Diplôme": "Diplome"}), 
                        master[['diplome', 'domaine', "nombre_de_reponses"]].rename(columns={"diplome": "Diplome", "domaine" : 'Domaine',"nombre_de_reponses" : "Nombre de réponses"})], 
                        axis = 0)
    diplome = diplome.groupby(by = ["Diplome", "Domaine"], as_index = False)["Nombre de réponses"].sum()
    fig = px.sunburst(diplome, path=["Diplome", "Domaine"], values="Nombre de réponses",color_continuous_scale='RdBu',
                    color='Nombre de réponses', title="Pourcentage des disciplines de chaque diplôme de l'année choisie")
    return fig

# Deuxième tabItems "Distribution des échantillons"
# Dans cette partie, nous présentons les évolutions des statistiques critiques de chaque diplôme au cours des années (2010 à 2016) 
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
                                        # Le RadioItems filtre les données alimentant les graphes en dessous en fonction des disciplines
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
                                            html.Br()
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
                                    value="tab21",
                                    className="custom-tabs",
                                    children=[
                                        # Les parts des femmes de chaque diplôme :
                                        dcc.Tab(
                                            id="Femme-an-tab",
                                            label="Part des femmes (en %)",
                                            children=[
                                                html.Div(
                                                    id="Femme-an-container",
                                                    children=[
                                                        dcc.Graph(id = "part_femmes_par_an")
                                                        ]
                                                    )
                                            ],
                                            value="tab21",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        # Le taux d'insertion (en %) de chaque diplôme
                                        dcc.Tab(
                                            id="Insertion-an-tab",
                                            label="Taux d'insertion (en %)",
                                            children=[
                                                html.Div(
                                                    id="Insertion-an-container",
                                                    children=[
                                                        dcc.Graph(id = "taux_dinsertion_par_an")]
                                                    )
                                            ],
                                            value="tab22",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        # Les Statistiques des emplois (en %) de chaque dipôme : 
                                        # le taux d'emplois cadres, le Taux d'emplois stables (en %) et le taux d'emplois à temps plein (en %)
                                        dcc.Tab(
                                            id="Emploi-an-tab",
                                            label="Statistiques des emplois (en %)",
                                            children=[
                                                html.Div(
                                                    id="Emploi-an-container",
                                                    children=[
                                                        dcc.Graph(id = "taux_emplois_cadre_par_an"),
                                                        dcc.Graph(id = "taux_emplois_stables_par_an"),
                                                        dcc.Graph(id = "taux_emplois_temps_plein_par_an")
                                                        ]
                                                    )
                                            ],
                                            value="tab23",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        # Les salaires nets mensuels médians des emplois à temps plein (en euros) de chaque diplôme 
                                        dcc.Tab(
                                            id="Salaires-an-tab",
                                            label="Salaires nets mensuels (en euros)",
                                            children=[
                                                html.Div(
                                                    id="Salaires-an-container",
                                                    children=[
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

# La tendance et la distribution des parts des femmes (en %) de chaque diplôme au cours des années en fonction de la discipline choisie 
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
    
    return px.scatter(part_femmes_par_an, x="Annee", y="Part des femmes", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Part des femmes (en %) en " + discipline_value,
                     labels = {'Annee' : "Années", "Part des femmes" : "Part des femmes (en %)"})

# La tendance et la distribution du taux d'insertion (en %) de chaque diplôme au cours des années en fonction de la discipline choisie 
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
    
    return px.scatter(taux_dinsertion_par_an, x="Annee", y="Taux d’insertion", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d’insertion (en %) en " + discipline_value,  
                     labels = {'Annee' : "Années", "Taux d’insertion" : "Taux d’insertion (en %)"})

# La tendance et la distribution des Statistiques des emplois (en %) cadres de chaque diplôme au cours des années en fonction de la discipline choisie 
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
    
    return px.scatter(taux_emplois_cadre_par_an, x="Annee", y="Emplois cadre", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d’emplois cadre (en %) en " + discipline_value,
                     labels = {'Annee' : "Années", "Emplois cadre" : "Taux d’emplois cadre (en %)"})

# La tendance et la distribution des Statistiques des emplois (en %) stables (en %) de chaque diplôme au cours des années en fonction de la discipline choisie 
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
    
    return px.scatter(taux_emplois_stables_par_an, x="Annee", y="Emplois stables", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d'emplois stables (en %) en " + discipline_value,
                     labels = {'Annee' : "Années", "Emplois stables" : "Taux d'emplois stables (en %)"})

# La tendance et la distribution des Statistiques des emplois (en %) à temps plein (en %) de chaque diplôme au cours des années en fonction de la discipline choisie 
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
    
    return px.scatter(taux_emplois_temps_plein_par_an, x="Annee", y="Emplois à temps plein", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d'emplois à temps plein (en %) en " + discipline_value,
                     labels = {'Annee' : "Années", "Emplois à temps plein" : "Taux d'emplois à temps plein (en %)"})

# La tendance et la distribution des salaires nets mensuels (en euros) de chaque diplôme au cours des années en fonction de la discipline choisie 
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
    
    return px.scatter(salaire_par_an, x="Annee", y="Salaire", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Salaires nets mensuels à temps plein (en euros) en " + discipline_value,
                     labels = {'Annee' : "Années", "Salaire" : "Salaires nets mensuels à temps plein (en euros)"})


# Construction du troisième onglet "Distribution des disciplines"
# Dans cette partie, on vous montre les distributions des statistiques critiques dans chaque discipline et chaque année, ainsi  
# qu'une comparaison entre les différents diplômes. Un histogramme et un violinplot par statistique illustrent ces distributions
def build_tab_3():
    return [
        html.Div(
            id="stats-an-graphs",
            children=[
                html.Div(
                    id="top-row",
                    children=[
                        html.H3("Paramètres"),
                        # Le slider filtre les données alimentant les trois graphes se situant en dessous en fonction de l'année
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
                        # Le radioButtons filtre les données alimentant les graphes qui se trouvent en dessous en fonction des disciplines
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
                                html.Br()
                            ],
                        )
                        
                    ],
                ),
                html.Div(
                    id="tabs",
                    className="tabs",
                    children=[
                        dcc.Tabs(
                            id="stats-discipline-tabs",
                            value="tab31",
                            className="custom-tabs",
                            children=[
                                # La distribution des parts des femmes de chaque diplôme en fonction de l'année et de la discipline choisies
                                # ainsi qu'un boxplot sur tous les jeux de données de ces derniers
                                dcc.Tab(
                                    id="Femme-discipline-tab",
                                    label="Part des femmes (en %)",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Femme-discipline-container",
                                            children=[
                                                dcc.Graph(id = "part_femmes_par_domaine")
                                                ],
                                            ),
                                        ],
                                    value="tab31",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                # La distribution du taux d'insertion (en %) de chaque diplôme en fonction de l'année et de la discipline choisies
                                # ainsi qu'un boxplot sur tous les jeux de données de ces derniers
                                dcc.Tab(
                                    id="Insertion-discipline-tab",
                                    label="Taux d'insertion (en %)",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Insertion-discipline-container",
                                            children=[
                                                dcc.Graph(id = "taux_dinsertion_par_domaine"),
                                                ],
                                            ),
                                        ],
                                    value="tab32",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                # La distribution des Statistiques des emplois (en %) cadres, stables et à temps plein (en %) de chaque diplôme en fonction de l'année et de la discipline choisies
                                # ainsi que des boxplots sur tous les jeux de données de ces derniers
                                dcc.Tab(
                                    id="Emploi-discipline-tab",
                                    label="Statistiques des emplois (en %)",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Emploi-discipline-container",
                                            children=[
                                                dcc.Graph(id = "taux_emplois_cadre_par_domaine"), 
                                                dcc.Graph(id = "taux_emplois_stables_par_domaine"),
                                                dcc.Graph(id = "taux_emplois_temps_plein_par_domaine")
                                                ],
                                            ),
                                        ],
                                    value="tab33",
                                    className="custom-tab",
                                    selected_className="custom-tab--selected",
                                ),
                                # La distribution des salaires nets mensuels (en euros) de chaque diplôme en fonction de l'année et de la discipline choisies
                                # ainsi qu'un boxplot sur tous les jeux de données de ces derniers
                                dcc.Tab(
                                    id="Salaires-discipline-tab",
                                    label="Salaires nets mensuels (en euros)",
                                    children=[
                                        html.Div(
                                            className="row",
                                            id="Salaires-discipline-container",
                                            children=[
                                                dcc.Graph(id = "salaire_par_domaine")
                                                ],
                                            ),
                                        ],
                                    value="tab34",
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

# Le violinPlot du taux d'insertion (en %) de chaque diplôme en fonction de l'année et de la discipline choisies
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
    return px.violin(taux_insertion_par_domaine, x="Diplome", y="Taux d’insertion", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d’insertion (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Diplômes", "Taux d’insertion" : "Taux d’insertion (en %)"})

# Le violinPlot des parts des femmes de chaque diplôme en fonction de l'année et de la discipline choisies
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
    return px.violin(part_femmes_par_domaine, x="Diplome", y="Part des femmes", 
    points="all", box = True, color = "Diplome", 
                     title = "Part des femmes (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Diplômes", "Part des femmes" : "Part des femmes (en %)"})


# Le violinPlot du taux d'emplois cadres (en %) de chaque diplôme en fonction de l'année et de la discipline choisies
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
    return px.violin(emplois_cadre_par_domaine, x="Diplome", y="Emplois cadre", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d'emplois cadre (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Diplômes", "Emplois cadre" : "Taux d'emplois cadre (en %)"})

# Le violinPlot du taux d'emplois stables (en %) de chaque diplôme en fonction de l'année et de la discipline choisies
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
    return px.violin(taux_emplois_stables_par_domaine, x="Diplome", y="Emplois stables", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d'emplois stables (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Diplômes", "Emplois stables" : "Taux d'emplois stables (en %)"})

# Le violinPlot du taux d'emplois à temps plein (en %) de chaque diplôme en fonction de l'année et de la discipline choisies
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
    return px.violin(taux_emplois_temps_plein_par_domaine, x="Diplome", y="Emplois à temps plein", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d'emplois à temps plein (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Diplômes", "Emplois à temps plein" : "Taux d'emplois à temps plein (en %)"})

# Le violinPlot des salaires nets mensuels (en euros) de chaque diplôme en fonction de l'année et de la discipline choisies
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
    return px.violin(taux_emplois_temps_plein_par_domaine, x="Diplome", y="Salaire", 
                     points="all", box = True, color = "Diplome", 
                     title = "Salaires nets mensuels (en euros) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Diplômes", "Salaire" : "Salaires nets mensuels (en euros)"})

# Construction du quatrième onglet "Statistiques par département"
# Dans cette partie, nous illustrons la distribution des statistiques critiques de chaque département sous forme d'une cartographie 
# en fonction de l'année, du diplôme, de la discipline et de la statistique choisis
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
                        # Le slider filtre les données alimentant les trois graphes se situant en dessous en fonction de l'année
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
                        # A cause du manque de données géographiques dans le jeu de données de DUT, 
                        # nous présentons ici uniquement la cartographie des données de licence professionnelle et de master
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
                        # Le radioItems filtre les données alimentant les graphes qui se trouvent en dessous en fonction des disciplines
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
                                    "label": "Taux d'insertion (en %)",
                                    "value": "Taux d'insertion"
                                    },
                                {
                                    "label": "Part des femmes (en %)",
                                    "value": "Part des femmes"
                                    },
                                {
                                    "label": "Taux d'emplois cadres (en %)",
                                    "value": "Taux d'emplois cadres"
                                    },
                                {
                                    "label": "Taux d'emplois stables (en %)",
                                    "value": "Taux d'emplois stables"
                                    },
                                {
                                    "label": "Taux d'emplois temps plein (en %)",
                                    "value": "Taux d'emplois temps plein"
                                    },
                                {
                                    "label": "Salaire net mensuel médian des emplois à temps plein (en euros)",
                                    "value": "Salaire net mensuel médian des emplois à temps plein"
                                    },                                                               
                            ],
                            value="Taux d'insertion",
                        ),
                        html.Br(),
                        dcc.Graph(id = "carte")
                    ],
                ),
            ],
        ),          
    ]

# La cartographie représente les statistiques par département en fonction de l'année, du diplôme, de la discipline et de la statistique choisis
# ici on prend en compte les médianes des statistiques de chaque département 
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

    
    if statistique_value == "Salaire net mensuel médian des emplois à temps plein":
        etiquette = '<b>Département</b>: <b>%{hovertext}</b>'+ '<br><b>'+ statistique_value +'</b>: %{z} €<br><extra></extra>'
        colorbar_label = 'Salaire net mensuel médian <br>des emplois à temps plein (en euros)'
        titre_carte = 'Salaire net mensuel médian des emplois à temps plein (en euros) par département en ' + discipline_value +" en " +str(annee_value)
    else : 
        etiquette = '<b>Département</b>: <b>%{hovertext}</b>'+ '<br><b>'+ statistique_value +'</b>: %{z} %<br><extra></extra>'
        colorbar_label = statistique_value + " (en %)"
        titre_carte = statistique_value + ' (en %) par département en ' + discipline_value +" en " +str(annee_value)

    fig = go.Figure(go.Choroplethmapbox(geojson=departement, 
                                            featureidkey="properties.nom",
                                            locations=Academie["Departement"], 
                                            z=Academie[statistique_value],
                                            text = Academie["Departement"], 
                                            hovertext = Academie["Departement"], 
                                            hovertemplate = etiquette,
                                            colorbar_title = colorbar_label,
                                            zauto=True,
                                            colorscale='viridis',
                                            marker_opacity=0.8,
                                            marker_line_width=0.8,
                                            showscale=True))
    fig.update_layout(title={'text':titre_carte,'xref':'paper','x':0.5},
                        margin={'l':10,'r':0,'t':50,'b':10},
                        mapbox_style="carto-darkmatter",
                        mapbox_zoom=4, 
                        mapbox_center = {"lat": 46.7167, "lon": 2.5167})
    


    return fig


# Construction du dashboard
app.layout = html.Div(
    id="big-app-container",
    #style = {'backgroundColor' : 'blue'},
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        )
        ],
    )

# Construction des onglets principaux
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

# Running the server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        port=8050
    )