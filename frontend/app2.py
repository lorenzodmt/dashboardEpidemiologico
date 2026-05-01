import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Carregar dados tratados
with open("../backend/data.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Garantir que a coluna de data está no formato datetime
df["data_iniSE"] = pd.to_datetime(df["data_iniSE"])

# Inicializar app Dash
app = dash.Dash(__name__)
app.title = "Dashboard Epidemiológico - Dengue"

# Valores mínimo e máximo das datas disponíveis
data_min = df["data_iniSE"].min().date()
data_max = df["data_iniSE"].max().date()

# Layout responsivo
app.layout = html.Div(
    style={"backgroundColor": "#111", "color": "white", "fontFamily": "Arial, sans-serif", "padding": "20px"},
    children=[
        # Título
        html.H1(
            "📊 Dashboard Epidemiológico - Dengue",
            style={"textAlign": "center", "marginBottom": "30px"},
        ),

        # Painel de filtros
        html.Div(
            style={
                "backgroundColor": "#1e1e1e",
                "borderRadius": "10px",
                "padding": "20px",
                "marginBottom": "30px",
                "display": "flex",
                "alignItems": "center",
                "gap": "20px",
                "flexWrap": "wrap",
            },
            children=[
                html.Label(
                    "📅 Filtrar por intervalo de datas:",
                    style={"fontWeight": "bold", "fontSize": "16px", "color": "#ccc"},
                ),
                dcc.DatePickerRange(
                    id="filtro-datas",
                    min_date_allowed=data_min,
                    max_date_allowed=data_max,
                    start_date=data_min,
                    end_date=data_max,
                    display_format="DD/MM/YYYY",
                    style={"color": "#000"},
                ),
                html.Button(
                    "🔄 Resetar",
                    id="btn-resetar",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#e74c3c",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "6px",
                        "padding": "8px 16px",
                        "cursor": "pointer",
                        "fontSize": "14px",
                    },
                ),
            ],
        ),

        # Cartões de resumo
        html.Div(
            id="cards-resumo",
            style={
                "display": "flex",
                "gap": "16px",
                "marginBottom": "30px",
                "flexWrap": "wrap",
            },
        ),

        # Gráficos
        html.Div(
            [
                dcc.Graph(id="grafico-casos", style={"width": "100%", "height": "400px"}),
                dcc.Graph(id="grafico-rt", style={"width": "100%", "height": "400px"}),
                dcc.Graph(id="grafico-media", style={"width": "100%", "height": "400px"}),
            ],
            style={"display": "flex", "flexDirection": "column", "gap": "20px"},
        ),
    ],
)


def card(titulo, valor, cor):
    """Cria um cartão de resumo estilizado."""
    return html.Div(
        style={
            "backgroundColor": "#1e1e1e",
            "borderLeft": f"5px solid {cor}",
            "borderRadius": "8px",
            "padding": "16px 24px",
            "flex": "1",
            "minWidth": "180px",
        },
        children=[
            html.P(titulo, style={"margin": "0", "color": "#aaa", "fontSize": "13px"}),
            html.H2(str(valor), style={"margin": "6px 0 0", "color": cor, "fontSize": "28px"}),
        ],
    )


# ─── Callback: resetar datas ───────────────────────────────────────────────
@app.callback(
    Output("filtro-datas", "start_date"),
    Output("filtro-datas", "end_date"),
    Input("btn-resetar", "n_clicks"),
    prevent_initial_call=True,
)
def resetar_datas(_):
    return data_min, data_max


# ─── Callback: atualizar gráficos e cards ─────────────────────────────────
@app.callback(
    Output("grafico-casos", "figure"),
    Output("grafico-rt", "figure"),
    Output("grafico-media", "figure"),
    Output("cards-resumo", "children"),
    Input("filtro-datas", "start_date"),
    Input("filtro-datas", "end_date"),
)
def atualizar_dashboard(start_date, end_date):
    # Filtrar dataframe pelo intervalo selecionado
    mask = (df["data_iniSE"] >= pd.to_datetime(start_date)) & (
        df["data_iniSE"] <= pd.to_datetime(end_date)
    )
    dff = df[mask]

    template = "plotly_dark"

    # Gráfico de casos semanais
    fig_casos = px.line(
        dff,
        x="data_iniSE",
        y="casos",
        title="Casos Semanais de Dengue",
        markers=True,
        template=template,
    )
    fig_casos.update_traces(line_color="#e74c3c")

    # Gráfico de Rt
    fig_rt = px.line(
        dff,
        x="data_iniSE",
        y="Rt",
        title="Taxa de Reprodução (Rt)",
        markers=True,
        template=template,
    )
    fig_rt.update_traces(line_color="#f39c12")
    # Linha de referência Rt = 1
    fig_rt.add_hline(
        y=1,
        line_dash="dash",
        line_color="white",
        annotation_text="Rt = 1 (limiar epidêmico)",
        annotation_position="bottom right",
    )

    # Gráfico da média móvel
    fig_media = px.line(
        dff,
        x="data_iniSE",
        y="media_movel",
        title="Média Móvel de Casos (4 semanas)",
        markers=True,
        template=template,
    )
    fig_media.update_traces(line_color="#2ecc71")

    # Cards de resumo
    total = int(dff["casos"].sum()) if not dff.empty else 0
    pico = int(dff["casos"].max()) if not dff.empty else 0
    rt_medio = round(dff["Rt"].mean(), 2) if not dff.empty else 0
    semanas = len(dff)

    cards = [
        card("Total de Casos", f"{total:,}".replace(",", "."), "#e74c3c"),
        card("Pico Semanal", f"{pico:,}".replace(",", "."), "#e67e22"),
        card("Rt Médio", rt_medio, "#f39c12"),
        card("Semanas Analisadas", semanas, "#2ecc71"),
    ]

    return fig_casos, fig_rt, fig_media, cards


if __name__ == "__main__":
    app.run(debug=True)