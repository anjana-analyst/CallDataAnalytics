#for processes
import pandas as pd
import re

#for graph
import plotly.express as px

#for rendering it in UI
import webbrowser
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input,Output
import dash_bootstrap_components as dbc
import dash_table as dt

app=dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

project_name="CDR call data analytics"


def dataloading():
    #first load the data files
    call_dataset="Call_data.csv"
    service_dataset="Service_data.csv"
    device_dataset="Device_data.csv"
    
    #make the var global as we use outside the fn too 
    global calldata
    global devicedata
    global servicedata
    
    #now read the csv files and store it accordingly
    calldata=pd.read_csv(call_dataset)
    devicedata=pd.read_csv(device_dataset)
    servicedata=pd.read_csv(service_dataset)
    
    #for data preparation to produce graphs
    global startdate
    templist=sorted(calldata['date'].dropna().unique().tolist())
    startdate=[{"label":str(i),"value":str(i)} for i in templist]
    
    global enddate
    enddate=startdate
    
    global report_type
    templist=["Hourly","Daily","Weekly"]
    report_type=[{"label":str(i),"value":str(i)} for i in templist]
    
def openbrowser():
    # Open the default web browser
    webbrowser.open_new('http://127.0.0.1:8050/')
    
def create_appUI():
    main_layout=html.Div([
        html.H1("CDR call data analytics with insights",id="Main title"),
        dcc.Tabs(id="tabs",value="tab-1",children=[
            dcc.Tab(label="call analytics",id="call data analytics",value="tab-1",children=[
                html.Br(),
                html.Br(),
                
                dcc.Dropdown(
                    id="start-date-dropdown",
                    options=startdate,
                    placeholder="Select starting date here",
                    value="2019-06-20"),
                
                dcc.Dropdown(
                    id="end-date-dropdown",
                    options=enddate,
                    placeholder="Select ending date here",
                    value="2019-06-20"),
                
                dcc.Dropdown(
                    id="select-group-dropdown",
                    placeholder="Select group",
                    multi=True
                    ),
                
                dcc.Dropdown(
                    id="group-type-dropdown",
                    options=report_type,
                    placeholder="Select report type",
                    value="Hourly"
                    )]),
            
            dcc.Tab(label="Device data analytics",id="Device data analytics",value="tab-2",children=[
                html.Br(),
                dcc.Dropdown(
                    id="Device-data-analytics",
                    options=startdate,
                    placeholder="Select starting date here",
                    multi=True),
                  html.Br()]),
        
           dcc.Tab(label="Service data analytics",id="Service data analytics",value="tab-3",children=[
               html.Br(),
               dcc.Dropdown(
                   id="Service-data-analytics",
                   options=startdate,
                   placeholder="Select starting date here",
                   multi=True),
               html.Br()])     
           ]),
          html.Br(),
         dcc.Loading(html.Div(id='visualization',children='Graph, Card, Table')),
           
            ])
    return main_layout

def card_creation(title,content,color):
    card=dbc.Card(
        dbc.CardBody([
            html.H4(title),
            html.Br(),
            html.Br(),
            html.H2(content),
            html.Br()
            ]),
        color=color,inverse=True
        )
    return (card)

def device_count(data):
    #device names types
    devices = {"Polycom" :0,
    "Windows" : 0,
    "iphone" : 0,
    "Android" : 0,
    "Mac" : 0,
    "Yealink" : 0,
    "Aastra" : 0,
    "Others" : 0}
    
    #collect and store the data in a neat manner
    data_reformed=data["UserDeviceType"].dropna().reset_index()
    
    #store data according to device type
    for i in data_reformed["UserDeviceType"]:
        if re.search('Polycom',i):
            devices["Polycom"]+=1
        elif re.search('Windows',i):
            devices["Windows"]+=1
        elif re.search('iphone',i):
            devices["iphone"]+=1
        elif re.search('Android',i):
            devices["Android"]+=1
        elif re.search('Mac',i):
            devices["Mac"]+=1
        elif re.search('Yealink',i):
            devices["Yealink"]+=1
        elif re.search('Aastra',i):
            devices["Aastra"]+=1
        else:
            devices["Others"]+=1
            
    data_final=pd.DataFrame()
    data_final["Device"]=devices.keys()
    data_final["Count"]=devices.values()
    return data_final

#call-back for page
@app.callback(
     Output('visualization','children'),
      [
        Input("tabs","value"),
        Input("start-date-dropdown",'value'),
        Input("end-date-dropdown",'value'),
        Input("select-group-dropdown",'value'),
        Input("group-type-dropdown",'value'),
        Input("Device-data-analytics",'value'),
        Input("Service-data-analytics",'value')
      ]
      )

def final_UI(tabs, start_date, end_date, group, report_types,device_date,service_date):
    
    print("Data Type of start_date value = " , str(type(start_date)))
    print("Data of start_date value = " , str(start_date))
    
    print("Data Type of end_date value = " , str(type(end_date)))
    print("Data of end_date value = " , str(end_date))
    
    
    print("Data Type of group value = " , str(type(group)))
    print("Data of group value = " , str(group))
    
    print("Data Type of report_type value = " , str(type(report_types)))
    print("Data of report_type value = " , str(report_types))
    
    print("Data Type of device_date value = " , str(type(device_date)))
    print("Data of device_date value = " , str(device_date))

    print("Data Type of service_date value = " , str(type(service_date)))
    print("Data of service_date value = " , str(service_date))
    if tabs=="tab-1":
        # Filter the data as per the selection of the drop downs
        
        call_analytics_data = calldata[ (calldata["date"]>=start_date) & (calldata["date"]<=end_date) ]
         
        if group  == [] or group is None:
           pass
        else:
           call_analytics_data = call_analytics_data[call_analytics_data["Group"].isin(group)]
           
        graph_data = call_analytics_data
        # Group the data based on the drop down     
        if report_types == "Hourly":
            graph_data = graph_data.groupby("hourly_range")["Call_Direction"].value_counts().reset_index(name = "count")
            x = "hourly_range"
            
            content = call_analytics_data["hourly_range"].value_counts().idxmax()
            title =  "Busiest Hour"
        
            
        elif report_types == "Daily":
            graph_data = graph_data.groupby("date")["Call_Direction"].value_counts().reset_index(name = "count")
            x = "date"
            
            content = call_analytics_data["date"].value_counts().idxmax()
            title =  "Busiest Day"
            
        else:
            graph_data = graph_data.groupby("weekly_range")["Call_Direction"].value_counts().reset_index(name = "count")
            x = "weekly_range"
            
            content = call_analytics_data["weekly_range"].value_counts().idxmax()
            title =  "Busiest WeekDay"
            
           
        # Graph Section
        figure = px.area(graph_data, 
                         x = x, 
                         y = "count",
                         color = "Call_Direction",
                         hover_data=[ "Call_Direction", "count"], 
                         template = "plotly_white")
        figure.update_traces(mode = "lines+markers")
      
      
      
        # Card Section
        total_calls = call_analytics_data["Call_Direction"].count()
        card_1 = card_creation("Total Calls",total_calls, "success")
          
        incoming_calls = call_analytics_data["Call_Direction"][call_analytics_data["Call_Direction"]=="Incoming"].count()
        card_2 = card_creation("Incoming Calls", incoming_calls, "primary")
          
        outgoing_calls = call_analytics_data["Call_Direction"][call_analytics_data["Call_Direction"]=="Outgoing"].count()
        card_3 = card_creation("Outgoing Calls", outgoing_calls, "secondary")
          
        missed_calls = call_analytics_data["Missed Calls"][call_analytics_data["Missed Calls"] == 3].count()
        card_4 = card_creation("Missed Calls", missed_calls, "warning")
          
        max_duration = call_analytics_data["duration"].max()
        card_5 = card_creation("Max Duration", f'{max_duration} min', "dark")
        
        card_6 = card_creation(title, content, "info")
             
      
    
        graphRow0 = dbc.Row([dbc.Col(id='card1', children=[card_1], md=3), dbc.Col(id='card2', children=[card_2], md=3)])
        graphRow1 = dbc.Row([dbc.Col(id='card3', children=[card_3], md=3), dbc.Col(id='card4', children=[card_4], md=3)])
        graphRow2 = dbc.Row([dbc.Col(id='card5', children=[card_5], md=3), dbc.Col(id='card6', children=[card_6], md=3)])
     
        cardDiv = html.Div([graphRow0,html.Br(), graphRow1,html.Br(), graphRow2])
        
    
    
    
    
        # Data Table Section
    
        datatable_data = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["Call_Direction"].value_counts().unstack(fill_value = 0).reset_index()
        if call_analytics_data["Missed Calls"][call_analytics_data["Missed Calls"]==19].count()!=0:
            datatable_data["Missed Calls"] = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["Missed Calls"].value_counts().unstack()[3]
        else:
            datatable_data["Missed Calls"] = 0
            
        datatable_data["Total_call_duration"] = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["duration"].sum().tolist()
        
      
    
        datatable = dt.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in datatable_data.columns],
        data=datatable_data.to_dict('records'),
        page_current=0,
        page_size=5,
        page_action='native',
        style_header={'backgroundColor': 'rgb(40, 40, 40)'},
        style_cell={
            'backgroundColor': 'rgb(60, 60, 60)',
            'color': 'white'
        }
        )
        
            
        return [
                dcc.Graph(figure = figure), 
                html.Br() ,
                cardDiv, 
                html.Br(),
                datatable
               ]
 
     #device analytics
    elif tabs == "tab-2":
        if device_date is None or device_date == []: 
            device_analytics_data = device_count(devicedata)
        else:
            device_analytics_data = device_count(devicedata[devicedata["DeviceEventDate"].isin(device_date)])
          
        fig = px.pie(device_analytics_data, names = "Device", values = "Count", color = "Device", hole = .3)
        fig.update_layout(autosize=True,
                          margin=dict(l=0, r=0, t=25, b=20),
                          )
        return dcc.Graph(figure = fig)
    
    #service analytics
    elif tabs == "tab-3":
        if service_date is None or service_date == []:
            service_analytics_data = servicedata["FeatureName"].value_counts().reset_index(name = "Count")
        else:
            service_analytics_data = servicedata["FeatureName"][servicedata["FeatureEventDate"].isin(service_date)].value_counts().reset_index(name = "Count")
        fig = px.pie(service_analytics_data, names = "index", values = "Count",color = "index")
        
        fig.update_layout(autosize=True,
                          margin=dict(l=0, r=0, t=25, b=20),
                          )
        return dcc.Graph(figure = fig)
    
    #if any other return nothing
    else:
        return None
    
@app.callback(
    Output("select-group-dropdown", "options"),
    [
    Input('start-date-dropdown', 'value'),
    Input('end-date-dropdown', 'value')
    ]
    )
    
def groups_update(start_date, end_date): 
    reformed_data = calldata[(calldata["date"]>=start_date) & (calldata["date"]<=end_date)]
    group_list = reformed_data["Group"].unique().tolist()
    group_list = [{"label":m, "value":m} for m in group_list]
    return group_list

#ultimate main that interacts with all other functions
def main():
    dataloading()
    
    openbrowser()
    
    global app, project_name
    project_name = "CDR Analysis with Insights"
    app.layout = create_appUI()
    app.title = project_name

    
    # go to https://www.favicon.cc/ and download the ico file and store in assets directory 
    app.run_server() # debug=True
    
    
    print("This would be executed only after the script is closed")
    
    app = None
    project_name = None
    
    global calldata,servicedata,startdate,enddate,report_type
    calldata = None
    servicedata = None
    startdate = None
    enddate = None
    report_type= None  
    
    
#calling of the main
if __name__ == '__main__':
    main()


