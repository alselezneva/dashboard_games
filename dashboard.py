from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px


# Подготовка датасета
def build_df(data, platform_value=[], year_value=[], genre_value=[], area=False):

    if (not isinstance(year_value, list)) or (len(year_value) == 0):
        year_value = data['Year_of_Release'].unique()
    else:
        year_value = range(year_value[0], year_value[-1] + 1)

    if (not isinstance(platform_value, list)) or (len(platform_value) == 0):
        platform_value = data['Platform'].unique()

    if (not isinstance(genre_value, list)) or (len(genre_value) == 0):
        genre_value = data['Genre'].unique()

    mask_gender = (data['Genre'].isin(genre_value))
    mask_platform = (data['Platform'].isin(platform_value))
    mask_year = (data['Year_of_Release'].isin(year_value))

    data = data[mask_gender & mask_platform & mask_year]
    data = data.rename(columns={'Year_of_Release': 'Year', 'Name': 'Value'})

    if area:
        data = data.groupby(by=['Year', 'Platform']).count()[['Value']].reset_index()

    return data


external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Game industry"

df = pd.read_csv("games.csv")
df = df[df['Year_of_Release'] >= 2000]
df = df.dropna()
df = df[df['User_Score'] != 'tbd']
df['User_Score'] = df['User_Score'].apply(lambda x: float(x))
df['Year_of_Release'] = df['Year_of_Release'].apply(lambda x: int(x))


fig = px.scatter(
    x=df['User_Score'],
    y=df['Critic_Score'],
    color=df['Genre'],
    title='Распределение оценок игроков и критиков'
)

fig2 = px.area(
    x=build_df(df, area=True)['Year'],
    y=build_df(df, area=True)['Value'],
    color=build_df(df, area=True)['Platform'],
    title='Выпуск игр по годам и платформам'
)

year_slider = dcc.RangeSlider(
    id='year-slider',
    min=2000,
    max=2016,
    marks={i: str(i) for i in range(2000, 2017)},
    value=[2000, 2016]
)

dropdown_genre = dcc.Dropdown(
    id='dropdown-genre',
    options=[{'label': i, 'value': i} for i in df['Genre'].unique()],
    placeholder="Select a genre",
    optionHeight=50,
    multi=True,
)

dropdown_platform = dcc.Dropdown(
    id='dropdown-platform',
    options=[{'label': i, 'value': i} for i in df['Platform'].unique()],
    placeholder="Select a platform",
    optionHeight=50,
    multi=True
)

app.layout = html.Div([

    dbc.Row(
        [
            dbc.Col([
                html.H1(
                    children="История игровой индустрии",
                    className="header-title")
                ],
                width={"size": 5, "offset": 4},
            )
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                html.P(
                    children="""
                    Интерактивные графики помогут узнать больше об игровой индустрии
                    в 2000-2016 гг.
                    """,
                    className="header-description"),
            ],
                width={"offset": 4},
            )
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                html.P("Выбрать жанр:"),
                html.Div(dropdown_genre)
            ],
                width={"size": 5, "offset": 1},),

            dbc.Col([
                html.P("Выбрать платформу:"),
                html.Div(dropdown_platform)
            ],
                width={"size": 5, "offset": 0},)
        ]
    ),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col([
                html.Div(
                    children=f"Количество выбранных игр: {build_df(df).shape[0]}",
                    id="first_output_3")
            ],
                width={"size": 4, "offset": 1}, )
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                dcc.Graph(
                    id="scatter-plot",
                    figure=fig,
                    style={'display': 'inline-block'})
            ],
                width={"size": 4, "offset": 1},),

            dbc.Col([
                dcc.Graph(
                    id="stack-area",
                    figure=fig2,
                    style={'display': 'inline-block'})
            ],
                width={"size": 4, "offset": 1},)
        ]
    ),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col([
                html.P("Выбрать год:"),
                html.Div(year_slider),
            ],
                width={"size": 10, "offset": 1},
            )
        ], align="center"
    ),
]
)


# Обновление графика scatter (Распределение оценок игроков и критиков)
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('dropdown-platform', 'value'),
     Input('year-slider', 'value'),
     Input('dropdown-genre', 'value')])
def update_graph(platform_value, year_value, genre_value):
    dff = build_df(df, platform_value, year_value, genre_value)

    if dff.shape[0] > 0:
        fig = px.scatter(x=dff['User_Score'],
                         y=dff['Critic_Score'],
                         color=dff['Genre'],
                         title='Распределение оценок игроков и критиков')
    else:
        fig = px.scatter(title='Распределение оценок игроков и критиков')
    return fig


# Обновление графика area (Выпуск игр по годам и платформам)
@app.callback(
    Output('stack-area', 'figure'),
    [Input('dropdown-platform', 'value'),
     Input('year-slider', 'value'),
     Input('dropdown-genre', 'value')])
def update_stack_area(platform_value, year_value, genre_value):
    dff = build_df(df, platform_value, year_value, genre_value, area=True)
    if dff.shape[0] > 0:
        fig2 = px.area(x=dff['Year'],
                       y=dff['Value'],
                       color=dff['Platform'],
                       title='Выпуск игр по годам и платформам')
    else:
        fig2 = px.area(title='Выпуск игр по годам и платформам')

    return fig2


# Обновление text_area (Количество выбранных игр)
@app.callback(
    Output('first_output_3', 'children'),
    [Input('dropdown-platform', 'value'),
     Input('year-slider', 'value'),
     Input('dropdown-genre', 'value')])
def update_text_area(platform_value, year_value, genre_value):
    dff = build_df(df, platform_value, year_value, genre_value)
    how_many_games = dff.shape[0]

    return f'Количество выбранных игр: {how_many_games}'


# Обновление выпадающего списка для выбора платформы
@app.callback(
    Output('dropdown-platform', 'options'),
    [Input('year-slider', 'value'),
     Input('dropdown-platform', 'value'),
     Input('dropdown-genre', 'value')])
def update_multi_options(year_value, platform_value, genre_value):
    if not platform_value:
        raise PreventUpdate
    dff = build_df(df, year_value=year_value, genre_value=genre_value)
    print(dff['Platform'].unique())
    return [{'label': i, 'value': i} for i in dff['Platform'].unique()]


# Обновление выпадающего списка для выбора жанра
@app.callback(
    Output('dropdown-genre', 'options'),
    [Input('year-slider', 'value'),
     Input('dropdown-platform', 'value'),
     Input('dropdown-genre', 'value')])
def update_multi_options(year_value, platform_value, genre_value):
    if not genre_value:
        raise PreventUpdate
    dff = build_df(df, year_value=year_value, platform_value=platform_value)
    print(dff['Genre'].unique())
    return [{'label': i, 'value': i} for i in dff['Genre'].unique()]


if __name__ == '__main__':
    app.run_server(debug=True)
