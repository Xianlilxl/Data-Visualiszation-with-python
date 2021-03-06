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
                    # Premier onglet "Distribution des √©chantillons"
                    dcc.Tab(
                        id="Echtls-tab",
                        label="Distribution des √©chantillons",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # Deuxi√®me onglet "Statistiques par an"
                    dcc.Tab(
                        id="An-tab",
                        label="Statistiques par an",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # Troisi√®me onglet "Distribution des disciplines"
                    dcc.Tab(
                        id="Disciplines-tab",
                        label="Distribution des disciplines",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    # Quatri√®me onglet "Statistiques par d√©partement"
                    dcc.Tab(
                        id="Ville-tab",
                        label="Statistiques par d√©partement",
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

# Construction du premier onglet "Distribution des √©chantillons"
# Dans un premier temps nous vous montrons la distribution de l'ensemble de notre jeu de donn√©es en l'illustrant 
# un histogramme des nombres d'√©chantillons de chaque dipl√īme, 
# et un graphe camembert des pourcentages d'√©chantillons des disciplines dans chaque dipl√īme 
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
                                # les deux graphes sont aliment√©s en fonction de l'ann√©e par le Slider qui filtre les donn√©es
                                html.H3("Param√®tres"),
                                html.Div(
                                    id="header-container2",
                                    children=[
                                        build_graph_title("Ann√©e"),
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
                                    # Le graphe des nombres d'√©chantillons de chaque dipl√īme(DUT, Licence professionnel et Master)
                                    html.Div([
                                        dcc.Graph(id = "histo_diplome")
                                    ], style={'width': '50%','display': 'inline-block'}),
                                    # Le graphe des pourcentages d'√©chantillons de chaque discipline dans chaque dipl√īme(DUT, Licence professionnelle et Master)
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
# L'histogramme du nombre d'√©chantillons de chaque dipl√īme en fonction de l'ann√©e choisie 
@app.callback(
    dash.dependencies.Output('histo_diplome', 'figure'),
    [dash.dependencies.Input('annee_par_diplome','value')]
)
def get_histo_par_diplome(annee_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value]
    master = diplome_master[diplome_master["annee"]==annee_value]

    nbr_echantillons = pd.DataFrame({"Diplome" : ["DUT", "LP", "Master"], 
                                     "Nombre" : [dut["Nombre de r√©ponses"].sum(), lp["Nombre de r√©ponses"].sum(), master["nombre_de_reponses"].sum()]})

    return px.histogram(nbr_echantillons, x="Diplome", y="Nombre", title="Nombre d'√©chantillons de chaque dipl√īme de l'ann√©e choisie", labels={'Diplome':'Dipl√īmes', 'Nombre':"Nombre d'√©chantillons de chaque dipl√īme"})

# Le graphe en camembert repr√©sente les pourcentages de chaque discipline dans chaque dipl√īme 
@app.callback(
    dash.dependencies.Output('diplome', 'figure'),
    [dash.dependencies.Input('annee_par_diplome','value')]
)
def get_diplome(annee_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value]
    master = diplome_master[diplome_master["annee"]==annee_value]

    diplome = pd.concat([dut[['Dipl√īme', 'Domaine', "Nombre de r√©ponses"]].rename(columns={"Dipl√īme": "Diplome"}), 
                        lp[['Dipl√īme', 'Domaine', 'Nombre de r√©ponses']].rename(columns={"Dipl√īme": "Diplome"}), 
                        master[['diplome', 'domaine', "nombre_de_reponses"]].rename(columns={"diplome": "Diplome", "domaine" : 'Domaine',"nombre_de_reponses" : "Nombre de r√©ponses"})], 
                        axis = 0)
    diplome = diplome.groupby(by = ["Diplome", "Domaine"], as_index = False)["Nombre de r√©ponses"].sum()
    fig = px.sunburst(diplome, path=["Diplome", "Domaine"], values="Nombre de r√©ponses",color_continuous_scale='RdBu',
                    color='Nombre de r√©ponses', title="Pourcentage des disciplines de chaque dipl√īme de l'ann√©e choisie")
    return fig

# Deuxi√®me tabItems "Distribution des √©chantillons"
# Dans cette partie, nous pr√©sentons les √©volutions des statistiques critiques de chaque dipl√īme au cours des ann√©es (2010 √† 2016) 
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
                                        # Le RadioItems filtre les donn√©es alimentant les graphes en dessous en fonction des disciplines
                                        html.H3("Param√®tres"),
                                        build_graph_title("Choisissez une discipline :"),
                                        dcc.RadioItems(
                                            id="discipline_par_an",
                                            options=[
                                            {
                                                "label": "Sciences, technologies et sant√©",
                                                "value": "Sciences, technologies et sant√©"
                                                },
                                            {
                                                "label": "Droit, √©conomie et gestion",
                                                "value": "Droit, √©conomie et gestion"
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
                                                "label": "Ensemble des d√©partements d'IUT",
                                                "value": "Ensemble des d√©partements d'IUT"
                                                },                                                             
                                        ],
                                                value="Sciences, technologies et sant√©",
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
                                        # Les parts des femmes de chaque dipl√īme :
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
                                        # Le taux d'insertion (en %) de chaque dipl√īme
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
                                        # Les Statistiques des emplois (en %) de chaque dip√īme : 
                                        # le taux d'emplois cadres, le Taux d'emplois stables (en %) et le taux d'emplois √† temps plein (en %)
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
                                        # Les salaires nets mensuels m√©dians des emplois √† temps plein (en euros) de chaque dipl√īme 
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

# La tendance et la distribution des parts des femmes (en %) de chaque dipl√īme au cours des ann√©es en fonction de la discipline choisie 
@app.callback(
    dash.dependencies.Output('part_femmes_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_part_femmes_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    part_femmes_par_an = pd.concat([dut[["Ann√©e", 'Dipl√īme', "Part des femmes"]].rename(columns={"Ann√©e" : "Annee", "Dipl√īme": "Diplome"}), 
                                        lp[["Annee", 'Dipl√īme', '% femmes']].rename(columns={"Dipl√īme": "Diplome", "% femmes" : "Part des femmes"}), 
                                        master[["annee", 'diplome', 'femmes']].rename(columns={"annee" : "Annee", "diplome": "Diplome", "femmes" : "Part des femmes"})], 
                                       axis = 0)
    part_femmes_par_an = part_femmes_par_an.dropna(axis=0,how='all')
    
    return px.scatter(part_femmes_par_an, x="Annee", y="Part des femmes", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Part des femmes (en %) en " + discipline_value,
                     labels = {'Annee' : "Ann√©es", "Part des femmes" : "Part des femmes (en %)"})

# La tendance et la distribution du taux d'insertion (en %) de chaque dipl√īme au cours des ann√©es en fonction de la discipline choisie 
@app.callback(
    dash.dependencies.Output('taux_dinsertion_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_dinsertion_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_dinsertion_par_an = pd.concat([dut[["Ann√©e", 'Dipl√īme', "Taux d‚Äôinsertion"]].rename(columns={"Ann√©e" : "Annee", "Dipl√īme": "Diplome"}), 
                                        lp[["Annee", 'Dipl√īme', "Taux d‚Äôinsertion"]].rename(columns={"Dipl√īme": "Diplome"}), 
                                        master[["annee", 'diplome', "taux_dinsertion"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "taux_dinsertion" : "Taux d‚Äôinsertion"})], 
                                       axis = 0)
    taux_dinsertion_par_an = taux_dinsertion_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_dinsertion_par_an, x="Annee", y="Taux d‚Äôinsertion", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d‚Äôinsertion (en %) en " + discipline_value,  
                     labels = {'Annee' : "Ann√©es", "Taux d‚Äôinsertion" : "Taux d‚Äôinsertion (en %)"})

# La tendance et la distribution des Statistiques des emplois (en %) cadres de chaque dipl√īme au cours des ann√©es en fonction de la discipline choisie 
@app.callback(
    dash.dependencies.Output('taux_emplois_cadre_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_emplois_cadre_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_emplois_cadre_par_an = pd.concat([dut[["Ann√©e", 'Dipl√īme', "Part des emplois de niveau cadre"]].rename(columns={"Ann√©e" : "Annee", "Dipl√īme": "Diplome", "Part des emplois de niveau cadre" : "Emplois cadre"}), 
                                        lp[["Annee", 'Dipl√īme', "% emplois cadre"]].rename(columns={"Dipl√īme": "Diplome", "% emplois cadre": "Emplois cadre"}), 
                                        master[["annee", 'diplome', "emplois_cadre"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "emplois_cadre" : "Emplois cadre"})], 
                                       axis = 0)
    taux_emplois_cadre_par_an = taux_emplois_cadre_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_emplois_cadre_par_an, x="Annee", y="Emplois cadre", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d‚Äôemplois cadre (en %) en " + discipline_value,
                     labels = {'Annee' : "Ann√©es", "Emplois cadre" : "Taux d‚Äôemplois cadre (en %)"})

# La tendance et la distribution des Statistiques des emplois (en %) stables (en %) de chaque dipl√īme au cours des ann√©es en fonction de la discipline choisie 
@app.callback(
    dash.dependencies.Output('taux_emplois_stables_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_emplois_stables_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_emplois_stables_par_an = pd.concat([dut[["Ann√©e", 'Dipl√īme', "Part des emplois stables"]].rename(columns={"Ann√©e" : "Annee", "Dipl√īme": "Diplome", "Part des emplois stables" : "Emplois stables"}), 
                                        lp[["Annee", 'Dipl√īme', "% emplois stables"]].rename(columns={"Dipl√īme": "Diplome", "% emplois stables": "Emplois stables"}), 
                                        master[["annee", 'diplome', "emplois_stables"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "emplois_stables" : "Emplois stables"})], 
                                       axis = 0)
    taux_emplois_stables_par_an = taux_emplois_stables_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_emplois_stables_par_an, x="Annee", y="Emplois stables", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d'emplois stables (en %) en " + discipline_value,
                     labels = {'Annee' : "Ann√©es", "Emplois stables" : "Taux d'emplois stables (en %)"})

# La tendance et la distribution des Statistiques des emplois (en %) √† temps plein (en %) de chaque dipl√īme au cours des ann√©es en fonction de la discipline choisie 
@app.callback(
    dash.dependencies.Output('taux_emplois_temps_plein_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_taux_emplois_temps_plein_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    taux_emplois_temps_plein_par_an = pd.concat([dut[["Ann√©e", 'Dipl√īme', "Part des emplois √† temps plein"]].rename(columns={"Ann√©e" : "Annee", "Dipl√īme": "Diplome", "Part des emplois √† temps plein" : "Emplois √† temps plein"}), 
                                        lp[["Annee", 'Dipl√īme', "% emplois √† temps plein"]].rename(columns={"Dipl√īme": "Diplome", "% emplois √† temps plein": "Emplois √† temps plein"}), 
                                        master[["annee", 'diplome', "emplois_a_temps_plein"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "emplois_a_temps_plein" : "Emplois √† temps plein"})], 
                                       axis = 0)
    taux_emplois_temps_plein_par_an = taux_emplois_temps_plein_par_an.dropna(axis=0,how='all')
    
    return px.scatter(taux_emplois_temps_plein_par_an, x="Annee", y="Emplois √† temps plein", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Taux d'emplois √† temps plein (en %) en " + discipline_value,
                     labels = {'Annee' : "Ann√©es", "Emplois √† temps plein" : "Taux d'emplois √† temps plein (en %)"})

# La tendance et la distribution des salaires nets mensuels (en euros) de chaque dipl√īme au cours des ann√©es en fonction de la discipline choisie 
@app.callback(
    dash.dependencies.Output('salaire_par_an', 'figure'),
    [dash.dependencies.Input('discipline_par_an','value')]
)
def get_salaire_par_an(discipline_value):
    dut = diplome_dut[diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["domaine"]==discipline_value]
    salaire_par_an = pd.concat([dut[["Ann√©e", 'Dipl√īme', "Salaire net mensuel m√©dian des emplois √† temps plein"]].rename(columns={"Ann√©e" : "Annee", "Dipl√īme": "Diplome", "Salaire net mensuel m√©dian des emplois √† temps plein" : "Salaire"}), 
                                        lp[["Annee", 'Dipl√īme', "Salaire net m√©dian des emplois √† temps plein"]].rename(columns={"Dipl√īme": "Diplome", "Salaire net m√©dian des emplois √† temps plein": "Salaire"}), 
                                        master[["annee", 'diplome', "salaire_net_median_des_emplois_a_temps_plein"]].rename(columns={"annee" : "Annee", "diplome": "Diplome", "salaire_net_median_des_emplois_a_temps_plein" : "Salaire"})], 
                                       axis = 0)
    salaire_par_an = salaire_par_an.dropna(axis=0,how='all')
    
    return px.scatter(salaire_par_an, x="Annee", y="Salaire", color = "Diplome",
                     trendline="ols", marginal_y="box", 
                     title = "Salaires nets mensuels √† temps plein (en euros) en " + discipline_value,
                     labels = {'Annee' : "Ann√©es", "Salaire" : "Salaires nets mensuels √† temps plein (en euros)"})


# Construction du troisi√®me onglet "Distribution des disciplines"
# Dans cette partie, on vous montre les distributions des statistiques critiques dans chaque discipline et chaque ann√©e, ainsi  
# qu'une comparaison entre les diff√©rents dipl√īmes. Un histogramme et un violinplot par statistique illustrent ces distributions
def build_tab_3():
    return [
        html.Div(
            id="stats-an-graphs",
            children=[
                html.Div(
                    id="top-row",
                    children=[
                        html.H3("Param√®tres"),
                        # Le slider filtre les donn√©es alimentant les trois graphes se situant en dessous en fonction de l'ann√©e
                        html.Div(
                            id="header-container2",
                            children=[
                                build_graph_title("Ann√©e"),
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
                        # Le radioButtons filtre les donn√©es alimentant les graphes qui se trouvent en dessous en fonction des disciplines
                        html.Div(
                            id="header-container",
                            children=[
                                build_graph_title("Choisissez une discipline :"),
                                dcc.RadioItems(
                                    id="discipline_par_domaine",
                                    options=[
                                        {
                                            "label": "Sciences, technologies et sant√©",
                                            "value": "Sciences, technologies et sant√©"
                                            },
                                        {
                                            "label": "Droit, √©conomie et gestion",
                                            "value": "Droit, √©conomie et gestion"
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
                                            "label": "Ensemble des d√©partements d'IUT",
                                            "value": "Ensemble des d√©partements d'IUT"
                                            },                                                             
                                    ],
                                    value = "Sciences, technologies et sant√©",
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
                                # La distribution des parts des femmes de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
                                # ainsi qu'un boxplot sur tous les jeux de donn√©es de ces derniers
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
                                # La distribution du taux d'insertion (en %) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
                                # ainsi qu'un boxplot sur tous les jeux de donn√©es de ces derniers
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
                                # La distribution des Statistiques des emplois (en %) cadres, stables et √† temps plein (en %) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
                                # ainsi que des boxplots sur tous les jeux de donn√©es de ces derniers
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
                                # La distribution des salaires nets mensuels (en euros) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
                                # ainsi qu'un boxplot sur tous les jeux de donn√©es de ces derniers
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

# Le violinPlot du taux d'insertion (en %) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
@app.callback(
    dash.dependencies.Output('taux_dinsertion_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_dinsertion_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_insertion_par_domaine = pd.concat([dut[['Dipl√īme', "Taux d‚Äôinsertion"]].rename(columns={"Dipl√īme": "Diplome"}), 
                                        lp[['Dipl√īme', 'Taux d‚Äôinsertion']].rename(columns={"Dipl√īme": "Diplome"}), 
                                        master[['diplome', 'taux_dinsertion']].rename(columns={"diplome": "Diplome", "taux_dinsertion" : "Taux d‚Äôinsertion"})], 
                                       axis = 0)
    taux_insertion_par_domaine = taux_insertion_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_insertion_par_domaine, x="Diplome", y="Taux d‚Äôinsertion", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d‚Äôinsertion (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Dipl√īmes", "Taux d‚Äôinsertion" : "Taux d‚Äôinsertion (en %)"})

# Le violinPlot des parts des femmes de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
@app.callback(
    dash.dependencies.Output('part_femmes_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_part_femmes_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    part_femmes_par_domaine = pd.concat([dut[['Dipl√īme', "Part des femmes"]].rename(columns={"Dipl√īme": "Diplome"}), 
                                        lp[['Dipl√īme', "% femmes"]].rename(columns={"Dipl√īme": "Diplome", "% femmes" : "Part des femmes"}), 
                                        master[['diplome', 'femmes']].rename(columns={"diplome": "Diplome", "femmes" : "Part des femmes"})], 
                                       axis = 0)
    part_femmes_par_domaine = part_femmes_par_domaine.dropna(axis=0,how='all')
    return px.violin(part_femmes_par_domaine, x="Diplome", y="Part des femmes", 
    points="all", box = True, color = "Diplome", 
                     title = "Part des femmes (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Dipl√īmes", "Part des femmes" : "Part des femmes (en %)"})


# Le violinPlot du taux d'emplois cadres (en %) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
@app.callback(
    dash.dependencies.Output('taux_emplois_cadre_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_emplois_cadre_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    emplois_cadre_par_domaine = pd.concat([dut[['Dipl√īme', "Part des emplois de niveau cadre"]].rename(columns={"Dipl√īme": "Diplome", "Part des emplois de niveau cadre": "Emplois cadre"}), 
                                        lp[['Dipl√īme', "% emplois cadre"]].rename(columns={"Dipl√īme": "Diplome", "% emplois cadre" : "Emplois cadre"}), 
                                        master[['diplome', 'emplois_cadre']].rename(columns={"diplome": "Diplome", "emplois_cadre" : "Emplois cadre"})], 
                                       axis = 0)
    emplois_cadre_par_domaine = emplois_cadre_par_domaine.dropna(axis=0,how='all')
    return px.violin(emplois_cadre_par_domaine, x="Diplome", y="Emplois cadre", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d'emplois cadre (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Dipl√īmes", "Emplois cadre" : "Taux d'emplois cadre (en %)"})

# Le violinPlot du taux d'emplois stables (en %) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
@app.callback(
    dash.dependencies.Output('taux_emplois_stables_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_emplois_stables_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_emplois_stables_par_domaine = pd.concat([dut[['Dipl√īme', "Part des emplois stables"]].rename(columns={"Dipl√īme": "Diplome", "Part des emplois stables": "Emplois stables"}), 
                                        lp[['Dipl√īme', "% emplois stables"]].rename(columns={"Dipl√īme": "Diplome", "% emplois stables" : "Emplois stables"}), 
                                        master[['diplome', 'emplois_stables']].rename(columns={"diplome": "Diplome", "emplois_stables" : "Emplois stables"})], 
                                       axis = 0)
    taux_emplois_stables_par_domaine = taux_emplois_stables_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_emplois_stables_par_domaine, x="Diplome", y="Emplois stables", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d'emplois stables (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Dipl√īmes", "Emplois stables" : "Taux d'emplois stables (en %)"})

# Le violinPlot du taux d'emplois √† temps plein (en %) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
@app.callback(
    dash.dependencies.Output('taux_emplois_temps_plein_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_taux_emplois_temps_plein_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_emplois_temps_plein_par_domaine = pd.concat([dut[['Dipl√īme', "Part des emplois √† temps plein"]].rename(columns={"Dipl√īme": "Diplome", "Part des emplois √† temps plein": "Emplois √† temps plein"}), 
                                        lp[['Dipl√īme', "% emplois √† temps plein"]].rename(columns={"Dipl√īme": "Diplome", "% emplois √† temps plein" : "Emplois √† temps plein"}), 
                                        master[['diplome', 'emplois_a_temps_plein']].rename(columns={"diplome": "Diplome", "emplois_a_temps_plein" : "Emplois √† temps plein"})], 
                                       axis = 0)
    taux_emplois_temps_plein_par_domaine = taux_emplois_temps_plein_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_emplois_temps_plein_par_domaine, x="Diplome", y="Emplois √† temps plein", 
                     points="all", box = True, color = "Diplome", 
                     title = "Taux d'emplois √† temps plein (en %) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Dipl√īmes", "Emplois √† temps plein" : "Taux d'emplois √† temps plein (en %)"})

# Le violinPlot des salaires nets mensuels (en euros) de chaque dipl√īme en fonction de l'ann√©e et de la discipline choisies
@app.callback(
    dash.dependencies.Output('salaire_par_domaine', 'figure'),
    [dash.dependencies.Input('annee_par_domaine','value'),
    dash.dependencies.Input('discipline_par_domaine','value')]
)
def get_salaire_par_domaine(annee_value, discipline_value):
    dut = diplome_dut[diplome_dut["Ann√©e"]==annee_value][diplome_dut["Domaine"]==discipline_value]
    lp = diplome_lp[diplome_lp["Annee"]==annee_value][diplome_lp["Domaine"]==discipline_value]
    master = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
    taux_emplois_temps_plein_par_domaine = pd.concat([dut[['Dipl√īme', "Salaire net mensuel m√©dian des emplois √† temps plein"]].rename(columns={"Dipl√īme": "Diplome", "Salaire net mensuel m√©dian des emplois √† temps plein": "Salaire"}), 
                                        lp[['Dipl√īme', "Salaire net m√©dian des emplois √† temps plein"]].rename(columns={"Dipl√īme": "Diplome", "Salaire net m√©dian des emplois √† temps plein" : "Salaire"}), 
                                        master[['diplome', 'salaire_net_median_des_emplois_a_temps_plein']].rename(columns={"diplome": "Diplome", "salaire_net_median_des_emplois_a_temps_plein" : "Salaire"})], 
                                       axis = 0)
    taux_emplois_temps_plein_par_domaine = taux_emplois_temps_plein_par_domaine.dropna(axis=0,how='all')
    return px.violin(taux_emplois_temps_plein_par_domaine, x="Diplome", y="Salaire", 
                     points="all", box = True, color = "Diplome", 
                     title = "Salaires nets mensuels (en euros) en " + discipline_value + " en " + str(annee_value),
                     labels = {'Diplome' : "Dipl√īmes", "Salaire" : "Salaires nets mensuels (en euros)"})

# Construction du quatri√®me onglet "Statistiques par d√©partement"
# Dans cette partie, nous illustrons la distribution des statistiques critiques de chaque d√©partement sous forme d'une cartographie 
# en fonction de l'ann√©e, du dipl√īme, de la discipline et de la statistique choisis
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
                        # Le slider filtre les donn√©es alimentant les trois graphes se situant en dessous en fonction de l'ann√©e
                        html.H3("Ann√©e"),
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
                        # A cause du manque de donn√©es g√©ographiques dans le jeu de donn√©es de DUT, 
                        # nous pr√©sentons ici uniquement la cartographie des donn√©es de licence professionnelle et de master
                        html.H3(
                            "Choisissez un dipl√īme :"
                        ),
                        dcc.RadioItems(
                            id="diplome_carte",
                            options=[
                                {"label": "LP", "value": "LP"},
                                {"label": "Master", "value": "Master"},                                
                            ],
                            value="LP",
                        ),
                        # Le radioItems filtre les donn√©es alimentant les graphes qui se trouvent en dessous en fonction des disciplines
                        html.H3(
                            "Choisissez une discipline :"
                        ),
                        dcc.RadioItems(
                            id="discipline_carte",
                            options=[
                                        {
                                            "label": "Sciences, technologies et sant√©",
                                            "value": "Sciences, technologies et sant√©"
                                            },
                                        {
                                            "label": "Droit, √©conomie et gestion",
                                            "value": "Droit, √©conomie et gestion"
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
                            value="Sciences, technologies et sant√©",
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
                                    "label": "Salaire net mensuel m√©dian des emplois √† temps plein (en euros)",
                                    "value": "Salaire net mensuel m√©dian des emplois √† temps plein"
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

# La cartographie repr√©sente les statistiques par d√©partement en fonction de l'ann√©e, du dipl√īme, de la discipline et de la statistique choisis
# ici on prend en compte les m√©dianes des statistiques de chaque d√©partement 
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
        donnees_carte = donnees_carte.groupby(donnees_carte['Acad√©mie'], as_index = False)[["Taux d‚Äôinsertion", "% femmes", "% emplois cadre", "% emplois stables", "% emplois √† temps plein", "Salaire net m√©dian des emplois √† temps plein"]].median()
        donnees_carte = donnees_carte.rename(columns = {"Acad√©mie" : "Academie", 
                                                            "Taux d‚Äôinsertion" : "Taux d'insertion",
                                                            "% femmes" : "Part des femmes", 
                                                            "% emplois cadre" : "Taux d'emplois cadres", 
                                                            "% emplois stables" : "Taux d'emplois stables", 
                                                            "% emplois √† temps plein" : "Taux d'emplois temps plein", 
                                                            "Salaire net m√©dian des emplois √† temps plein" : "Salaire net mensuel m√©dian des emplois √† temps plein"})
    else:
        donnees_carte = diplome_master[diplome_master["annee"]==annee_value][diplome_master["domaine"]==discipline_value]
        donnees_carte = donnees_carte.groupby(donnees_carte['academie'], as_index = False)[["taux_dinsertion", "femmes", "emplois_cadre", "emplois_stables", "emplois_a_temps_plein", "salaire_net_median_des_emplois_a_temps_plein"]].median()
        donnees_carte = donnees_carte.rename(columns = {"academie" : "Academie", 
                                                                "taux_dinsertion" : "Taux d'insertion",
                                                                "femmes" : "Part des femmes", 
                                                                "emplois_cadre" : "Taux d'emplois cadres", 
                                                                "emplois_stables" : "Taux d'emplois stables", 
                                                                "emplois_a_temps_plein" : "Taux d'emplois temps plein", 
                                                                "salaire_net_median_des_emplois_a_temps_plein" : "Salaire net mensuel m√©dian des emplois √† temps plein"})

    columns = ['Academie']
    columns.append(statistique_value)
    donnees_carte = pd.DataFrame(donnees_carte, columns = columns)

    with open("departements.geojson",'r') as load_f:
            departement = json.load(load_f)

    Academie = pd.DataFrame({'Academie' : ["Amiens","Reims","Normandie","Clermont-Ferrand","Orl√©ans-Tours","Rennes","Besan√ßon","Bordeaux","Lyon","Orl√©ans-Tours",
                    "Bordeaux","Nancy-Metz","Normandie","Lille","Clermont-Ferrand","Strasbourg","Strasbourg","Normandie","Dijon","Cr√©teil",
                    "Aix-Marseille","Aix-Marseille","Grenoble","Reims","Toulouse","Poitiers","Limoges","Bordeaux","Normandie","Orl√©ans-Tours",
                    "Montpellier","Dijon","Amiens","Bordeaux","Lyon","Dijon","Paris","Versailles","Toulouse","Toulouse","Nice","Nantes",
                    "Limoges","Nancy-Metz","Versailles","Clermont-Ferrand","Nice","Montpellier","Corse","Rennes","Limoges","Besan√ßon","Rennes",
                    "Montpellier","Bordeaux","Orl√©ans-Tours","Grenoble","Reims","Reims","Nancy-Metz","Toulouse","Montpellier","Grenoble",
                    "Grenoble","Cr√©teil","Aix-Marseille","Poitiers","Cr√©teil","Lyon","Toulouse","Aix-Marseille","Poitiers","Orl√©ans-Tours",
                    "Corse","Dijon","Grenoble","Toulouse","Toulouse","Montpellier","Clermont-Ferrand","Nantes","Toulouse","Nantes","Normandie",
                    "Rennes","Lille","Besan√ßon","Nantes","Amiens","Versailles","Versailles","Orl√©ans-Tours","Nantes","Nancy-Metz","Poitiers",
                    "Besan√ßon"]})

    Academie = Academie.merge(donnees_carte, on='Academie')
    depts = []
    for i in range(len(Academie)) : 
        depts.append(departement["features"][i]["properties"]['nom'])

    Academie = pd.concat([pd.DataFrame({'Departement' : depts}),Academie], axis = 1)

    
    if statistique_value == "Salaire net mensuel m√©dian des emplois √† temps plein":
        etiquette = '<b>D√©partement</b>: <b>%{hovertext}</b>'+ '<br><b>'+ statistique_value +'</b>: %{z} ‚ā¨<br><extra></extra>'
        colorbar_label = 'Salaire net mensuel m√©dian <br>des emplois √† temps plein (en euros)'
        titre_carte = 'Salaire net mensuel m√©dian des emplois √† temps plein (en euros) par d√©partement en ' + discipline_value +" en " +str(annee_value)
    else : 
        etiquette = '<b>D√©partement</b>: <b>%{hovertext}</b>'+ '<br><b>'+ statistique_value +'</b>: %{z} %<br><extra></extra>'
        colorbar_label = statistique_value + " (en %)"
        titre_carte = statistique_value + ' (en %) par d√©partement en ' + discipline_value +" en " +str(annee_value)

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