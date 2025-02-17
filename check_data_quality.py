from ask_api import ASK
import pandas as pd

pd.set_option('display.max_columns', None)

if __name__ == "__main__":
    # Initialize API client
    ask = ASK()
    
    # Navigate to marriages dataset
    ask.go_down('Population', 'Marriages and divorces', 'Marriages', 
                'Monthly indicators', 'tab05.px')
    
    # Query all data
    ask.set_query()
    df = ask.get_data_as_df()
    
    # Extract month and year
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    # Split into two dataframes
    df_total = df[df['Municipality'] == 'Gjithsej'].copy()
    df_municipalities = df[df['Municipality'] != 'Gjithsej'].copy()
    
    # Calculate sum of municipalities for each year-month
    municipality_sums = df_municipalities.groupby(['Year', 'Month'])['Marriages'].sum().reset_index()
    municipality_sums.columns = ['Year', 'Month', 'Municipality_Sum']
    
    # Merge with totals
    comparison = pd.merge(
        df_total[['Year', 'Month', 'Marriages']],
        municipality_sums,
        on=['Year', 'Month']
    )

    # Rename columns for clarity
    comparison.columns = ['Year', 'Month', 'Gjithsej', 'Municipality_Sum']
    
    # Calculate difference
    comparison['Difference'] = comparison['Gjithsej'] - comparison['Municipality_Sum']
    
    # Sort by absolute difference to see biggest discrepancies first
    comparison['Abs_Difference'] = abs(comparison['Difference'])
    comparison = comparison.sort_values('Abs_Difference', ascending=False)
    
    # Print results
    print("\nData Quality Check Results:")
    print("===========================")
    print(f"\nTotal number of year-month pairs checked: {len(comparison)}")
    print(f"Number of discrepancies found: {len(comparison[comparison['Difference'] != 0])}")
    
    if len(comparison[comparison['Difference'] != 0]) > 0:
        print("\nTop 10 largest discrepancies:")
        print(comparison[['Year', 'Month', 'Gjithsej', 'Municipality_Sum', 'Difference']]
              .head(10)
              .to_string(index=False))
        
        # Save full results to CSV
        comparison.to_csv('marriage_data_quality_check.csv', index=False)
        print("\nFull results saved to 'marriage_data_quality_check.csv'")
    else:
        print("\nNo discrepancies found! All municipality sums match 'Gjithsej' values.")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("------------------")
    print(f"Mean absolute difference: {comparison['Abs_Difference'].mean():.2f}")
    print(f"Median absolute difference: {comparison['Abs_Difference'].median():.2f}")
    print(f"Max absolute difference: {comparison['Abs_Difference'].max():.2f}")
    
    # Check for missing data
    print("\nMissing Data Check:")
    print("------------------")
    missing_municipalities = df_municipalities.groupby(['Year', 'Month'])['Municipality'].count().reset_index()
    missing_municipalities.columns = ['Year', 'Month', 'Municipality_Count']
    
    if missing_municipalities['Municipality_Count'].nunique() > 1:
        print("\nWarning: Inconsistent number of municipalities across different months!")
        print("\nMunicipality counts by month:")
        print(missing_municipalities.sort_values('Municipality_Count')
              .head()
              .to_string(index=False)) 