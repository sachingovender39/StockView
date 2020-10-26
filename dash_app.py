import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.foreignexchange import ForeignExchange
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#Preloaded symbols
symbols=['EURUSD','USDZAR']
#navbar

#input section 
input_form=html.Div([dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label("Indices", className="mr-2"),
                dbc.Input(type="text", placeholder="Enter symbol",id='input-box'),
            ],
            className="mr-3",
        ),
        dbc.Button("Submit", color="dark",id="button",n_clicks=0),
    ],inline=True
)])
#graph
graph_list=[]
output_list=[]
for i in symbols:
    graph_id = i+'_graph'
    graph_list.append(dcc.Graph(id=graph_id, animate=True, style={"backgroundColor": "#1a2d46", 'color':'#ffffff'}))
    output_list.append(Output(graph_id,'figure'))

graphs = html.Div(id='graphs',children=graph_list)

timer=dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )

body = html.Div([
    input_form,graphs,timer
])

app.layout=body
api_key = 'J2443HCF3V58552B'
period = 60
fx = TimeSeries(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format='pandas')
##########event handling###########

@app.callback(output_list,
              [Input('interval-component', 'n_intervals')],
              #[State('input-box', 'value')]
              )
def update_layout(n):
    figure_items=[]
    #Getting Dataframes Ready
    for i in symbols:
        from_currency = i.upper()[0:3]
        to_currency = i.upper()[3:]
        data_fx,meta_fx = fx.get_intraday(symbol=i, interval='1min',outputsize='full')
        data_fx.columns=['Open','High','Low','Close','Volume']
        print(data_fx.head())
        data_ti, meta_data_ti = ti.get_sma(symbol=i.upper(), interval='1min', time_period=period, series_type='close')
        data_fx = data_fx.iloc[::-1]
        BuySide = go.Candlestick(
            x=data_fx.index,
            open=data_fx['Open'],
            high=data_fx['High'],
            low=data_fx['Low'],
            close=data_fx['Close'],
            increasing={'line': {'color': '#00CC94'}},
            decreasing={'line': {'color': '#F50030'}},
            name='candlestick'
        )

        SMA = go.Scatter(
        x=data_ti.index,
        y=data_ti['SMA'],
        mode='lines',
        name='SMA'
        )
        data = [BuySide]

        layout = go.Layout(
            paper_bgcolor='#27293d',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(type="date",nticks=10,tickmode='auto'),
            yaxis=dict(range=[min(data_fx['Low']), max(data_fx['High'])]),
            font=dict(color='white'),
            height=700
        )
        figure_items.append({'data': data, 'layout': layout})

    return figure_items

# @app.callback([Input('button', 'n_clicks')],
#               [State('input-box', 'value')])
# def update_symbols(n_clicks,new_symbol):
#     print('adding')
    # new_graph_id = new_symbol.upper()+'_graph'
    # graph_list.append(dcc.Graph(id=new_graph_id, animate=True, style={"backgroundColor": "#1a2d46", 'color':'#ffffff'}))
    # output_list.append(Output(graph_id,'figure'))
    # symbols.append(new_symbol.upper())
if __name__ == '__main__':
    app.run_server(port=8088)