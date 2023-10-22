import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load your data
merge = pd.read_csv('https://drive.google.com/uc?export=download&id=1y7Zu4IJaNKXn7mAuQqWfj2qPaHSRS4KO')

# Calculate required dataframes
daily_payments = merge.groupby('اسم اليوم')['قيمه المشتريات'].sum().reset_index()
monthly_payments = merge.groupby('الشهر')['قيمه المشتريات'].sum().reset_index()
seasonality_payments = merge.groupby('فصول')['قيمه المشتريات'].sum().reset_index()

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={'font-family': 'Arial, sans-serif', 'padding': '20px', 'background-color': '#F0F3F5', 'direction': 'rtl'},
    children=[
        html.H1(children='فتح الله فرع الرحاب', style={'color': '#333', 'font-weight': 'bold'}),
        html.Hr(style={'border-top': '2px solid #999'}),
        dcc.RadioItems(
            options=[
                {'label': 'نسبة المبيعات على مدار فصول السنة', 'value': 'season'},
                {'label': 'نسبة المبيعات على مدار الاسبوع', 'value': 'days'},
                {'label': 'نسبة المبيعات على مدار الشهر', 'value': 'month'}
            ],
            value='season',
            id='controls-and-radio-item',
            labelStyle={'display': 'block', 'margin-bottom': '10px', 'font-weight': 'bold', 'color': '#353'}
        ),
        html.Div([
            dcc.Graph(figure={}, id='controls-and-graph')
        ]),
        html.Div([
            dcc.Graph(
                figure=px.scatter(
                    merge,
                    x='recency_in_days',
                    y='tenure',
                    color='عدد الزيارات',
                    labels={
                        "recency_in_days": "عدد الأيام لغاية آخر زيارة",
                        "tenure": "عدد الأيام من أول زيارة لغاية اليوم"
                    },
                    color_discrete_sequence=px.colors.sequential.Viridis
                ).update_layout(title='العلاقة بين الأيام والزيارات')
            ),
        ]),
    ]
)

@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(chosen_option):
    if chosen_option == 'season':
        figure = px.bar(
            seasonality_payments,
            x='فصول',
            y='قيمه المشتريات',
            title='المبيعات على مدار فصول السنة',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
    elif chosen_option == 'days':
        figure = px.bar(
            daily_payments,
            x='اسم اليوم',
            y='قيمه المشتريات',
            title='المبيعات على مدار الأسبوع',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
    elif chosen_option == 'month':
        figure = px.line(
            monthly_payments,
            x='الشهر',
            y='قيمه المشتريات',
            title='المبيعات على مدار الشهر',
            color_discrete_sequence=px.colors.sequential.Viridis
        )

    return figure

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
