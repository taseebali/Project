import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px


# Read CSV files
account_share = pd.read_csv("./data/company_shares_in_south_africa.csv")
investment = pd.read_csv("./data/global_investments.csv")
forecasting_ai = pd.read_csv("./data/market_size_forecasting_generative_ai.csv")
outsourcing = pd.read_csv("./data/outsourcing_it.csv")
revenue_forecast = pd.read_csv("./data/revenue_forecast_it_south_africa.csv")
topcompanies = pd.read_csv("./data/top_ai_companies.csv")

# Change column names
account_share.columns = ['brand', 'sharepercentage', 'market']

# Convert billions to millions
def ConvertToMillions(value):
    if 'm' in value:
        return float(value.replace('m', ''))
    elif 'b' in value:
        return float(value.replace('b', '')) * 1000
    else:
        return float(value)

investment['total_investment(in Millions)'] = investment['total_investment'].apply(ConvertToMillions)
simplified_investment = investment.drop(columns=['total_investment'])
simplified_investment.to_csv("./data/simplified_global_investment.csv", index=False)

# Lowercase column names
outsourcing.columns = outsourcing.columns.str.lower()#Brand >> brand
revenue_forecast.columns = revenue_forecast.columns.str.lower()
topcompanies.columns = topcompanies.columns.str.lower()
topcompanies.columns = topcompanies.columns.str.replace(' ', '_')#Market Value >> marketvalue

# Rename and clean topcompanies
topcompanies.rename(columns={'market_cap(as_of_march_2024)': 'market_cap_march2024'}, inplace=True)
cleaned_topcompanies = topcompanies.dropna()# dropping null values
cleaned_topcompanies.to_csv("./data/cleaned_topcompanies.csv", index=False)

# Fix null values in outsourcing
outsourcing.loc[2, 'insource'] = '23%'
outsourcing_fixed = outsourcing.fillna('77%')
outsourcing_fixed.to_csv('./data/fixed_outsourcing.csv', index=False)
forecasting_ai_melted = pd.melt(forecasting_ai, id_vars=['Area'], var_name='Year', value_name='GenAI Value')
forecasting_ai_melted = forecasting_ai_melted.drop('Area', axis=1)

# Process revenue forecast
rf_melted = revenue_forecast.melt(id_vars=['area'], var_name='years', value_name="values")
rf_pivoted = rf_melted.pivot(index="years", columns="area", values="values")
rf_pivoted.columns = rf_pivoted.columns.get_level_values(0)
rf_pivoted = rf_pivoted.reset_index()
rf_pivoted.columns.name = None
rf_pivoted.columns = rf_pivoted.columns.str.lower().str.replace(' ', '').str.replace('-', '')

# Create figures
fig1 = px.bar(outsourcing_fixed, x="area", y="insource", title="Insourcing in each area")
outsourcing_fixed1 = outsourcing_fixed.sort_values(by="outsource", ascending=True)
fig2 = px.bar(outsourcing_fixed1, x="area", y="outsource", title="Outsourcing in each area")
fig3 = px.line(outsourcing_fixed, x="area", y=["insource", "outsource"], title="Insourcing and Outsourcing in each area")
fig4 = px.line(outsourcing_fixed, x="area", y=["insource"], title="Insourcing in each area")
fig5 = px.line(outsourcing_fixed1, x="area", y=["outsource"], title="Outsourcing in each area")
fig6 = px.scatter(outsourcing_fixed, x="area", y="insource")
fig7 = px.scatter(outsourcing_fixed1, x="area", y="outsource")

fig8 = px.bar(rf_pivoted, x="years", y="itadministrationoutsourcing", text="itadministrationoutsourcing", title="IT Administration Outsourcing forecast")
fig9 = px.bar(rf_pivoted, x="years", y="itapplicationoutsourcing", text="itapplicationoutsourcing", title="IT Application Outsourcing forecast")
fig10 = px.bar(rf_pivoted, x="years", y="itotheritoutsourcing", text="itotheritoutsourcing", title="Other IT Outsourcing forecast")
fig11 = px.bar(rf_pivoted, x="years", y="itwebhosting", text="itwebhosting", title="IT Web Hosting forecast")
fig12 = px.line(rf_pivoted, x="years", y=["itadministrationoutsourcing", "itapplicationoutsourcing", "itotheritoutsourcing", "itwebhosting"])
fig13 = px.scatter(rf_pivoted, x="years", y=["itadministrationoutsourcing", "itapplicationoutsourcing", "itotheritoutsourcing", "itwebhosting"])

# Other figures
fig15 = px.bar(simplified_investment, x="year", y="total_investment(in Millions)", title="Total Investment each year (in millions)", text="total_investment(in Millions)")
fig16 = px.bar(account_share, x='brand', y='sharepercentage', title='Percentage Share of brands in South Africa', range_y=[0, 80], text="sharepercentage")

# Random colors for brands
fig17 = px.bar(account_share[account_share['market'].isin(['generative AI(text)', 'generative AI(image)'])], x='brand', y='sharepercentage', title='Share Percentage of Brands that are working with AI in South Africa', color='brand', range_y=[0, 80], text="sharepercentage")
fig18 = px.treemap(
    account_share,
    path=['market', 'brand'],
    values='sharepercentage',
    color='market',
    color_discrete_map={'it services': '#636EFA', 'generative AI(text)': '#EF553B', 'generative AI(image)': '#00CC96'},
    title='Market Share by Brand and Market Segment',
    hover_data = ['sharepercentage']
)
# Configure text display
fig18.update_traces(hovertemplate="<br>Share: %{value}%<br>")
# Adjust margins
fig18.update_layout(margin=dict(t=50, l=25, r=25, b=25))
fig19 = px.bar(forecasting_ai_melted, x = 'Year', y = 'GenAI Value', text = 'GenAI Value')


app = dash.Dash()
server = app.server

app.layout = html.Div([
    html.H1('GRAPHS', style={'textAlign': 'center', 'color': '#636EFA'}),
    html.Hr(),
    
    html.H2('Top AI Companies'),
    dcc.Graph(figure=fig15),
    dcc.Graph(figure=fig16),
    
    html.Hr(),
    
    html.H2('Market Share'),
    dcc.Graph(figure=fig17),
    dcc.Graph(figure=fig18),
    
    html.Hr(),
    
    html.H2('Generative AI Forecast'),
    dcc.Graph(figure=fig19),
    html.Hr(),

    html.H2('Outsourcing'),
    dcc.Graph(figure=fig1),
    dcc.Graph(figure=fig2),
    
    html.Hr(),
    
    html.H2('Revenue Forecast'),
    dcc.Graph(figure=fig8),
    dcc.Graph(figure=fig9),
    dcc.Graph(figure=fig10),
    dcc.Graph(figure=fig11),

    html.Hr(),
    
])

if __name__ == '__main__':
    app.run_server(debug = True)
