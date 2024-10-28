import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
file_path = 'C:\\Users\\CONNECT\\OneDrive\\Desktop\\project_dashbord\\players_statistics.csv'
# Load the data with the updated path
try:
    data = pd.read_csv(file_path, encoding='utf-8')
except UnicodeDecodeError:
    # If utf-8 fails, try ISO-8859-1 encoding
    try:
        data = pd.read_csv(file_path, encoding='ISO-8859-1')
    except UnicodeDecodeError:
        # If ISO-8859-1 fails, try latin1 encoding
        try:
            data = pd.read_csv(file_path, encoding='latin1')
        except UnicodeDecodeError:
            # Use chardet to detect the file encoding
            with open(file_path, 'rb') as file:
                result = chardet.detect(file.read())
                encoding = result['encoding']
                # Read the file using the detected encoding
                data = pd.read_csv(file_path, encoding=encoding)# Create a Dash application
app = dash.Dash(__name__)

# Define custom CSS styles
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

# Apply external stylesheets to the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Layout of the dashboard with custom styles
app.layout = html.Div(style={'backgroundColor': '#0a0606', 'fontFamily': 'Roboto'}, children=[
    html.H1('laliga Player Statistics ', style={'color': '#ffffff', 'textAlign': 'center'}),

    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': player, 'value': player} for player in data['player name'].unique()],
        value=data['player name'].unique()[0],
        style={'width': '50%', 'backgroundColor': '#05ab92', 'color': '#05ab92', 'border': '1px solid #ffffff'}
    ),

    html.Div(id='player-data', style={'color': '#ffffff'}),

    dcc.Graph(id='goals-per-match-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='pass-success-rate-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='player-performance-graph', style={'backgroundColor': '#1e1e1e'}),
    dcc.Graph(id='pass-heatmap-graph', style={'backgroundColor': '#1e1e1e'})  # Add graph for heatmap
])

@app.callback(
    Output('player-data', 'children'),
    Output('goals-per-match-graph', 'figure'),
    Output('pass-success-rate-graph', 'figure'),
    Output('player-performance-graph', 'figure'),
    Output('pass-heatmap-graph', 'figure'),  # Output for heatmap
    Input('player-dropdown', 'value')
)
def update_dashboard(selected_player):
    player_data = data[data['player name'] == selected_player].iloc[0]

    player_stats = [
        html.P(f"Player: {player_data['player name']}"),
        html.P(f"Team: {player_data['player team']}"),
        html.P(f"Minutes Played: {player_data['Minutes Played']}"),
        html.P(f"Matches: {player_data['Matches']}"),
        html.P(f"Goals: {player_data['goals']}"),
        html.P(f"Total Passes: {player_data['Total Passes']}"),
        html.P(f"Successful Passes: {player_data['Successful Passes']}")
    ]

    goals_per_match = player_data['goals'] / player_data['Matches']
    pass_success_rate = (player_data['Successful Passes'] / player_data['Total Passes']) * 100
    performance_score = (player_data['goals'] * 2 + pass_success_rate * 0.5 + player_data['Minutes Played'] / 500) / 10

    goals_per_match_fig = px.bar(
        x=['Goals per Match'], 
        y=[goals_per_match],
        labels={'x': '', 'y': 'Goals per Match'},
        title='Goals per Match',
        template='plotly_dark'
    )

    pass_success_rate_fig = px.pie(
        names=['Successful Passes', 'Unsuccessful Passes'],
        values=[player_data['Successful Passes'], player_data['Total Passes'] - player_data['Successful Passes']],
        title='Pass Success Rate',
        template='plotly_dark'
    )

    performance_fig = px.scatter(
        x=[player_data['Minutes Played']],
        y=[performance_score],
        labels={'x': 'Minutes Played', 'y': 'Performance Score'},
        title='Player Performance',
        size=[player_data['goals']],
        hover_name=[player_data['player name']],
        template='plotly_dark'
    )

    # Creating heatmap data
    passes_data = data[data['player name'] == selected_player]
    start_positions = passes_data['Pass Start Position'].str.strip('()').str.split(',', expand=True).astype(float)
    end_positions = passes_data['Pass End Position'].str.strip('()').str.split(',', expand=True).astype(float)

    heatmap_fig = go.Figure()

    # Adding pass start positions
    heatmap_fig.add_trace(go.Scatter(
        x=start_positions[0],
        y=start_positions[1],
        mode='markers',
        marker=dict(size=5, color='blue', opacity=0.5),
        name='Pass Start'
    ))

    # Adding pass end positions
    heatmap_fig.add_trace(go.Scatter(
        x=end_positions[0],
        y=end_positions[1],
        mode='markers',
        marker=dict(size=5, color='red', opacity=0.5),
        name='Pass End'
    ))

    heatmap_fig.update_layout(
        title='Heatmap of Player Passes',
        xaxis_title='Field X',
        yaxis_title='Field Y',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        showlegend=True,
        template='plotly_dark'
    )

    return player_stats, goals_per_match_fig, pass_success_rate_fig, performance_fig, heatmap_fig


if __name__ == '__main__':
    from waitress import serve
    serve(app.server, host='0.0.0.0', port=8000)

