from ask_api import ASK
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

if __name__ == "__main__":
    # Initialize API client
    ask = ASK()

    # Navigate to marriages dataset and query marriage statistics for Kosovo municipalities
    ask.go_down('Population', 'Marriages and divorces', 'Marriages', 
                'Monthly indicators', 'tab05.px')
    
    # Query all data (no filters)
    ask.set_query()
    
    # Get the data
    df = ask.get_data_as_df()
    
    # Sort municipalities by number of marriages for each time period
    df = df.sort_values('Marriages', ascending=False)  # Changed to True for horizontal bars

    # Remove 'Gjithsej' from municipalities
    df = df[df['Municipality'] != 'Gjithsej']

    # Create the interactive bar chart
    fig = px.bar(df, 
                y='Municipality',  # Switched x and y for horizontal bars
                x='Marriages',
                animation_frame=df['Date'].dt.strftime('%Y-%m'),
                template='plotly_white')

    # Update traces to set bar color and add text
    fig.update_traces(
        marker_color='rgb(36,74,165)',  # Blue bars
        text=df['Marriages'],  # Show marriage count
        textposition='inside',  # Place text inside bars
        textfont=dict(color='white'),  # White text
        insidetextanchor='middle'  # Center text in bars
    )

    # For each frame in the animation, sort the data
    for frame in fig.frames:
        frame.data[0].y = frame.data[0].y[::-1]  # Reverse the order
        frame.data[0].x = frame.data[0].x[::-1]  # Reverse the corresponding values
        frame.data[0].text = frame.data[0].x  # Update the text to match

    # Update layout for minimal design
    fig.update_layout(
        title=dict(
            text='Marriages by Municipality Over Time',
            x=0.5,
            font=dict(color='black', size=20)
        ),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        yaxis=dict(
            showgrid=False,
            title_text=None,  # Remove y-axis title
            autorange="reversed"  # Reverse order to have highest values at top
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            title_text='Number of Marriages'
        ),
        # Animation settings
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 1000, 'redraw': True}, 'fromcurrent': True}]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}]
                }
            ],
            'x': 0.1,
            'y': 1.1
        }],
        sliders=[{
            'currentvalue': {'prefix': 'Date: '},
            'pad': {'t': 50}
        }],
        height=800  # Make the plot taller to accommodate all municipalities
    )

    # Save the interactive plot
    fig.write_html('marriages_over_time.html')

    # Display in browser
    fig.show()
