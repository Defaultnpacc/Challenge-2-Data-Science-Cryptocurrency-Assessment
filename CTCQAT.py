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