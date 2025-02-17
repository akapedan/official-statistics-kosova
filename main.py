from ask_api import ASK

if __name__ == "__main__":
    # Initialize API client
    ask = ASK()

    # View the navigation tree
    ask.print_navigation_tree(max_depth=3)

    # Interactive navigation
    path = ask.navigate()

    if path:
        # You can now use this path directly
        ask.go_down(*path)

    else:
        # Navigate to marriages dataset
        ask.go_down('Population', 'Marriages and divorces', 'Marriages', 
                    'Monthly indicators', 'tab05.px')
        
    # Print available municipalities
    print("Available municipalities:")
    for name, code in ask.get_available_municipalities().items():
        print(f"- {name}")
    
    # Example 1: Query by municipality names and specific months
    ask.set_query(
        municipalities=["Prishtinë", "Prizren"],
        months=["2024M01", "2024M02"]
    )
    
    # Example 2: Query entire year for one municipality
    ask.set_query(
        municipalities="Gjakovë",
        year=2023
    )
    
    # Example 3: Query date range for multiple municipalities
    ask.set_query(
        municipalities=["Prishtinë", "Prizren", "Gjakovë"],
        start_date="2023-01",
        end_date="2023-12"
    )
    
    # Get the data
    df = ask.get_data_as_df()
    
    if df is not None:
        print("\nData shape:", df.shape)
        print("\nFirst few rows:")
        print(df.head())
        
        # Basic statistics
        print("\nMarriages by Municipality:")
        print(df.groupby('Municipality')['Marriages'].agg(['count', 'mean', 'sum']))
        
        # Export to CSV (optional)
        df.to_csv('marriage_statistics.csv', index=False)
