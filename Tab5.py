import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Load the dataset
df = pd.read_csv(r"C:\r data sets\energy.csv")

# Define seasons
def season(month):
    season_month = {
        12: 'Summer', 1: 'Summer', 2: 'Summer',
        3: 'Autumn', 4: 'Autumn', 5: 'Autumn',
        6: 'Winter', 7: 'Winter', 8: 'Winter',
        9: 'Spring', 10: 'Spring', 11: 'Spring'
    }
    return season_month.get(month)

df['season'] = df['month'].apply(season)
# Pre-process the data to calculate average demand year and month-wise
average_demand_data = df.groupby(['year', 'month'])['demand'].mean().reset_index()
# Calculate average RRP and demand for each season and year
avg_data = df.groupby(["season", "year"]).agg({"RRP": "mean", "demand": "mean"}).reset_index()
# Group data by season and year, calculating average demand, max temp, and min temp
season_year_data = df.groupby(['season', 'year']).agg({
    'demand': 'mean',
    'max_temperature': 'max',
    'min_temperature': 'min'
}).reset_index()



# Convert the "date" column to datetime format for proper filtering
df['date'] = pd.to_datetime(df['date'])

# Create the Dash application
app = dash.Dash(title="Data Visualization")

# Define the layout of the application
# Define the layout of the application
app.layout = html.Div([
    html.H1("Australia Victoria Energy Data Visualization 2015-2020"),
    dcc.Tabs(id="tabs", value="tab-0", children=[
        dcc.Tab(label="Introduction", value="tab-0", children=[
            html.Div([
                html.Div([
                   html.Img(
    src="https://assets.nationbuilder.com/icf/pages/195/attachments/original/1482432025/melbourne-victoria-australia.jpg?1482432025",
    alt="Melbourne, Victoria",
    style={'width': '100%', 'height': '500px'}
),

                    
                    html.H2("Understanding the Impact of Seasonal Changes on Victoria's Energy Demand"),
html.H5("The Victoria Energy Visualization application takes into account the dynamic relationship between seasonal changes and energy demand. Victoria, Australia, experiences distinct seasons — summer (December to February), autumn (March to May), winter (June to August), and spring (September to November)."),
html.H5("Exploring the visualizations, you can analyze how energy demand fluctuates in response to varying weather conditions throughout the year. Seasonal changes play a crucial role in shaping the energy landscape, and this application provides insights for effective energy planning."),


                    html.A("Australia Weather Information", href="https://www.australia.com/en/facts-and-planning/weather-in-australia.html"),
                ]),  # Adjust text color to ensure readability on the background
            ]),
        ]),
        dcc.Tab(label="Line Chart", value="tab-1", children=[
            html.H3("Line Chart"),
            html.Div([
                html.Label("Select Variable:"),
                dcc.Dropdown(
                    id="line-variable-dropdown",
                    options=[
                        {"label": "Demand", "value": "demand"},
                        {"label": "RRP", "value": "RRP"},
                        {"label": "Solar Exposure", "value": "solar_exposure"},
                    ],
                    value="demand", style={'padding': '10px'}
                ),
                html.Br(),
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id="line-date-range-picker",
                    start_date=df["date"].min(),
                    end_date=df["date"].max(),
                ),
            ]),
            dcc.Graph(id="line-chart"),
        ]),
        dcc.Tab(label="Scatter Plot", value="tab-2", children=[
            html.H3("Scatter Plot"),
            html.Label("Select Variable:"),
            dcc.RadioItems(
                id="variable-radio",
                options=[
                    {"label": "Max Temperature", "value": "max_temperature"},
                    {"label": "Month", "value": "month"},
                    {"label": "Rainfall", "value": "rainfall"},
                    {"label": "Min Temperature", "value": "min_temperature"},
                ],
                value="max_temperature",
            ),
            dcc.Graph(id="scatter-plot"),
        ]),
        dcc.Tab(label='Interactive Charts', value="tab-3", children=[
            html.H3('Interactive Charts'),
            html.Div([
                # Chart 1 (Box Plot)
                dcc.Graph(
                    id='chart1',
                    figure=px.box(df, x='month', y='demand', color='season'),
                    style={'display': 'inline-block', 'width': '140%'},
                ),
                # Chart 2 (Line Chart)
                dcc.Graph(
                    id='chart2',
                    figure=px.line(df, x='month', y='demand', color='season'),
                    config={'displayModeBar': False},
                    style={'display': 'inline-block', 'width': '100%','height':'20%'},
                )
            ], style={'display': 'flex'}),
        ]),
        dcc.Tab(label="Energy Data Analysis", value="tab-4", children=[
            html.H3("Energy Data Analysis"),
            html.Label("Select Year Range:"),
            dcc.RangeSlider(
                id="year-range-slider",
                min=2015,
                max=2020,
                step=1,
                value=[2015, 2020],
                marks={year: str(year) for year in range(2015, 2021)},
            ),
            html.Div(
                [
                    dcc.Graph(id="demand-chart"),
                    dcc.Graph(id="max-temp-chart"),
                    dcc.Graph(id="min-temp-chart"),
                ],
                style={'display': 'flex', 'flex-direction': 'row'}
            ),
        ])
    ]),
    html.Div("Pasindu Perera - COHNDDS-231F-023", className="name-tag"),
])



# Define the callback function for the line chart
@app.callback(
    Output("line-chart", "figure"),
    Input("line-variable-dropdown", "value"),
    Input("line-date-range-picker", "start_date"),
    Input("line-date-range-picker", "end_date"),
)
def update_line_chart(variable, start_date, end_date):
    # Convert the start_date and end_date to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the dataframe based on the selected date range and variable
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df[variable],
            mode="lines",
            name=variable,
        )
    )

    fig.update_layout(
        title="Line Chart",
        xaxis_title="Date",
        yaxis_title=variable,
        showlegend=True,
        legend_title="Variable",
        height=500,
       
    )

    return fig

@app.callback(
    Output("scatter-plot", "figure"),
    Input("variable-radio", "value"),
)
def update_scatter_plot(selected_variable):
    x_variable = "demand"  

    fig = go.Figure(data=go.Scatter(x=df[x_variable], y=df[selected_variable], mode='markers'))
    correlation = df[x_variable].corr(df[selected_variable])
    fig.update_layout(
        title=f"Scatter Plot ({x_variable} vs {selected_variable}) - Correlation: {correlation:.2f}",
        xaxis_title=x_variable,
        yaxis_title=selected_variable,
        height=500,
       
    )
    return fig
# Callback function to update line chart based on box plot click
@app.callback(
    Output('chart2', 'figure'),
    Input('chart1', 'clickData')
)

def update_line_chart(click_data):
    if click_data:
        x_val = click_data['points'][0]['x']
        filtered_data = average_demand_data[average_demand_data['month'] == x_val]
        modified_fig = px.line(filtered_data, x='year', y='demand', title=f'Average Demand for Month {x_val}')
       
        return modified_fig
    else:
        return px.line(average_demand_data, x='month', y='demand',color='year' ,title='Average Demand Over Time')
# Define callback to update charts based on year range selection
@app.callback(
    [Output("demand-chart", "figure"),
     Output("max-temp-chart", "figure"),
     Output("min-temp-chart", "figure")],
    [Input("year-range-slider", "value")]
)
def update_charts(year_range):
    selected_data = season_year_data[(season_year_data["year"] >= year_range[0]) & (season_year_data["year"] <= year_range[1])]

    # Set the height and width for smaller charts
    chart_height = 500
    chart_width = 700

    demand_fig = px.line(
        selected_data,
        x='season',
        y='demand',
        color='year',
        title='Average Demand by Season and Year',
        labels={'y': 'Average Demand', 'x': 'Season'},
        height=chart_height,
        width=chart_width
    )

    max_temp_fig = px.line(
        selected_data,
        x='season',
        y='max_temperature',
        color='year',
        title='Maximum Temperature by Season and Year',
        labels={'y': 'Maximum Temperature', 'x': 'Season'},
        height=chart_height,
        width=chart_width
    )

    min_temp_fig = px.line(
        selected_data,
        x='season',
        y='min_temperature',
        color='year',
        title='Minimum Temperature by Season and Year',
        labels={'y': 'Minimum Temperature', 'x': 'Season'},
        height=chart_height,
        width=chart_width
    )
    return demand_fig, max_temp_fig, min_temp_fig
# Run the application
if __name__ == "__main__":
    app.run_server(port=7777)
