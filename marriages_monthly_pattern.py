from ask_api import ASK
import plotly.express as px
import pandas as pd

if __name__ == "__main__":
    # Initialize API client
    ask = ASK()
    
    # Navigate to marriages dataset
    ask.go_down('Population', 'Marriages and divorces', 'Marriages', 
                'Monthly indicators', 'tab05.px')
    
    # Query all data
    ask.set_query()
    df = ask.get_data_as_df()
    
    # Remove 'Gjithsej' and 'Jashtë Kosovës'
    df = df[~df['Municipality'].isin(['Gjithsej', 'Jashtë Kosovës'])]
    
    # Extract month and year
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    # Calculate total marriages per month
    monthly_totals = df.groupby(['Year', 'Month'])['Marriages'].sum().reset_index()
    
    # Get April and June 2023 values
    april_2023 = monthly_totals[(monthly_totals['Year'] == 2023) & (monthly_totals['Month'] == 4)]['Marriages'].values[0]
    june_2023 = monthly_totals[(monthly_totals['Year'] == 2023) & (monthly_totals['Month'] == 6)]['Marriages'].values[0]
    
    # Calculate May 2023 value as average
    may_2023_value = (april_2023 + june_2023) / 2
    
    # Update May 2023 value in the dataframe
    may_2023_mask = (monthly_totals['Year'] == 2023) & (monthly_totals['Month'] == 5)
    monthly_totals.loc[may_2023_mask, 'Marriages'] = may_2023_value
    
    # Create line chart with a line for each year
    fig = px.line(monthly_totals, 
                  x='Month', 
                  y='Marriages',
                  color='Year',
                  markers=True,
                  color_discrete_sequence=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854'])
    
    # Add a special marker for the imputed value
    fig.add_scatter(
        x=[5],
        y=[may_2023_value],
        mode='markers',
        marker=dict(
            symbol='star',
            size=15,
            color='red'
        ),
        name='Imputed Value (May 2023)',
        hovertemplate='Imputed value for May 2023<br>Average of April and June'
    )
    
    # Add year labels at the end of each line
    for year in monthly_totals['Year'].unique():
        year_data = monthly_totals[monthly_totals['Year'] == year]
        last_month = year_data['Month'].max()
        last_value = year_data[year_data['Month'] == last_month]['Marriages'].values[0]
        
        fig.add_annotation(
            x=last_month,
            y=last_value,
            text=str(year),
            showarrow=False,
            xshift=10,
            font=dict(size=12)
        )
    
    fig.update_traces(
        marker=dict(size=8)
    )
    
    fig.update_layout(
        title=dict(
            text='Total Number of Marriages by Month (Excluding Jashtë Kosovës)<br><sup>Star marker indicates imputed value for May 2023</sup>',
            x=0.5,
            font=dict(color='black', size=20)
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(
            tickmode='array',
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            tickvals=list(range(1, 13)),
            showgrid=False,
            title=None
        ),
        yaxis=dict(
            title='Number of Marriages',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        showlegend=False  # Remove legend
    )
    
    # Print the imputed value
    print(f"Imputed value for May 2023: {may_2023_value:.0f}")
    print(f"(Average of April 2023: {april_2023:.0f} and June 2023: {june_2023:.0f})")
    
    fig.write_html('marriages_monthly_pattern.html')
    fig.show() 