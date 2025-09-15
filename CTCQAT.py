import requests
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re  # For wallet address validation

def get_user_inputs():
    """
    Get and validate user inputs for API key, wallet address, and number of transactions.
    Handles input errors and validates formats.
    """
    try:
        api_key = input("Enter your Etherscan API key: ").strip()
        if not api_key:
            raise ValueError("API key cannot be empty. Please sign up at https://etherscan.io/apis for a free key.")
        
        wallet_address = input("Enter the wallet address to analyze: ").strip().lower()
        if not re.match(r'^0x[a-f0-9]{40}$', wallet_address):
            raise ValueError("Invalid Ethereum wallet address. It should start with '0x' followed by 40 hexadecimal characters.")
        
        num_transactions_str = input("Enter the number of transactions to fetch (e.g., 10-20): ").strip()
        num_transactions = int(num_transactions_str)
        if num_transactions < 1 or num_transactions > 100:  # Arbitrary upper limit to avoid API abuse
            raise ValueError("Number of transactions must be a positive integer between 1 and 100.")
        
        return api_key, wallet_address, num_transactions
    except ValueError as e:
        print(f"Input Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error during input: {e}")
        exit(1)
        
def fetch_transactions(api_key, wallet_address, num_transactions):
    """
    Fetch recent transactions from Etherscan API.
    Handles API errors and returns the list of transactions.
    """
    url = (
        f"https://api.etherscan.io/api?"
        f"module=account&action=txlist&"
        f"address={wallet_address}&"
        f"startblock=0&endblock=99999999&"
        f"sort=desc&"
        f"apikey={api_key}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad HTTP status
        data = response.json()
        
        if data['status'] != '1':
            raise ValueError(f"API Error: {data.get('message', 'Unknown error')}. Result: {data.get('result')}")
        
        transactions = data['result'][:num_transactions]
        if not transactions:
            print("No transactions found for this address.")
        
        return transactions
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching data: {e}")
        exit(1)
    except ValueError as e:
        print(e)
        exit(1)
    except Exception as e:
        print(f"Unexpected error during API fetch: {e}")
        exit(1)
        
def build_graph(transactions):
    """
    Build a directed graph from transactions.
    Nodes are addresses, edges are transactions with weights as ETH values.
    Returns the graph, total value transferred, and unique addresses.
    """
    try:
        G = nx.DiGraph()
        total_value_transferred = 0.0
        unique_addresses = set()

        for tx in transactions:
            from_addr = tx['from'].lower()
            to_addr = tx['to'].lower()
            value_wei = int(tx['value'])
            value_eth = value_wei / 1e18  # Convert Wei to ETH
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            
            G.add_edge(from_addr, to_addr, weight=value_eth, tx_hash=tx['hash'], timestamp=timestamp)
            unique_addresses.add(from_addr)
            unique_addresses.add(to_addr)
            total_value_transferred += value_eth
        
        return G, total_value_transferred, unique_addresses
    except KeyError as e:
        print(f"Error in transaction data: Missing key {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error building graph: {e}")
        exit(1)