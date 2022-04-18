"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location, and a callback uses the
current location to render the appropriate page content. The active prop of
each NavLink is set automatically according to the current pathname. To use
this feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from server import app, redisUtil

from home_page import get_home_page
from model_info_page import get_model_info_page
from certificate_page import get_certificate_page
from metric_page import  get_metric_page
from metric_info_page import get_metric_info_page
from certificate_info_page import get_certificate_info_page

from metric_page_details import get_metric_page_details
from metric_page_graph import get_metric_page_graph

from utils import Iconify


import sys

 


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
sidebar = html.Div(
    [
        html.H2( ["RAI",html.Img(src = "./assets/img/rai_logo.png", style={"float":"right","width":"62px","height":"80px"} )], className="display-4"),
        
        html.P(
            "A framework for responsible AI development", className="small"
        ),
        html.Hr(),
        dbc.Nav(
            [ 
                dbc.NavLink(  
                    Iconify( "Home", "fa-solid fa-home" , "25px"), 
                    href="/", active="exact"  ),
                html.Hr(),
                dbc.NavLink( 
                    Iconify( "Metrics Details", "fas fa-table fas-10x" , "18px"),
                    href="/metrics_details", active="exact"),
                dbc.NavLink(
                    Iconify( "Metrics Graphs", "fa-solid fa-chart-gantt" , "18px"),
                    href="/metrics_graphs", active="exact"),
                
                dbc.NavLink(
                    Iconify( "Certificates", "fa-solid fa-list-check" , "45px"),
                    href="/certificates", active="exact"),
                
                html.Hr(),
                dbc.NavLink(
                    Iconify( "Model Info", "fa-solid fa-circle-info" , "55px"),
                    href="/modelInfo", active="exact"),
                
                dbc.NavLink(
                    Iconify( "Metrics Info", "fa-solid fa-file-lines" , "50px"),
                    href="/metricsInfo", active="exact"),
                dbc.NavLink( 
                    Iconify( "Certificates Info", "fa-solid fa-check-double" , "20px"),
                    href="/certificateInfo", active="exact"),
                
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return get_home_page() 
    elif pathname == "/metrics":
        return get_metric_page()
    elif pathname == "/metrics_details":
        return get_metric_page_details()
    elif pathname == "/metrics_graphs":
        return get_metric_page_graph()
    elif pathname == "/certificates":
        return get_certificate_page()
    elif pathname == "/modelInfo":
        return get_model_info_page()

    elif pathname == "/metricsInfo":
        return get_metric_info_page()
    elif pathname == "/certificateInfo":
        return get_certificate_info_page()
        
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    
    model_name = "AdultDB"  # sys.argv[1]
    if len(sys.argv) == 2:
        model_name = sys.argv[1]

    if not redisUtil.initialized:
        redisUtil.initialize(model_name, subscribers={"metric_detail","metric_graph","certificate"})
    app.run_server(debug=True)
    redisUtil.close()