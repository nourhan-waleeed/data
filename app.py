import pandas as pd
import dash
from dash import Dash, dcc, Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output  # Import the necessary classes
import plotly.express as px
#import plotly.graph_objects as go  # Import go from plotly.graph_objects
import dash_table

category = pd.read_csv('https://drive.google.com/uc?export=download&id=1hDkvMLW32NPlt3GlbpyfkrSSp3g9tSNd')
dashboard = pd.read_csv('https://drive.google.com/uc?export=download&id=1y7Zu4IJaNKXn7mAuQqWfj2qPaHSRS4KO')
complaints_big = pd.read_csv('https://drive.google.com/uc?export=download&id=1NK52hyFiS9JbiRrgxZd4Mn1gA-87PiBB')
#complaints = pd.read_csv('elrehab_final_complaint.csv')

#dash.drop(columns=['Unnamed: 0'],inplace= True)
#complaints.drop(columns=['Unnamed: 0'],inplace= True)
#complaints_big.drop(columns=['Unnamed: 0'],inplace= True)
#category.drop(columns=['Unnamed: 0'],inplace= True)

category['duration'] = category['tenure']- category['recency_in_days']

one_visit_data = category[category['segments'] == 'One Visit']
monthly_purchases = one_visit_data.groupby('الشهر ')['segments'].count().reset_index()
dep = complaints_big.groupby(['Department','reason']).size().reset_index(name='count')
seg = category.groupby('segments').size().reset_index(name='count')

sales = category.groupby(['الشهر ','القسم السلعي'])['المشتريات'].sum().reset_index()

daily_payments = dashboard.groupby('اسم اليوم')['قيمه المشتريات'].sum().reset_index()
monthly_payments = dashboard.groupby('الشهر')['قيمه المشتريات'].sum().reset_index()
seasonality_payments = dashboard.groupby('فصول')['قيمه المشتريات'].sum().reset_index()

unique_segments = category.groupby("رقم العميل")["segments"].unique().reset_index()
segment_counts = unique_segments['segments'].value_counts().reset_index()
segment_counts = segment_counts.rename(columns={'segments': 'Segment', 'index': 'Count'})

category_dropdown_options = [{'label': category, 'value': category} for category in category['القسم السلعي'].unique()]
segments_dropdown_options = [{'label': segment, 'value': segment} for segment in seg['segments'].unique()]
comp_dropdown_options = [{'label': department, 'value': department} for department in dep['Department'].unique()]

merged_other = category[category['segments'].isin(['Champion', 'Need Attention','One Visit'])]
merged_loyal = category[category['segments']=='Loyal']
other_counts = merged_other.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')
loyal_counts = merged_loyal.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')

category_sum = category.groupby('القسم السلعي')['المشتريات'].sum().reset_index()
category_count = category.groupby('القسم السلعي')['المشتريات'].count().reset_index()
category_sum=category_sum.rename(columns={'المشتريات': 'قيمة المشتريات'})
category_count=category_count.rename(columns={'المشتريات': 'عدد المنتجات'})
category_merge=pd.merge(category_sum, category_count, on='القسم السلعي', how='inner')



app = dash.Dash(__name__)
server = app.server


app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'padding': '20px', 'background-color': '', 'text-align': 'right','color':'purple','font-size':'20px'}, children=[
    html.H1(children='فتح الله فرع الرحاب', style={'color': '#333', 'font-weight': 'bold','text-align': 'center','color':'purple','font-size':'50px'}),
    html.Hr(style={'border-top': '2px solid #999'}),
    dcc.RadioItems(
        options=[
            {'label': 'نسبة المبيعات على مدار فصول السنة', 'value': 'season'},
            {'label': 'نسبة المبيعات على مدار الاسبوع', 'value': 'days'},
            {'label': 'نسبة المبيعات على مدار الشهر', 'value': 'month'},
            {'label': 'عدد الزيارات ', 'value': 'freq'},
            {'label': 'معدل الشراء', 'value': 'معدل'}

        ],
        value='month',
        id='controls-and-radio-item',
        labelStyle={'display': 'block', 'margin-bottom': '10px', 'font-weight': 'bold', 'color': '#353'}
     ),
    
    
  html.Div([
          dcc.Graph(figure={}, id='controls-and-graph'),
      
       
            dcc.Graph(figure = px.bar(
            monthly_purchases,
            y='segments', x='الشهر ',
            color_discrete_sequence=px.colors.sequential.Viridis).
            update_layout(title='"One Visit" Segment by Month')),
            ], style={'display': 'flex', 'flex-direction': 'row'}),
    
           

      
   html.Div([
       
       dcc.Graph(figure= px.scatter(
           category,
           x='recency_in_days',
           y='tenure',
           color='segments',
           labels={
                     "recency_in_days":'اخر يوم اشترى فيه',
                     "tenure": "عدد الايام من اول زياره  "
                 },
           color_discrete_sequence=px.colors.sequential.Viridis
            ).update_layout(title='relation between recency & number of days')),

    
       dcc.Graph(figure = px.pie(
            segment_counts,
            values='Count', names='Segment',
            color_discrete_sequence=px.colors.sequential.Viridis).
            update_layout(title='تصنيف العملاء'))
            ], style={'display': 'flex', 'flex-direction': 'row'}),
    
    
    
    
    
        html.Div([
            dcc.Dropdown(
        id='segment-dropdown',
        options=segments_dropdown_options,
        multi=True,  # Allow for selecting multiple segments
        value=category['segments'].unique(),  # Default to all segments
        placeholder="Select segment(s)"
    ),
            
        dcc.Graph(id='segment-plot'),
  
            
        ]),
        dash_table.DataTable(
        id='segment-table',
        columns=[
            {'name': 'رقم العميل', 'id': 'رقم العميل'},
            {'name': 'عدد الزيارات', 'id': 'عدد الزيارات'},
            {'name': 'معدل الشراء', 'id': 'معدل الشراء'},
        ],
        data=[]
    ),
    
        
        html.Div([
            dcc.Dropdown(
        id='category-dropdown',
        options=category_dropdown_options,
        multi=True,  # Allow for selecting multiple segments
        value=category['القسم السلعي'].unique(),  # Default to all segments
        placeholder="Select Category"
    ),
    
        ]),
    
    html.Div([
        
           dcc.Graph(id='cat-plot1'),
          dcc.Graph(id='cat-plot2')],
        style={'display': 'flex', 'flex-direction': 'row'}),
    
   html.Div([
        
           dcc.Graph(id='cat-plot3'),
          dcc.Graph(id='cat-plot4')],
        style={'display': 'flex', 'flex-direction': 'row'}),        
    
            

        
    

        html.Div([

     dcc.Graph(
    figure = px.scatter(category, x='duration', y='عدد الزيارات', title='Scatter Plot of Duration vs. عدد الزيارات',size='معدل الشراء',color_discrete_sequence=px.colors.sequential.Viridis
).update_layout(
    xaxis_title='Duration',
    yaxis_title='عدد الزيارات',
    showlegend=False  
    ))

    ]),
    
    html.Div([
            html.Hr(style={'border-top': '3px solid #999'}),
            html.H1(children='شكاوي فرع الرحاب', style={'color': '#333', 'font-weight': 'bold','text-align': 'center','color':'purple','font-size':'30px'}),       
    ]),
    
    
            html.Div([
            dcc.Dropdown(
        id='comp-dropdown',
        options=comp_dropdown_options,
        multi=True,  # Allow for selecting multiple segments
        value=dep['Department'].unique(),  # Default to all segments
        placeholder="Select department(s)"
    ),
            
        dcc.Graph(id='comp-plot'),
  
            
        ])
    
    

])

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
            title='المبيعات على مدار فصول السنة'
            ,color_discrete_sequence=px.colors.sequential.Viridis
        )
    elif chosen_option == 'days':
        figure = px.bar(
            daily_payments,
            x='اسم اليوم',
            y='قيمه المشتريات',
            title='المبيعات على مدار الاسبوع'
            ,color_discrete_sequence=px.colors.sequential.Viridis
        )
    elif chosen_option == 'month':
        figure = px.line(
            monthly_payments,
            x='الشهر',
            y='قيمه المشتريات',
            title='المبيعات على مدار الشهر',
            color_discrete_sequence=px.colors.sequential.Viridis)
           #figure.update_layout(barmode='group', bargap=0.2)
            
    elif chosen_option == 'freq':

        figure = px.histogram(
            dashboard,
            x='عدد الزيارات',
            title='Box Plot of Frequency of Visits',
            color_discrete_sequence=px.colors.sequential.Viridis)


    elif chosen_option == 'معدل':

        figure = px.box(
            category,
            x='معدل الشراء',
            title='Box Plot of Frequency of Visits',
            color_discrete_sequence=px.colors.sequential.Viridis)
        

    return figure






@app.callback(
    Output('segment-plot', 'figure'),
    Input('segment-dropdown', 'value')
)
def update_segment_plot(selected_segments):
    if selected_segments:
        filtered_data = seg[seg['segments'].isin(selected_segments)]

        fig = px.bar(
            filtered_data,
            x='segments',
            y='count',
            title='Number of Customers by Segment',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        return fig
    return {}

@app.callback(
    Output('segment-table', 'data'),
    Input('segment-dropdown', 'value')
)
def update_segment_table(selected_segments):
    if selected_segments:
        selected_data = category[category['segments'].isin(selected_segments)][['رقم العميل', 'عدد الزيارات', 'معدل الشراء']]
        unique_data = selected_data.drop_duplicates(subset=['رقم العميل'])
        sorted_data = unique_data.sort_values(by=['عدد الزيارات','معدل الشراء'], ascending=[False,False])

        return sorted_data.head(10).to_dict('records')
    return []



@app.callback(
    Output('comp-plot', 'figure'),
    Input('comp-dropdown', 'value')
)



def update_comp_plot(selected_comp):
    if selected_comp:
        filtered_data = dep[dep['Department'].isin(selected_comp)]
        
        fig = px.bar(
            filtered_data,
            x='reason',  
            y='count',
            title='Number of Customers by Subcategory',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        
        return fig
    return {}



    
    
    
    
    
    
    
    
@app.callback(
    [Output('cat-plot1', 'figure'),Output('cat-plot2', 'figure'),Output('cat-plot3', 'figure'),Output('cat-plot4', 'figure')],
    Input('category-dropdown', 'value')
)



def update_comp_plot(selected_cat):
    if selected_cat:
        
        other_counts = merged_other.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')
        loyal_counts = merged_loyal.groupby(['segments', 'القسم السلعي']).size().reset_index(name='count')
        
        
        
        filtered_data = loyal_counts[loyal_counts['القسم السلعي'].isin(selected_cat)]
        filtered_data2 = other_counts[other_counts['القسم السلعي'].isin(selected_cat)]
        filtered_data3 = sales[sales['القسم السلعي'].isin(selected_cat)]
        filtered_data4 = category_merge[category_merge['القسم السلعي'].isin(selected_cat)]

        figure1 = px.bar(
            filtered_data,
            y='count', x='segments',color='القسم السلعي',
            color_discrete_sequence=px.colors.sequential.Viridis,
            title='Most Selling Categories for Loyal Segment')
            
        figure2 = px.bar(
            filtered_data2,
            y='count', x='segments',color='القسم السلعي',
            color_discrete_sequence=px.colors.sequential.Viridis
            ,title='Most Selling Categories for Other Segments')
        
        figure3 = px.line(
            filtered_data3,
            x='الشهر ', y='المشتريات',color='القسم السلعي',
            color_discrete_sequence=px.colors.sequential.Viridis)
        
        
        figure4 = px.bar(
            filtered_data4,
            x='القسم السلعي',
            y=['عدد المنتجات', 'قيمة المشتريات'],
            barmode='group',
            labels={'value': 'Value'},
            title='Comparison of Product Count and Purchase Value by Category',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        
        
        

        
        return figure1, figure2, figure3, figure4
    return {}, {}, {}, {}

 

if __name__ == '__main__':
    app.run_server(debug=True, port=8800)
