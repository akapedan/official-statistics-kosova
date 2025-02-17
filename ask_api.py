import requests
import pandas as pd
import json
from typing import List, Union, Dict, Optional

class ASK:
    """
    Kosovo Agency of Statistics (ASK) API wrapper.
    
    A class to interact with the ASK API, providing methods to fetch and process
    statistical data about Kosovo.
    
    Parameters
    ----------
    lang : str, optional
        Language code for the API responses, by default 'sq'
        Options: 'sq' for Albanian, 'en' for English
    
    Attributes
    ----------
    base_url : str
        Base URL for the ASK API
    current_path : list
        Current navigation path in the API structure
    municipality_map : dict
        Mapping of municipality codes to names
    municipality_reverse_map : dict
        Mapping of municipality names to codes
    """
    
    def __init__(self, lang='sq'):
        self.lang = lang
        self.base_url = f'http://askdata.rks-gov.net/api/v1/{lang}/ASKdata'
        self.current_path = []
        self.query = {
            "query": [],
            "response": {"format": "json"}
        }
        
        # Municipality mapping (code to name)
        self.municipality_map = {
            '0': 'Deçan', '1': 'Gjakovë', '2': 'Gllogoc', '3': 'Gjilan',
            '4': 'Dragash', '5': 'Istog', '6': 'Kaçanik', '7': 'Klinë',
            '8': 'Fushë Kosovë', '9': 'Kamenicë', '10': 'Mitrovicë',
            '11': 'Leposaviq', '12': 'Lipjan', '13': 'Novobërdë',
            '14': 'Obiliq', '15': 'Rahovec', '16': 'Pejë', '17': 'Podujevë',
            '18': 'Prishtinë', '19': 'Prizren', '20': 'Skenderaj',
            '21': 'Shtime', '22': 'Shtërpcë', '23': 'Suharekë',
            '24': 'Ferizaj', '25': 'Viti', '26': 'Vushtrri',
            '27': 'Zubin Potok', '28': 'Zveqan', '29': 'Malishevë',
            '30': 'Junik', '31': 'Mamushë', '32': 'Hani i Elezit',
            '33': 'Graçanicë', '34': 'Ranillug', '35': 'Partesh',
            '36': 'Kllokot', '37': 'Mitrovicë Veriore', '38': 'Jashtë Kosovës',
            '39': 'Gjithsej'
        }
        
        # Create reverse mapping (name to code)
        self.municipality_reverse_map = {v.lower(): k for k, v in self.municipality_map.items()}

    def info(self) -> Optional[Dict]:
        """
        Get metadata for the current endpoint.
        
        Returns
        -------
        dict or None
            JSON response containing metadata if successful, None otherwise
        
        Notes
        -----
        This method fetches the metadata associated with the current API endpoint,
        which includes information about available variables and their possible values.
        """
        url = self.base_url + '/' + '/'.join(self.current_path)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching metadata: {e}")
            return None

    def go_down(self, *args):
        """
        Navigate deeper in the API structure.
        
        Parameters
        ----------
        *args : str
            Variable number of path segments to append to the current path
        
        Examples
        --------
        >>> ask = ASK()
        >>> ask.go_down('Population', 'Marriages')
        """
        self.current_path.extend(list(args))

    def go_up(self, levels: int = 1):
        """
        Go up specified number of levels in the API structure.
        
        Parameters
        ----------
        levels : int, optional
            Number of levels to go up in the hierarchy, by default 1
        """
        self.current_path = self.current_path[:-levels]

    def get_url(self) -> str:
        """
        Get the URL for the current endpoint.
        
        Returns
        -------
        str
            Complete URL for the current API endpoint
        """
        return self.base_url + '/' + '/'.join(self.current_path)

    def get_variables(self) -> Optional[Dict]:
        """
        Get available variables at the current endpoint.
        
        Returns
        -------
        dict or None
            Dictionary containing variable information if successful:
            - code: variable identifier
            - values: possible values
            - valueTexts: human-readable value descriptions
            Returns None if no variables are found
        """
        response = self.info()
        if not response or 'variables' not in response:
            print("Error: No variables found at current endpoint")
            return None

        variables = {}
        for var in response['variables']:
            variables[var['text']] = {
                'code': var['code'],
                'values': var['values'],
                'valueTexts': var['valueTexts']
            }
        return variables

    def clear_query(self):
        """
        Reset the query to its default state.
        
        Notes
        -----
        This method is typically called internally before setting new query parameters.
        """
        self.query = {
            "query": [],
            "response": {"format": "json"}
        }

    def get_municipality_code(self, municipality: str) -> Optional[str]:
        """
        Get the code for a given municipality name.
        
        Parameters
        ----------
        municipality : str
            Name of the municipality
        
        Returns
        -------
        str or None
            Municipality code if found, None otherwise
        
        Notes
        -----
        The search is case-insensitive.
        """
        return self.municipality_reverse_map.get(municipality.lower())

    def set_query(self, 
                 municipalities: Union[List[str], str] = None,
                 months: Union[List[str], str] = None,
                 year: Union[int, str] = None,
                 start_date: str = None,
                 end_date: str = None):
        """
        Set query parameters for data retrieval.
        
        Parameters
        ----------
        municipalities : str or list of str, optional
            Municipality name(s) to query
        months : str or list of str, optional
            Specific months to query in format "YYYYMXX"
        year : int or str, optional
            Year to query (will include all months)
        start_date : str, optional
            Start date in format "YYYY-MM" or "YYYYMM"
        end_date : str, optional
            End date in format "YYYY-MM" or "YYYYMM"
        
        Notes
        -----
        At least one parameter should be provided to create a valid query.
        
        Examples
        --------
        >>> ask = ASK()
        >>> ask.set_query(municipalities=["Prishtinë", "Prizren"],
        ...              start_date="2023-01",
        ...              end_date="2023-12")
        """
        self.clear_query()
        
        # Process municipalities
        if municipalities:
            if isinstance(municipalities, str):
                municipalities = [municipalities]
            
            municipality_codes = []
            for muni in municipalities:
                code = self.get_municipality_code(muni)
                if code:
                    municipality_codes.append(code)
                else:
                    print(f"Warning: Municipality '{muni}' not found")
            
            if municipality_codes:
                self.query["query"].append({
                    "code": "Komuna",
                    "selection": {
                        "filter": "item",
                        "values": municipality_codes
                    }
                })

        # Process dates
        date_values = []
        
        if months:
            if isinstance(months, str):
                months = [months]
            date_values.extend(months)
        
        if year:
            year_str = str(year)
            date_values.extend([f"{year_str}M{str(m).zfill(2)}" for m in range(1, 13)])
        
        if start_date and end_date:
            # Convert dates to proper format
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            dates = pd.date_range(start, end, freq='M')
            date_values.extend([d.strftime('%YM%m') for d in dates])
        
        if date_values:
            self.query["query"].append({
                "code": "Viti-muaji",
                "selection": {
                    "filter": "item",
                    "values": sorted(list(set(date_values)))
                }
            })

    def get_query(self) -> Dict:
        """
        Get the current query parameters.
        
        Returns
        -------
        dict
            Current query configuration
        """
        return self.query

    def get_data(self) -> Optional[Dict]:
        """
        Fetch raw data using the current query.
        
        Returns
        -------
        dict or None
            Raw JSON response from the API if successful, None otherwise
        
        Notes
        -----
        This method performs the actual API request using the current query parameters.
        """
        url = self.get_url()
        try:
            response = requests.post(url, json=self.query)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def get_data_as_df(self) -> Optional[pd.DataFrame]:
        """
        Fetch and transform data into a pandas DataFrame.
        
        Returns
        -------
        pandas.DataFrame or None
            DataFrame containing the query results with columns:
            - Date: datetime
            - Municipality_Code: str
            - Municipality: str
            - Marriages: int or None
            Returns None if the data fetch fails
        
        Notes
        -----
        Missing values in the data are represented as None.
        The DataFrame is sorted by Date and Municipality.
        
        Examples
        --------
        >>> ask = ASK()
        >>> ask.go_down('Population', 'Marriages')
        >>> ask.set_query(municipalities="Prishtinë", year=2023)
        >>> df = ask.get_data_as_df()
        >>> print(df.head())
        """
        data = self.get_data()
        if not data:
            return None
        
        # Create a list to store the transformed data
        rows = []
        
        # Process each data point
        for item in data['data']:
            date = item['key'][0]
            municipality_code = item['key'][1]
            marriages = item['values'][0]
            
            # Convert ':' to None for missing values
            if marriages == ':':
                marriages = None
            else:
                marriages = int(marriages)
                
            rows.append({
                'Date': date,
                'Municipality_Code': municipality_code,
                'Municipality': self.municipality_map.get(municipality_code, f'Unknown ({municipality_code})'),
                'Marriages': marriages
            })
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'].str.replace('M', '-'), format='%Y-%m')
        
        # Sort by Date and Municipality
        df = df.sort_values(['Date', 'Municipality'])
        
        return df

    def get_available_municipalities(self) -> Dict[str, str]:
        """
        Get all available municipalities and their codes.
        
        Returns
        -------
        dict
            Dictionary mapping municipality names to their codes
        
        Examples
        --------
        >>> ask = ASK()
        >>> municipalities = ask.get_available_municipalities()
        >>> print(municipalities['Prishtinë'])
        '18'
        """
        return {v: k for k, v in self.municipality_map.items()}

    def get_available_months(self) -> Optional[List[str]]:
        """
        Get list of available months from the current endpoint.
        
        Returns
        -------
        list of str or None
            List of available months in format "YYYYMXX" if successful,
            None if the information is not available
        
        Notes
        -----
        This method requires being at a valid endpoint in the API hierarchy.
        """
        variables = self.get_variables()
        if variables and 'Viti-muaji' in variables:
            return variables['Viti-muaji']['valueTexts']
        return None

    def get_current_location(self) -> str:
        """
        Get the current location in the API hierarchy.
        
        Returns
        -------
        str
            String representation of current path
        
        Examples
        --------
        >>> ask = ASK()
        >>> ask.go_down('Population', 'Marriages')
        >>> print(ask.get_current_location())
        'Current location: Population/Marriages'
        """
        return 'Current location: ' + '/'.join(self.current_path)

    def list_available_paths(self) -> Optional[List[Dict]]:
        """
        List all available navigation options from current location.
        
        Returns
        -------
        list of dict or None
            List of available paths with their metadata:
            - id: path identifier
            - text: human-readable name
            - type: node type ('l' for leaf, 'h' for hierarchy)
            Returns None if fetching fails
        
        Examples
        --------
        >>> ask = ASK()
        >>> paths = ask.list_available_paths()
        >>> for path in paths:
        ...     print(f"- {path['text']} ({'dataset' if path['type']=='l' else 'folder'})")
        """
        response = self.info()
        if not response:
            return None
        
        if 'variables' in response:
            print("This is a dataset endpoint. Available variables:")
            for var in response['variables']:
                print(f"- {var['text']}")
            return None
        
        # Check if response is a list (contains paths)
        if isinstance(response, list):
            return response
        
        print("No paths available at current location")
        return None

    def print_navigation_tree(self, max_depth: int = 2):
        """
        Print the navigation tree from current location up to specified depth.
        
        Parameters
        ----------
        max_depth : int, optional
            Maximum depth to explore, by default 2
        
        Notes
        -----
        This method may take some time as it needs to make multiple API requests.
        
        Examples
        --------
        >>> ask = ASK()
        >>> ask.print_navigation_tree(max_depth=2)
        Current location: /
        ├── Population
        │   ├── Marriages and divorces
        │   ├── Migration
        │   └── Population estimates
        ├── Education
        │   ├── Primary education
        │   └── Secondary education
        └── Economy
            ├── GDP
            └── Trade
        """
        def explore_path(path, depth, prefix=""):
            if depth >= max_depth:
                return
            
            current_path = self.current_path.copy()
            self.current_path = path
            
            items = self.list_available_paths()
            if not items:
                self.current_path = current_path
                return
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                print(f"{prefix}{'└──' if is_last else '├──'} {item['text']}")
                
                if item['type'] == 'h':  # If it's a hierarchy node
                    new_prefix = prefix + ('    ' if is_last else '│   ')
                    explore_path(path + [item['id']], depth + 1, new_prefix)
            
            self.current_path = current_path

        print(f"Current location: /{'/'.join(self.current_path)}")
        explore_path([], 0)

    def navigate(self) -> Optional[List[str]]:
        """
        Interactive navigation through the API structure.
        
        Returns
        -------
        list of str or None
            List of path segments to reach the selected dataset,
            can be used with go_down(). Returns None if navigation
            was cancelled.
        
        Notes
        -----
        This method provides an interactive command-line interface for navigation.
        
        Examples
        --------
        >>> ask = ASK()
        >>> path = ask.navigate()
        >>> if path:
        ...     print(f"To reach this dataset, use: ask.go_down({', '.join(repr(p) for p in path)})")
        ...     ask.go_down(*path)
        """
        path_taken = []
        
        while True:
            print(f"\n{self.get_current_location()}")
            paths = self.list_available_paths()
            
            if not paths:
                print("\nThis is a dataset endpoint.")
                print("Available variables:")
                variables = self.get_variables()
                if variables:
                    for var_name, var_info in variables.items():
                        print(f"- {var_name}")
                print("\nTo reach this dataset, use:")
                print(f"ask.go_down({', '.join(repr(p) for p in path_taken)})")
                return path_taken
            
            print("\nAvailable paths:")
            for i, path in enumerate(paths, 1):
                path_type = 'dataset' if path['type'] == 'l' else 'folder'
                print(f"{i}. {path['text']} ({path_type})")
            
            choice = input("\nEnter number to navigate (0 to exit, -1 to go up): ")
            if not choice.isdigit() and choice != '-1':
                print("Invalid input. Please enter a number.")
                continue
            
            choice = int(choice)
            if choice == 0:
                return None
            elif choice == -1:
                if self.current_path:
                    self.go_up()
                    if path_taken:
                        path_taken.pop()
                continue
            elif 1 <= choice <= len(paths):
                selected_path = paths[choice-1]
                self.go_down(selected_path['id'])
                path_taken.append(selected_path['id'])
            else:
                print("Invalid choice. Please try again.")
