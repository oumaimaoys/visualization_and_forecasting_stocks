import dash
from dash import dcc, html, Input, Output, State
from datetime import datetime as dt
from datetime import date
import yahooquery as yq
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

app = dash.Dash(__name__)
server = app.server

item1 = html.Div(
    [
        html.P("Dash Stocks app", id="title"),
        html.Div([
            html.P("input stock code:", className="bodystyle"),
            html.Div([
                # stock code input
                dcc.Input(
                    placeholder='Enter the stock code',
                    type='text',
                    value='',
                    id="stock-code-input",
                    className="input-space"
                ),
                # submit button
                html.Button('Submit', className='button-box', id="stock-code-button", n_clicks=0)
            ], className="input-box")

        ], className="box"),
        html.Div([
            # date range picker input
            dcc.DatePickerRange(
                id='my_date_picker_range',
                min_date_allowed=date(1990, 1, 1),
                max_date_allowed=date(2022, 12, 31),
                initial_visible_month=dt.today(),
                end_date=dt.today()
            ),

        ], className="box"),
        html.Div([
            html.Div([
                # stock price button
                html.Button('Stock Price', id='stock-Price-button', n_clicks=0),
                # indicators button
                html.Button('Indicators', id='indicator-button', n_clicks=0)
            ], className="two-buttons"),

            html.Div([
                # number of days of forecast input
                dcc.Input(
                    placeholder='Enter number of days',
                    type='text',
                    value='',
                    className="input-space"
                ),
                # forecast button
                html.Button('Forecast', className='button-box', n_clicks=0),
            ], className="input-box")

        ], className="box")
    ], className="inputs")
item2 = html.Div(
    [
        html.Div([
            # company name
        ], id="header-id", className="header"),
        html.Div(
            # description
            id="description", className="description_ticker"
        ),
        html.Div([
            # stock price plot
        ], id="graphs-content", className="graph"),
        html.Div([
            # Indicator plot
        ], id="main-content", className="graph"),
        html.Div([
            # forecast plot
        ], id="forecast-content", className="graph")

    ], className="content")

app.layout = html.Div([item1, item2], className="container")


@app.callback(
    [Output(component_id="header-id", component_property="children"),
     Output("description", "children")],
    [Input(component_id="stock-code-button", component_property="n_clicks")],
    [State(component_id="stock-code-input", component_property="value")]
)
def get_company_info(times_clicked, stock_code):
    ticker = yq.Ticker(stock_code)
    inf_1 = ticker.asset_profile
    inf_2 = ticker.price
    df_1 = pd.DataFrame().from_dict(inf_1, orient="index")
    df_2 = pd.DataFrame().from_dict(inf_2, orient="index")
    return df_2.at[df_2.index[0], 'shortName'], df_1.at[df_1.index[0], 'longBusinessSummary']


# user defined function that returns stock figure from DataFrame
def get_stock_price_fig(df):
    fig = px.line(df,
                  x="date",
                  y=["close", "open"],
                  title="Closing and Opening Price vs Date"
                  )
    return fig


@app.callback(
    Output("graphs-content", "children"),
    [Input('my_date_picker_range', 'start_date'),
     Input('my_date_picker_range', 'end_date'),
     Input("stock-Price-button", "n_clicks")],
    [State(component_id="stock-code-input", component_property="value")]
)
def get_stock_price_plot(start_date, end_date, times_clicks, stock_code):
    df = yq.Ticker(stock_code).history(start=start_date, end=end_date)
    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return dcc.Graph(figure=fig)


# user defines function that return indicator  figure
def get_more(df):
    df["ewa_20"] = df['close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x='date',
                     y='ewa_20',
                     title="Exponential Moving Average vs Date",
                     )
    fig.update_traces(overwrite=True)
    return fig


@app.callback(
    Output("main-content", "children"),
    [Input('my_date_picker_range', 'start_date'),
     Input('my_date_picker_range', 'end_date'),
     Input("indicator-button", "n_clicks")],
    [State(component_id="stock-code-input", component_property="value")]
)
def get_indicator_plot(start_date, end_date, times_clicks, stock_code):
    df = yq.Ticker(stock_code).history(start=start_date, end=end_date)
    df.reset_index(inplace=True)
    fig = get_more(df)
    return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True)
