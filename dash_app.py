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
from threading import Thread
import pytz as tz
from datetime import datetime
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#Preloaded symbols
symbol=['EURUSD']
#navbar
##static components
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
)],style={'backgroundColor':"#1a2d46", 'color':'#ffffff','padding-bottom':'2%','padding-top':'2%'})
#timer
timer=dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )

#dynamic graphing function
graph_list=[dcc.Graph(id='graph', animate=True, style={"backgroundColor": "#1a2d46", 'color':'#ffffff'})]
output_list=[Output('graph','figure')]
graphs = html.Div(id='graphs',children=graph_list,style={"backgroundColor": "#1a2d46", 'color':'#ffffff'})
body = html.Div([
input_form,graphs,timer,html.P(id='place',style={'display':'none'})])
app.layout=body
api_key = 'J2443HCF3V58552B'
period = 60
fx = TimeSeries(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format='pandas')

##########event handling###########

def monitor():
    @app.callback(output_list,
                [Input('interval-component', 'n_intervals'),Input('button', 'n_clicks')],
                #[State('input-box', 'value')]
                )
    def update_layout(n,click):
        figure_items=[]
        #Getting Dataframes Ready
        print(symbol)
        data_fx,meta_fx = fx.get_intraday(symbol=symbol[0], interval='1min',outputsize='full')
        data_fx.columns=['Open','High','Low','Close','Volume']
        print(data_fx.head())
        data_ti, meta_data_ti = ti.get_sma(symbol=symbol[0].upper(), interval='1min', time_period=period, series_type='close')
        #######Timezone adjust################
        format = '%Y-%m-%d %H:%M:%S'
        old_timezone = tz.timezone(meta_fx['6. Time Zone'])
        new_timezone = tz.timezone("Africa/Johannesburg")
        ##convert index to SAST
        def getlocalindex(index):   
            local_index=[]
            for i in index:
                actual_datetime=datetime.strptime(str(i), format)
                local_timestamp = old_timezone.localize(actual_datetime).astimezone(new_timezone) 
                local_index.append(local_timestamp.strftime(format))
            return local_index
        data_fx.index=getlocalindex(data_fx.index)
        data_ti.index=getlocalindex(data_ti.index)
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
        data = [BuySide,SMA]

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
monitor_thread = Thread(target=monitor)
monitor_thread.start()
@app.callback(Output('place','children'),[Input('button', 'n_clicks')],
              [State('input-box', 'value')])
def update_symbols(n_clicks,new_symbol):
    print('adding')
    symbol[0]=new_symbol.upper()
    return new_symbol.upper()

if __name__ == '__main__':
    app.run_server(port=8088) 