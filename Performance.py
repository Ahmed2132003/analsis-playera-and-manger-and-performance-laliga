import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import re

# ملفات البيانات
csv_file_path = 'C:\\Users\\CONNECT\\OneDrive\\Desktop\\project_dashbord\\Performance Analysts.csv'
formation_file_path = 'C:\\Users\\CONNECT\\OneDrive\\Desktop\\teams.txt'

# قراءة ملف CSV
data = pd.read_csv(csv_file_path)

# قراءة التشكيلات من ملف TXT
with open(formation_file_path, 'r') as file:
    formations = file.readlines()

# تحويل البيانات
formations_dict = {}
for line in formations:
    match = re.match(r"Team: (.*) - Formation: (.*)", line.strip())
    if match:
        team = match.group(1).strip()
        formation = match.group(2).strip()
        formations_dict[team] = formation

def calculate_attack_performance(goals_scored):
    if goals_scored >= 1.5:
        return 6 + (goals_scored - 1.5) * 2
    else:
        return 6 - (1.5 - goals_scored) * 2

def calculate_defense_performance(goals_conceded):
    if goals_conceded <= 1.5:
        return 5 + (1.5 - goals_conceded) * 2
    else:
        return 5 - (goals_conceded - 1.5) * 2

# إعداد تطبيق Dash
app = dash.Dash(__name__)

# واجهة المستخدم
app.layout = html.Div(style={'backgroundColor': '#0a0606', 'fontFamily': 'Roboto'}, children=[
    html.H1('Performance Analyst Dashboard', style={'color': '#ffffff', 'textAlign': 'center'}),

    dcc.Dropdown(
        id='analyst-dropdown',
        options=[{'label': analyst, 'value': analyst} for analyst in data['Performance Analyst'].unique()],
        value=data['Performance Analyst'].unique()[0],
        style={'width': '50%', 'backgroundColor': '#05ab92', 'color': '#05ab92', 'border': '1px solid #ffffff'}
    ),

    html.Div(id='analyst-data', style={'color': '#ffffff'}),
    dcc.Graph(id='goals-chart', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='pass-chart', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='penalty-chart', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='set-piece-chart', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='attack-performance-chart', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='defense-performance-chart', style={'backgroundColor': '#1e1e1e'}),
    html.Div(id='preferred-formation', style={'color': '#ffffff'}),
])

@app.callback(
    Output('analyst-data', 'children'),
    Output('goals-chart', 'figure'),
    Output('pass-chart', 'figure'),
    Output('penalty-chart', 'figure'),
    Output('set-piece-chart', 'figure'),
    Output('attack-performance-chart', 'figure'),
    Output('defense-performance-chart', 'figure'),
    Output('preferred-formation', 'children'),
    Input('analyst-dropdown', 'value')
)
def update_dashboard(selected_analyst):
    analyst_data = data[data['Performance Analyst'] == selected_analyst]

    if analyst_data.empty:
        return [
            html.P("No data available for the selected analyst.")
        ], go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), "No formation available"

    team_stats = []
    for _, row in analyst_data.iterrows():
        team_stats.extend([
            html.P(f"Team: {row['Team']}"),
            html.P(f"Goals Scored: {row['Goals Scored']}"),
            html.P(f"Goals Conceded: {row['Goals Conceded']}"),
            html.P(f"Top Scorer: {row['Top Scorer (Goals)']} (Goals: {row['Top Scorer (Goals)']})"),
            html.P(f"Top Clean Sheet Keeper: {row['Top Clean Sheet Keeper (Clean Sheets)']} (Clean Sheets: {row['Top Clean Sheet Keeper (Clean Sheets)']})"),
            html.P(f"Passes Attempted: {row['Passes Attempted']}"),
            html.P(f"Passes Completed: {row['Passes Completed']}"),
            html.P(f"Set Kick Goals: {row['Set Piece Goals']}"),
            html.P(f"Penalties Granted: {row['Penalties Awarded']}"),
            html.P(f"Penalty Goals: {row['Penalty Goals']}")
        ])

    goals_chart = go.Figure(data=[
        go.Bar(name='Goals Scored', x=analyst_data['Team'], y=analyst_data['Goals Scored']),
        go.Bar(name='Goals Conceded', x=analyst_data['Team'], y=analyst_data['Goals Conceded'])
    ])
    goals_chart.update_layout(title='Goals Analysis', barmode='group', template='plotly_dark')

    pass_chart = go.Figure(data=[
        go.Pie(labels=['Passes Completed', 'Passes Missed'], 
               values=[analyst_data['Passes Completed'].sum(), 
                       analyst_data['Passes Attempted'].sum() - analyst_data['Passes Completed'].sum()])
    ])
    pass_chart.update_layout(title='Pass Completion Rate', template='plotly_dark')

    penalty_chart = go.Figure(data=[
        go.Pie(labels=['Penalty Goals', 'Missed Penalties'], 
               values=[analyst_data['Penalty Goals'].sum(), 
                       analyst_data['Penalties Awarded'].sum() - analyst_data['Penalty Goals'].sum()])
    ])
    penalty_chart.update_layout(title='Penalty Performance', template='plotly_dark')

    set_piece_goals = analyst_data['Set Piece Goals'].sum()
    other_goals = analyst_data['Goals Scored'].sum() - set_piece_goals

    set_piece_chart = go.Figure(data=[
        go.Bar(y=['Set Piece Goals', 'Other Goals'], 
               x=[set_piece_goals, other_goals], 
               orientation='h')
    ])
    set_piece_chart.update_layout(title='Set Piece Goals Analysis', template='plotly_dark')

    attack_performance_scores = []
    attack_performance_chart = go.Figure()
    for _, row in analyst_data.iterrows():
        attack_rating = calculate_attack_performance(row['Goals Scored'])
        attack_performance_scores.append(html.P(f"Attack Performance Rating for {row['Team']}: {attack_rating:.2f} / 10"))

        attack_performance_chart.add_trace(go.Indicator(
            mode="number",
            value=attack_rating,
            title=f"Attack Performance for {row['Team']}",
            domain={'row': 0, 'column': 0}
        ))
    attack_performance_chart.update_layout(template='plotly_dark', grid={'rows': 1, 'columns': len(analyst_data)})

    defense_performance_scores = []
    defense_performance_chart = go.Figure()
    for _, row in analyst_data.iterrows():
        defense_rating = calculate_defense_performance(row['Goals Conceded'])
        defense_performance_scores.append(html.P(f"Defense Performance Rating for {row['Team']}: {defense_rating:.2f} / 10"))

        defense_performance_chart.add_trace(go.Indicator(
            mode="number",
            value=defense_rating,
            title=f"Defense Performance for {row['Team']}",
            domain={'row': 0, 'column': 0}
        ))
    defense_performance_chart.update_layout(template='plotly_dark', grid={'rows': 1, 'columns': len(analyst_data)})

    team_formation_texts = []
    for team in analyst_data['Team']:
        formation_text = f"Preferred Formation for {team}: {formations_dict.get(team, 'No formation available')}"
        team_formation_texts.append(html.P(formation_text))
    
    return team_stats, goals_chart, pass_chart, penalty_chart, set_piece_chart, attack_performance_chart, defense_performance_chart, html.Div(team_formation_texts)

# Run the server using waitress
if __name__ == '__main__':
    from waitress import serve
    serve(app.server, host='0.0.0.0', port=8000)
