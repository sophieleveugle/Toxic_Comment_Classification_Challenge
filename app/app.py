# Dash dependencies
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

external_stylesheets = [dbc.themes.BOOTSTRAP]

#Model dependencies
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import plotly
import plotly.graph_objects as go


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

def load_models():
    # Load my pre-trained Keras model
    global model, tokenizer
    model = load_model('model.h5')
    # load my original tokenizer used to build model
    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    return model, tokenizer

model, tokenizer = load_models()

def prepare_text(text):
    '''Need to Tokenize text and pad sequences'''
    words = tokenizer.texts_to_sequences(text)
    words_padded = pad_sequences(words, maxlen = 150)

    return words_padded

# Initialize plot
fig = go.Figure(
                data=[go.Bar(x=["Toxic", "Severe toxic", "Obscene", "Threat", "Insult", "Identity hate"], 
                            y=[0, 0, 0, 0, 0, 0], 
                            marker=dict(color="#673EF1"),
                            width=[0.4]*6)],
                layout=go.Layout(
                    title=go.layout.Title(text="Your comment is...", font=dict(size=20)),
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(
                        family='Source Sans Pro'
                    ),
                    xaxis=dict(
                        tickfont=dict(size=16)
                    ),
                    yaxis=dict(
                        title_text="Probability",
                        tickmode="array",
                        tickfont=dict(size=16),
                        range=[0, 1]
                    ),
                    margin=dict(
                        b=100,
                        t=30,
                    ),
                    title_x=0.5
                )
            )

# Layout of the app
app.layout = html.Div(children=[
    html.Div(children=[
        html.Img(
            src='assets/eyes.gif',
            style={
                'width': '200px'
            })
        ], style={'textAlign': 'center', 'backgroundColor': '#000000'}),
    html.H1("The Toxic Comment Agent"),
    
    html.Div("Discussing things you care about can be difficult. The threat of abuse and harassment online means that many people stop expressing themselves and give up on seeking different opinions. This tool uses a multi-label model that can detect the type of toxicity of a comment.",
    style={'textAlign': 'center', 'margin-bottom': '40px', 'margin-left': '300px', 'margin-right': '300px'}),   
    
    html.H2("Enter a comment below and I'll predict what I think about it",  style={'fontSize': 24}),
    html.Div(children=[
        html.Img(
            src='assets/arrow.gif',
            style={
                'width': '50px'
            })
        ], style={'textAlign': 'center', 'margin-bottom': '20px'}),

    # Block of the text area
    html.Div(children=[
        dcc.Textarea(id = 'comment', value = '', style={'width': '50%', 'rows': '5'})
    ], style={'textAlign': 'center'}),

    # Check button
    html.Div(children=[
        html.Button(id = 'submit-button', n_clicks = 0, children = 'Check', className='button-submit')
    ], style={'textAlign': 'center', 'fontSize': 22, 'height': '100px', 'margin-bottom': '0px'}),

    # Display graph
    dcc.Graph(id='update-chart', figure=fig, style={
        'height': 300,
        'width': 700,
        "display": "block",
        "margin-left": "auto",
        "margin-right": "auto",
    }),

    html.Div([
        # About this project
        html.H2("About this project", style={'fontSize': 28, 'color': '#673EF1'}),
        html.Div('This predictive tool was built as part of a student project during our Post Master degree in Big Data at Télécom Paris. The data used to build the tool are from the Kaggle "Toxic Comment Classification Challenge" organized by Jigsaw and Conversation AI.',
        style={'textAlign': 'center', 'margin-left': '300px', 'margin-right': '300px', 'margin-top': '30px', 'margin-bottom': '30px'}),
        html.Div(children=[
            html.A([html.Img(src='assets/github-icon.png', style={'width': '30px'})], href='https://github.com/camillecochener/Toxic_comment_classification_challenge')
        ],
        style={'textAlign': 'center', 'margin-bottom': '40px'}),
        
        # About us
        html.H2("About us", style={'fontSize': 28, 'color': '#673EF1'}),
        html.Div(children=[
        dbc.Row([
            dbc.Col(html.Img(src='assets/camille.png', style={'width': '100px', 'margin-left': '10px', 'margin-right': '10px'})),
            dbc.Col(html.Img(src='assets/hamza.png', style={'width': '100px', 'margin-left': '10px', 'margin-right': '10px'})),
            dbc.Col(html.Img(src='assets/sophie.png', style={'width': '100px', 'margin-left': '10px', 'margin-right': '10px'})),
            dbc.Col(html.Img(src='assets/rodolphe.png', style={'width': '100px', 'margin-left': '10px', 'margin-right': '10px'}))
        ]),
        dbc.Row([
            dbc.Col(html.Div("Camille COCHENER", style={'margin-left': '10px', 'margin-right': '10px'})),
            dbc.Col(html.Div("Hamza AMRI", style={'margin-left': '10px', 'margin-right': '10px'})),
            dbc.Col(html.Div("Sophie LEVEUGLE", style={'margin-left': '10px', 'margin-right': '10px'})),
            dbc.Col(html.Div("Rodolphe SIMONEAU", style={'margin-left': '10px', 'margin-right': '10px'})),
        ])
        ], style={'textAlign': 'center', 'height': '100px', 'margin-left':'300px', 'margin-right': '300px', 'margin-top': '30px', 'margin-bottom': '30px'}), 
        html.Div('© Copyright TheToxicCommentAgent', style={'textAlign': 'center', 'margin-top': '40px'})
    ], style={'backgroundColor': '#F6F6F6'}) 
    
])

@app.callback(Output('update-chart', 'figure'),
    [Input('submit-button', 'n_clicks')],   
    [State('comment', 'value')])
def predict_text(submit, comment):
    if comment is '':
        empty_fig = go.Figure(
                data=[go.Bar(x=["Toxic", "Severe toxic", "Obscene", "Threat", "Insult", "Identity hate"], 
                            y=[0, 0, 0, 0, 0, 0],
                            marker=dict(color="#673EF1"),
                            width=[0.4]*6)],
                layout=go.Layout(
                    title=go.layout.Title(text="Your comment is...", font=dict(size=20)),
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(
                        family='Source Sans Pro'
                    ),
                    xaxis=dict(
                        tickfont=dict(size=16)
                    ),
                    yaxis=dict(
                        title_text="Probability",
                        tickmode="array",
                        tickfont=dict(size=16),
                        range=[0, 1]
                    ),
                    margin=dict(
                        b=100,
                        t=30,
                    ),
                    title_x=0.5
                )
            )
        return empty_fig
    else:
        try:
            clean_text = prepare_text([comment])
            preds = model.predict(clean_text)
            print(preds[0])
            yvalue = [i for i in preds[0]]
            return fig.update_traces(y=yvalue)
        except ValueError as e:
            print(e)
            return "The text area is empty."

if __name__ == '__main__':
    app.run_server(debug=False, threaded = False)