import pandas as pd
import plotly.express as px 
from dash import Dash, dcc, html, Input, Output
from datetime import date, datetime
import numpy as np

app = Dash( __name__)

# -- Import and clean data (importing csv into pandas)
DataBasePath = "/<Path>"
DataBaseSprintDataName = "/<FileName>.csv"
DataBaseKanbanDataName = "/<FileName>.csv"

FullSprintData = pd.read_csv(DataBasePath + DataBaseSprintDataName, sep=";", index_col=0)
FullKanbanData = pd.read_csv(DataBasePath + DataBaseKanbanDataName, sep=";", index_col=0)

# FullSprintData = FullSprintData.append(FullKanbanData, ignore_index=True)

FullSprintData['Count(*)'] = 1

FullSprintData['Date Extracted'] = pd.to_datetime(FullSprintData['Date Extracted'])
MinDate = FullSprintData['Date Extracted'].min()
MaxDate = FullSprintData['Date Extracted'].max()
MinYear = FullSprintData['Date Extracted'].min().year
MinMonth = FullSprintData['Date Extracted'].min().month
MinDay = FullSprintData['Date Extracted'].min().day
MaxYear = FullSprintData['Date Extracted'].max().year
MaxMonth = FullSprintData['Date Extracted'].max().month
MaxDay = FullSprintData['Date Extracted'].max().day
FullSprintData['Date Extracted'] = pd.to_datetime(FullSprintData['Date Extracted']).dt.date



FullSprintDataStatus = pd.get_dummies(FullSprintData, columns=["Status"], drop_first=False)
FullSprintDataStatus = FullSprintDataStatus.groupby(['Project Name', 'Issue Type', 'Issue Key', 'Issue Id', 'Summary', 'Priority'])[['Status_Backlog', 'Status_Blocked', 'Status_Blocker',
       'Status_Blocker/Waiting', 'Status_Communicate', 'Status_Done',
       'Status_In Progress', 'Status_Prioritised Backlog',
       'Status_Ready for Design', 'Status_Ready to Build', 'Status_Review',
       'Status_Testing', 'Status_Under Review']].sum()
FullSprintDataStatus.reset_index(inplace=True)

FullSprintDataStatus['Total Blocked Time'] = FullSprintDataStatus['Status_Blocked'] + FullSprintDataStatus['Status_Blocker/Waiting'] + FullSprintDataStatus['Status_Blocker']

CleanFullSprintData = FullSprintData.dropna(subset=["Issue Key"])

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([   

    html.Div([
        html.H1(children='CIBT Wave 2', className='title'),
        #html.Div(html.Img(src='./assets/AtradiusLogo.jpg', className="logo"), className='logoContainer')
    ], className='topBar'),

    dcc.Checklist(
        options=FullSprintData["Project Name"].unique(),
        value=FullSprintData["Project Name"].unique(),
        id='Squads',
    ),

    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(MinYear, MinMonth, MinDay),
        max_date_allowed=date(MaxYear, MaxMonth, MaxDay),
        initial_visible_month=date(MaxYear, MaxMonth, MaxDay),
        end_date=date(MaxYear, MaxMonth, MaxDay),
        start_date=date(MaxYear, MaxMonth-1, MaxDay)
    ),
    html.Div(id='output-container-date-picker-range'),

    html.Div([
        dcc.Graph(
            id='example-graph',
            className='graph_container'
        ),
        dcc.Graph(
            id='otro mas',
            className='graph_container'
        )
    ], className='container_status'),

    html.H1(
        id='a ver'
    ),

])

# ------------------------------------------------------------------------------

@app.callback(
    Output('example-graph', 'figure'),
    Output('output-container-date-picker-range', 'children'),
    Output('a ver', 'children'),
    Output('otro mas', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('Squads', 'value')
)
def DatePicker(start_date, end_date, SquadsValue):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    NoneFullSprintData = FullSprintData.where(pd.notnull(FullSprintData), None)
    FullSprintDataFilteredByDateRange = NoneFullSprintData[(NoneFullSprintData['Date Extracted'] >= start_date) & (NoneFullSprintData['Date Extracted'] <= end_date)]
    FullSprintDataFilteredByDateRangeAndSquads = FullSprintDataFilteredByDateRange[FullSprintDataFilteredByDateRange['Project Name'].isin(np.array(SquadsValue))]
    fig = px.pie(FullSprintDataFilteredByDateRangeAndSquads, values='Count(*)', names='Status', color_discrete_sequence=px.colors.sequential.RdBu)

    FilteredBlockedIssues = FullSprintDataFilteredByDateRangeAndSquads[FullSprintDataFilteredByDateRangeAndSquads['Status'].isin(['Blocked', 'Blocker/Waiting', 'Blocker'])]
    figure=px.histogram(FilteredBlockedIssues, x = 'Project Name', y = 'Count(*)', labels={'Project Name':'Squad', 'Count(*)': 'issue days where issues are blocked'}, color_discrete_sequence=px.colors.sequential.RdBu)
    figure.update_xaxes(categoryorder='total descending')
    

    picked_range = f'you have selected: Start Date: {start_date} | End Date: {end_date}'
    issues = f'Total number of issue days from these squads between these dates: {FullSprintDataFilteredByDateRangeAndSquads.shape[0] + 1}'
    return fig, picked_range, issues, figure



# ------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)