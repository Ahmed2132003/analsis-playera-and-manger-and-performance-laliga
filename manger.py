import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from waitress import serve

# تحميل بيانات المدربين
file_path_coaches = 'C:\\Users\\CONNECT\\OneDrive\\Desktop\\project_dashbord\\la_liga_managers_2024.csv'
try:
    coach_data = pd.read_csv(file_path_coaches, encoding='utf-8')
except UnicodeDecodeError:
    try:
        coach_data = pd.read_csv(file_path_coaches, encoding='ISO-8859-1')
    except UnicodeDecodeError:
        try:
            coach_data = pd.read_csv(file_path_coaches, encoding='latin1')
        except UnicodeDecodeError:
            with open(file_path_coaches, 'rb') as file:
                import chardet
                result = chardet.detect(file.read())
                encoding = result['encoding']
                coach_data = pd.read_csv(file_path_coaches, encoding=encoding)

# إعداد تطبيق Dash
external_stylesheets = [
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8sh+wyZ3B/cEYLxtY0QoZsibTNF5IT8+9ePLZB',
        'crossorigin': 'anonymous'
    },
    {
        'href': 'https://fonts.googleapis.com/css2?family=Roboto&display=swap',
        'rel': 'stylesheet'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# واجهة المستخدم لتطبيق Dash
app.layout = html.Div(style={'backgroundColor': '#0a0606', 'fontFamily': 'Roboto'}, children=[
    html.H1('La Liga Coach Statistics Dashboard', style={'color': '#ffffff', 'textAlign': 'center'}),
    
    dcc.Dropdown(
        id='coach-dropdown',
        options=[{'label': manager, 'value': manager} for manager in coach_data['Manager'].unique()],
        value=coach_data['Manager'].unique()[0],
        style={'width': '50%', 'backgroundColor': '#05ab92', 'color': '#05ab92', 'border': '1px solid #ffffff', 'marginTop': '20px'}
    ),
    html.Div(id='coach-data', style={'color': '#ffffff'}),
    dcc.Graph(id='win-rate-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='goals-per-match-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='offensive-performance-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='defensive-performance-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='overall-performance-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='ranking-graph', style={'backgroundColor': '#1e1e1e'}),
    html.Div(id='preferred-formation', style={'color': '#ffffff'})
])

# دالة لتحليل إحصائيات المدربين
def get_coach_statistics(selected_coach):
    coach_data_selected = coach_data[coach_data['Manager'] == selected_coach].iloc[0]
    coach_stats = [
        html.P(f"Manager: {coach_data_selected['Manager']}"),
        html.P(f"Team: {coach_data_selected['Team']}"),
        html.P(f"Matches: {coach_data_selected['Matches']}"),
        html.P(f"Wins: {coach_data_selected['Wins']}"),
        html.P(f"Draws: {coach_data_selected['Draws']}"),
        html.P(f"Losses: {coach_data_selected['Losses']}"),
        html.P(f"Goals Scored: {coach_data_selected['Goals Scored']}"),
        html.P(f"Goals Conceded: {coach_data_selected['Goals Conceded']}"),
        html.P(f"Trophies: {coach_data_selected['Trophies']}")
    ]

    return coach_stats

# دالة لحساب نسبة الفوز
def calculate_win_rate(coach_data_selected):
    matches = coach_data_selected['Matches']
    wins = coach_data_selected['Wins']
    if matches > 0:
        win_rate = (wins / matches) * 100
    else:
        win_rate = 0
    return win_rate

# دالة لحساب متوسط الأهداف المسجلة والمستقبلة لكل مباراة
def calculate_goals_per_match(coach_data_selected):
    matches = coach_data_selected['Matches']
    goals_scored = coach_data_selected['Goals Scored']
    goals_conceded = coach_data_selected['Goals Conceded']
    if matches > 0:
        goals_scored_per_match = goals_scored / matches
        goals_conceded_per_match = goals_conceded / matches
    else:
        goals_scored_per_match = 0
        goals_conceded_per_match = 0
    return goals_scored_per_match, goals_conceded_per_match

# دالة لتقييم الأداء الهجومي
def calculate_offensive_performance(goals_scored_per_match):
    if goals_scored_per_match > 1.5:
        offensive_score = 6 + (goals_scored_per_match - 1.5) * 2.67
    else:
        offensive_score = 6 * (goals_scored_per_match / 1.5)
    offensive_score = min(offensive_score, 10)
    return offensive_score

# دالة لتقييم الأداء الدفاعي
def calculate_defensive_performance(goals_conceded_per_match):
    if goals_conceded_per_match < 1.5:
        defensive_score = 5 + (1.5 - goals_conceded_per_match) * 3.33
    else:
        defensive_score = 5 - (goals_conceded_per_match - 1.5) * 3.33
    defensive_score = max(defensive_score, 0)
    return defensive_score

# دالة لتقييم الأداء العام للمدرب
def calculate_overall_performance(win_rate, offensive_score, defensive_score):
    overall_score = (win_rate * 0.4 + offensive_score * 0.3 + defensive_score * 0.3) / 10
    return overall_score

# دالة لعرض ترتيب المدرب
def calculate_ranking(coach_data, selected_coach):
    coach_data['Win Rate'] = coach_data.apply(lambda row: (row['Wins'] / row['Matches']) * 100 if row['Matches'] > 0 else 0, axis=1)
    coach_data['Goals per Match'] = coach_data.apply(lambda row: row['Goals Scored'] / row['Matches'] if row['Matches'] > 0 else 0, axis=1)
    coach_data['Offensive Score'] = coach_data.apply(lambda row: calculate_offensive_performance(row['Goals per Match']), axis=1)
    coach_data['Defensive Score'] = coach_data.apply(lambda row: calculate_defensive_performance(row['Goals Conceded'] / row['Matches'] if row['Matches'] > 0 else 0), axis=1)
    coach_data['Overall Score'] = coach_data.apply(lambda row: calculate_overall_performance(row['Win Rate'], row['Offensive Score'], row['Defensive Score']), axis=1)

    selected_coach_score = coach_data[coach_data['Manager'] == selected_coach]['Overall Score'].values[0]
    ranking = coach_data[coach_data['Overall Score'] >= selected_coach_score].shape[0]

    return ranking, coach_data.sort_values(by='Overall Score', ascending=False)

# تعريف الكول باك لتحديث البيانات
@app.callback(
    Output('coach-data', 'children'),
    Output('win-rate-graph', 'figure'),
    Output('goals-per-match-graph', 'figure'),
    Output('offensive-performance-graph', 'figure'),
    Output('defensive-performance-graph', 'figure'),
    Output('overall-performance-graph', 'figure'),
    Output('ranking-graph', 'figure'),
    Output('preferred-formation', 'children'),
    Input('coach-dropdown', 'value')
)
def update_dashboard(selected_coach):
    coach_data_selected = coach_data[coach_data['Manager'] == selected_coach].iloc[0]

    coach_stats = get_coach_statistics(selected_coach)
    
    win_rate = calculate_win_rate(coach_data_selected)
    win_rate_fig = px.pie(
    values=[win_rate, 100 - win_rate],
    names=['Win Rate', ''],
    labels={'': 'Percentage'},
    title='Win Rate',
    template='plotly_dark',
    )
    win_rate_fig.update_traces(marker=dict(colors=['#05ab92', '#1e1e1e'], line=dict(color='#ffffff', width=2)))  # تحديث ألوان القطاعات والحواف

    # إعداد التخطيط والعرض
    win_rate_fig.update_layout(
    showlegend=False,  # عدم عرض مفتاح الشرح
    uniformtext_minsize=12,  # حجم النص بالحجم الأدنى
    uniformtext_mode='hide'  # إخفاء النصوص المكررة
    )
    #تغيير لون الشريط

    
    goals_scored_per_match, goals_conceded_per_match = calculate_goals_per_match(coach_data_selected)
    goals_per_match_fig = go.Figure(data=[
        go.Bar(name='Goals Scored per Match', x=['Goals per Match'], y=[goals_scored_per_match], marker_color='green'),
        go.Bar(name='Goals Conceded per Match', x=['Goals per Match'], y=[goals_conceded_per_match], marker_color='red')
    ])
    goals_per_match_fig.update_layout(barmode='group', title='Goals per Match', template='plotly_dark')
    
    offensive_performance = calculate_offensive_performance(goals_scored_per_match)
    offensive_performance_fig = go.Figure(go.Indicator(
    mode='gauge+number',
    value=offensive_performance,
    title='Offensive Performance',
    gauge={'axis': {'range': [0, 10]},
           'bar': {'color': '#05ab92'}}
    ))
    offensive_performance_fig.update_layout(paper_bgcolor='#1e1e1e')

    # عرض الرسم البياني
    defensive_performance = calculate_defensive_performance(goals_conceded_per_match)

    defensive_performance_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=defensive_performance,
        title={'text': "Defensive Performance", 'font': {'color': '#ffffff'}},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': '#05ab92'},
            'bgcolor': '#1e1e1e',
            'steps': [
                {'range': [0, 4], 'color': '#ff6666'},
                {'range': [4, 7], 'color': '#ffa64d'},
                {'range': [7, 10], 'color': '#66ff66'}
            ]
        }
    ))

# تحديث تخطيط وعرض الشكل البياني
    defensive_performance_fig.update_layout(
        template='plotly_dark',
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )

# عرض الشكل البياني
    defensive_performance_fig.show()

    
    overall_performance = calculate_overall_performance(win_rate, offensive_performance, defensive_performance)
    overall_performance_fig = px.bar(
        x=['Overall Performance'],
        y=[overall_performance],
        labels={'x': '', 'y': 'Score'},
        title='Overall Performance',
        template='plotly_dark'
    )
    
    ranking, sorted_coach_data = calculate_ranking(coach_data, selected_coach)
    ranking_fig = px.bar(
        x=sorted_coach_data['Manager'],
        y=sorted_coach_data['Overall Score'],
        labels={'x': 'Manager', 'y': 'Overall Score'},
        title='Coach Rankings',
        template='plotly_dark'
    )
    
    formation = html.Div([
        html.P(f"Goalkeeper: {coach_data_selected['Goalkeeper']}"),
        html.P(f"Defenders: {coach_data_selected['Defenders']}"),
        html.P(f"Midfielders: {coach_data_selected['Midfielders']}"),
        html.P(f"Forwards: {coach_data_selected['Forwards']}")
    ])
    
    return coach_stats, win_rate_fig, goals_per_match_fig, offensive_performance_fig, defensive_performance_fig, overall_performance_fig, ranking_fig, formation

if __name__ == '__main__':
    serve(app.server, host='0.0.0.0', port=8000)
