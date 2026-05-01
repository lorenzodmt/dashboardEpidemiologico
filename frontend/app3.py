import json
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, clientside_callback
import plotly.graph_objects as go

# ─── Temas ────────────────────────────────────────────────────────────────────
TEMAS = {
    "escuro": {
        "bg":         "#0d1117",
        "surface":    "#161b22",
        "surface2":   "#21262d",
        "border":     "#30363d",
        "text":       "#e6edf3",
        "text_muted": "#8b949e",
        "accent":     "#f85149",
        "accent2":    "#d29922",
        "accent3":    "#3fb950",
        "accent4":    "#58a6ff",
        "paper_bg":   "#161b22",
        "plot_bg":    "#161b22",
        "grid":       "#21262d",
    },
    "claro": {
        "bg":         "#f4f6f9",
        "surface":    "#ffffff",
        "surface2":   "#eef1f5",
        "border":     "#d0d7de",
        "text":       "#1c2128",
        "text_muted": "#57606a",
        "accent":     "#cf222e",
        "accent2":    "#9a6700",
        "accent3":    "#1a7f37",
        "accent4":    "#0969da",
        "paper_bg":   "#ffffff",
        "plot_bg":    "#ffffff",
        "grid":       "#eef1f5",
    },
}

FONTS = [
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600"
    "&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap"
]

# ─── Dados ────────────────────────────────────────────────────────────────────
with open("../backend/data.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["data_iniSE"] = pd.to_datetime(df["data_iniSE"])
data_min = df["data_iniSE"].min().date()
data_max = df["data_iniSE"].max().date()

# ─── App ──────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, external_stylesheets=FONTS)
app.title = "Dashboard Epidemiológico · Dengue"

# CSS estrutural fixo (não muda com o tema)
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { box-sizing: border-box; }
            html, body { margin: 0; padding: 0; height: 100%; }
            body { transition: background-color 0.3s, color 0.3s; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div(
    id="root",
    style={"minHeight": "100vh", "fontFamily": "'IBM Plex Sans', sans-serif",
           "transition": "background-color 0.3s, color 0.3s"},
    children=[
        dcc.Store(id="tema-store", data="escuro"),

        # ── Cabeçalho ─────────────────────────────────────────────────────
        html.Header(id="header",
            style={"display": "flex", "justifyContent": "space-between",
                   "alignItems": "center", "padding": "20px 24px",
                   "position": "sticky", "top": "0", "zIndex": "100",
                   "boxShadow": "0 2px 12px rgba(0,0,0,0.2)",
                   "transition": "background-color 0.3s"},
            children=[
                html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px"}, children=[
                    html.Span("🦟", style={"fontSize": "28px"}),
                    html.Div([
                        html.H1("Dashboard Epidemiológico",
                                style={"margin": "0", "fontSize": "20px", "fontWeight": "700",
                                       "fontFamily": "'IBM Plex Sans', sans-serif"}),
                        html.P("Monitoramento de Dengue · Atualização semanal",
                               style={"margin": "0", "fontSize": "12px",
                                      "fontFamily": "'IBM Plex Mono', monospace"}),
                    ]),
                ]),
                html.Button(id="btn-tema", n_clicks=0, children="🌙  Modo Claro",
                            style={"padding": "8px 18px", "borderRadius": "20px",
                                   "border": "1px solid", "cursor": "pointer",
                                   "fontFamily": "'IBM Plex Sans', sans-serif",
                                   "fontWeight": "600", "fontSize": "13px",
                                   "transition": "all 0.25s"}),
        ]),

        # ── Filtros ───────────────────────────────────────────────────────
        html.Div(id="filtro-panel",
            style={"borderRadius": "10px", "padding": "16px 20px",
                   "margin": "24px 24px 20px",
                   "transition": "background-color 0.3s"},
            children=[
                html.Div(style={"display": "flex", "alignItems": "center",
                                "gap": "10px", "flexWrap": "wrap"}, children=[
                    html.Span("📅", style={"fontSize": "18px"}),
                    html.Label("Intervalo de datas",
                               style={"fontWeight": "600", "fontSize": "14px",
                                      "fontFamily": "'IBM Plex Sans', sans-serif"}),
                    dcc.DatePickerRange(
                        id="filtro-datas",
                        min_date_allowed=data_min,
                        max_date_allowed=data_max,
                        start_date=data_min,
                        end_date=data_max,
                        display_format="DD/MM/YYYY",
                    ),
                    html.Button("↺  Resetar", id="btn-resetar", n_clicks=0,
                                style={"padding": "7px 16px", "borderRadius": "6px",
                                       "border": "none", "cursor": "pointer",
                                       "fontFamily": "'IBM Plex Sans', sans-serif",
                                       "fontWeight": "600", "fontSize": "13px",
                                       "backgroundColor": "#cf222e", "color": "#fff"}),
                ]),
        ]),

        # ── Cards ─────────────────────────────────────────────────────────
        html.Div(id="cards-resumo",
                 style={"display": "flex", "gap": "16px", "flexWrap": "wrap",
                        "margin": "0 24px 24px"}),

        # ── Gráficos ──────────────────────────────────────────────────────
        html.Div(id="graficos-wrapper",
                 style={"display": "flex", "flexDirection": "column", "gap": "20px",
                        "padding": "0 24px 40px"}, children=[
            html.Div(id="wrap-casos", children=[dcc.Graph(id="grafico-casos")],
                     style={"borderRadius": "10px", "overflow": "hidden",
                            "boxShadow": "0 2px 8px rgba(0,0,0,0.12)",
                            "transition": "background-color 0.3s"}),
            html.Div(id="wrap-rt",    children=[dcc.Graph(id="grafico-rt")],
                     style={"borderRadius": "10px", "overflow": "hidden",
                            "boxShadow": "0 2px 8px rgba(0,0,0,0.12)",
                            "transition": "background-color 0.3s"}),
            html.Div(id="wrap-media", children=[dcc.Graph(id="grafico-media")],
                     style={"borderRadius": "10px", "overflow": "hidden",
                            "boxShadow": "0 2px 8px rgba(0,0,0,0.12)",
                            "transition": "background-color 0.3s"}),
        ]),
    ],
)

# ─── Clientside callback: aplica o tema diretamente no DOM ────────────────────
# Isso roda no browser, sem round-trip ao servidor — garante que body e root
# recebem as cores imediatamente, sem depender de CSS externo ou observer.
clientside_callback(
    """
    function(tema) {
        var temas = {
            escuro: {
                bg:       '#0d1117', surface:  '#161b22', surface2: '#21262d',
                border:   '#30363d', text:     '#e6edf3', text_muted:'#8b949e',
                accent4:  '#58a6ff'
            },
            claro: {
                bg:       '#f4f6f9', surface:  '#ffffff', surface2: '#eef1f5',
                border:   '#d0d7de', text:     '#1c2128', text_muted:'#57606a',
                accent4:  '#0969da'
            }
        };
        var t = temas[tema];

        // body e root
        document.body.style.backgroundColor = t.bg;
        document.body.style.color           = t.text;
        var root = document.getElementById('root');
        if (root) { root.style.backgroundColor = t.bg; root.style.color = t.text; }

        // header
        var header = document.getElementById('header');
        if (header) {
            header.style.backgroundColor = t.surface;
            header.style.borderBottom    = '1px solid ' + t.border;
        }

        // btn-tema
        var btn = document.getElementById('btn-tema');
        if (btn) {
            btn.style.backgroundColor = t.surface2;
            btn.style.color           = t.text;
            btn.style.borderColor     = t.border;
        }

        // filtro-panel
        var fp = document.getElementById('filtro-panel');
        if (fp) {
            fp.style.backgroundColor = t.surface;
            fp.style.border          = '1px solid ' + t.border;
        }

        // chart-cards (wrappers dos graficos)
        ['wrap-casos','wrap-rt','wrap-media'].forEach(function(id) {
            var el = document.getElementById(id);
            if (el) {
                el.style.backgroundColor = t.surface;
                el.style.border          = '1px solid ' + t.border;
            }
        });

        return window.dash_clientside.no_update;
    }
    """,
    Output("root", "data-tema"),   # output dummy (só para disparar o callback)
    Input("tema-store", "data"),
)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_card(icone, titulo, valor, cor, t):
    return html.Div(
        style={"backgroundColor": t["surface"], "border": f"1px solid {t['border']}",
               "borderTop": f"3px solid {cor}", "borderRadius": "10px",
               "padding": "18px 22px", "flex": "1", "minWidth": "160px",
               "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"},
        children=[
            html.Div(style={"display": "flex", "alignItems": "center",
                            "gap": "8px", "marginBottom": "8px"}, children=[
                html.Span(icone, style={"fontSize": "18px"}),
                html.P(titulo, style={"margin": "0", "fontSize": "12px",
                                      "color": t["text_muted"],
                                      "fontFamily": "'IBM Plex Mono', monospace",
                                      "fontWeight": "600", "textTransform": "uppercase",
                                      "letterSpacing": "0.5px"}),
            ]),
            html.H2(str(valor), style={"margin": "0", "color": cor, "fontSize": "30px",
                                       "fontFamily": "'IBM Plex Mono', monospace",
                                       "fontWeight": "600"}),
        ],
    )


def make_fig(dff, x, y, title, color, t, hline=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dff[x], y=dff[y],
        mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=5, color=color),
        hovertemplate=f"<b>%{{x|%d/%m/%Y}}</b><br>{y}: %{{y:.2f}}<extra></extra>",
    ))
    if hline:
        fig.add_hline(y=hline["y"], line_dash="dot", line_color=t["text_muted"],
                      annotation_text=hline["label"],
                      annotation_font_color=t["text_muted"],
                      annotation_position="bottom right")
    fig.update_layout(
        title=dict(text=title, font=dict(family="'IBM Plex Sans', sans-serif",
                                          size=15, color=t["text"]), x=0.02),
        paper_bgcolor=t["paper_bg"],
        plot_bgcolor=t["plot_bg"],
        font=dict(family="'IBM Plex Sans', sans-serif", color=t["text"]),
        xaxis=dict(showgrid=True, gridcolor=t["grid"], zeroline=False,
                   tickfont=dict(family="'IBM Plex Mono', monospace", size=11)),
        yaxis=dict(showgrid=True, gridcolor=t["grid"], zeroline=False,
                   tickfont=dict(family="'IBM Plex Mono', monospace", size=11)),
        margin=dict(l=50, r=30, t=50, b=40),
        height=360,
        hovermode="x unified",
    )
    return fig

# ─── Callbacks Python ─────────────────────────────────────────────────────────

@app.callback(
    Output("tema-store", "data"),
    Output("btn-tema",   "children"),
    Input("btn-tema",    "n_clicks"),
    State("tema-store",  "data"),
    prevent_initial_call=True,
)
def alternar_tema(_, tema_atual):
    if tema_atual == "escuro":
        return "claro", "🌙  Modo Escuro"
    return "escuro", "☀️  Modo Claro"


@app.callback(
    Output("filtro-datas", "start_date"),
    Output("filtro-datas", "end_date"),
    Input("btn-resetar",   "n_clicks"),
    prevent_initial_call=True,
)
def resetar_datas(_):
    return data_min, data_max


@app.callback(
    Output("grafico-casos", "figure"),
    Output("grafico-rt",    "figure"),
    Output("grafico-media", "figure"),
    Output("cards-resumo",  "children"),
    Input("filtro-datas",   "start_date"),
    Input("filtro-datas",   "end_date"),
    Input("tema-store",     "data"),
)
def atualizar(start_date, end_date, tema_key):
    t = TEMAS[tema_key]
    mask = (
        (df["data_iniSE"] >= pd.to_datetime(start_date)) &
        (df["data_iniSE"] <= pd.to_datetime(end_date))
    )
    dff = df[mask]

    fig_casos = make_fig(dff, "data_iniSE", "casos",
                          "🦟  Casos Semanais de Dengue", t["accent"], t)
    fig_rt    = make_fig(dff, "data_iniSE", "Rt",
                          "📈  Taxa de Reprodução (Rt)", t["accent2"], t,
                          hline={"y": 1, "label": "Rt = 1  (limiar epidêmico)"})
    fig_media = make_fig(dff, "data_iniSE", "media_movel",
                          "📉  Média Móvel (4 semanas)", t["accent3"], t)

    total   = int(dff["casos"].sum())           if not dff.empty else 0
    pico    = int(dff["casos"].max())            if not dff.empty else 0
    rt_med  = round(float(dff["Rt"].mean()), 2) if not dff.empty else 0
    semanas = len(dff)

    cards = [
        make_card("🦟", "Total de Casos",    f"{total:,}".replace(",", "."), t["accent"],  t),
        make_card("🔝", "Pico Semanal",       f"{pico:,}".replace(",", "."),  t["accent2"], t),
        make_card("📊", "Rt Médio",           rt_med,                          t["accent4"], t),
        make_card("📅", "Semanas Analisadas", semanas,                         t["accent3"], t),
    ]

    return fig_casos, fig_rt, fig_media, cards


if __name__ == "__main__":
    app.run(debug=True)