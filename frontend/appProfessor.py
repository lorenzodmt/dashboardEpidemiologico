import json
import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output

# Carregar dados tratados
with open("../backend/data.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)
# Inicializar app com tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Dashboard Epidemiológico - Dengue"
# Gráficos iniciais
fig_casos = px.line(
    df,
    x="data_iniSE",
    y="casos",
    title="Casos Semanais de Dengue",
    markers=True,
    template="plotly_white",
)
fig_rt = px.line(
    df,
    x="data_iniSE",
    y="Rt",
    title="Taxa de Reprodução (Rt)",
    markers=True,
    template="plotly_white",
)
fig_media = px.line(
    df,
    x="data_iniSE",
    y="media_movel",
    title="Média Móvel de Casos (4 semanas)",
    markers=True,
    template="plotly_white",
)
# Layout com cards e dropdown
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Dashboard Epidemiológico - Dengue",
                        className="text-center mb-4",
                    ),
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Seleção de Ano"),
                            dbc.CardBody(
                                [
                                    dcc.Dropdown(
                                        options=[
                                            {"label": "2022", "value": "2022"},
                                            {"label": "2023", "value": "2023"},
                                        ],
                                        value="2022",
                                        id="ano-dropdown",
                                    )
                                ]
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Casos Semanais"),
                            dbc.CardBody(dcc.Graph(id="fig-casos", figure=fig_casos)),
                        ]
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Taxa de Reprodução (Rt)"),
                            dbc.CardBody(dcc.Graph(id="fig-rt", figure=fig_rt)),
                        ]
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Média Móvel"),
                            dbc.CardBody(dcc.Graph(id="fig-media", figure=fig_media)),
                        ]
                    ),
                    width=4,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Indicadores"),
                            dbc.CardBody(
                                [
                                    html.H4(
                                        f"Total de Casos: {df['casos'].sum()}",
                                        className="cardtitle",
                                    ),
                                    html.H4(
                                        f"Média de Rt: {df['Rt'].mean():.2f}",
                                        className="cardtitle",
                                    ),
                                ]
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            className="mt-4",
        ),
    ],
    fluid=True,
)
# Callback para atualizar gráficos conforme ano selecionado
@app.callback(
    [
        Output("fig-casos", "figure"),
        Output("fig-rt", "figure"),
        Output("fig-media", "figure"),
    ],
    [Input("ano-dropdown", "value")],
)
def update_graphs(ano):
    df_filtrado = df[df["data_iniSE"].str.contains(ano)]
    fig_casos = px.line(
        df_filtrado,
        x="data_iniSE",
        y="casos",
        title=f"Casos Semanais ({ano})",
        markers=True,
        template="plotly_white",
    )
    fig_rt = px.line(
        df_filtrado,
        x="data_iniSE",
        y="Rt",
        title=f"Taxa de Reprodução (Rt) ({ano})",
        markers=True,
        template="plotly_white",
    )
    fig_media = px.line(
        df_filtrado,
        x="data_iniSE",
        y="media_movel",
        title=f"Média Móvel de Casos ({ano})",
        markers=True,
        template="plotly_white",
    )
    return fig_casos, fig_rt, fig_media


if __name__ == "__main__":
    app.run(debug=True)
