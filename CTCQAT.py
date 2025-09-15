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
        
def plot_graph(G, wallet_address, num_transactions):
    """
    Plot the transaction graph using matplotlib and networkx.
    Handles plotting errors.
    """
    try:
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=1, iterations=50)  # Spring layout for better visualization
        nx.draw(
            G, pos, 
            with_labels=False, 
            node_size=300, 
            node_color='lightblue', 
            font_size=8, 
            font_weight='bold',
            arrows=True, 
            arrowsize=10,
            edge_color='gray',
            width=[d['weight'] * 0.1 for (u, v, d) in G.edges(data=True)]  # Edge width proportional to value
        )
        plt.title(f'Transaction Graph for Wallet {wallet_address[:10]}... (Last {num_transactions} Transactions)')
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"Error plotting graph: {e}. Graph plotting skipped.")
        
def print_insights(transactions, wallet_address, total_value_transferred, unique_addresses):
    """
    Print key insights, metrics, and basic illicit activity detection.
    Uses heuristics for flags.
    """
    try:
        print("=== Key Insights and Metrics ===")
        print(f"Wallet Address: {wallet_address}")
        print(f"Number of Transactions Analyzed: {len(transactions)}")
        print(f"Unique Addresses Involved: {len(unique_addresses)}")
        print(f"Total Value Transferred (ETH): {total_value_transferred:.4f}")
        avg_value = total_value_transferred / len(transactions) if transactions else 0
        print(f"Average Transaction Value (ETH): {avg_value:.4f}")

        # Time-based insight (assuming recent = last 24 hours)
        recent_threshold = datetime.now() - timedelta(hours=24)
        recent_count = sum(1 for tx in transactions if datetime.fromtimestamp(int(tx['timeStamp'])) > recent_threshold)
        print(f"Transactions in Last 24 Hours: {recent_count}")

        # Simple activity insight
        if recent_count > 5:
            print("Insight: High activity detected (multiple transactions in the last day).")
        else:
            print("Insight: Low recent activity.")

        #Detection of possible illicit activity (basic heuristics)
        # Note: This is simplistic; real detection requires blacklists (e.g., from Chainalysis) and more analysis.
        # Here high-value single tx (>10 ETH) or high-degree nodes (potential mixers/hubs) are flagged.
        high_value_txs = [tx for tx in transactions if int(tx['value']) / 1e18 > 10]
        G = nx.DiGraph()  # Rebuild minimal graph for degree calculation if needed
        for tx in transactions:
            G.add_edge(tx['from'].lower(), tx['to'].lower())
        high_degree_nodes = [node for node, degree in dict(G.degree()).items() if degree > 3]

        print("\n=== Bonus: Illicit Activity Detection (Basic) ===")
        if high_value_txs:
            print(f"Potential Flag: {len(high_value_txs)} high-value transactions (>10 ETH) detected. Could indicate large transfers or wash trading.")
            for tx in high_value_txs[:3]:  # Show top 3
                print(f"  - Tx Hash: {tx['hash'][:10]}... Value: {int(tx['value'])/1e18:.2f} ETH")
        if high_degree_nodes:
            print(f"Potential Flag: {len(high_degree_nodes)} addresses with high connectivity (degree >3). Could suggest mixer or exchange activity.")
            for node in high_degree_nodes[:3]:
                print(f"  - Address: {node[:10]}...")
        if not high_value_txs and not high_degree_nodes:
            print("No basic red flags detected. Activity appears routine.")

        print("\nData Source: Etherscan API")
    except Exception as e:
        print(f"Error printing insights: {e}")

# Main execution
if __name__ == "__main__":
    API_KEY, WALLET_ADDRESS, NUM_TRANSACTIONS = get_user_inputs()
    transactions = fetch_transactions(API_KEY, WALLET_ADDRESS, NUM_TRANSACTIONS)
    if transactions:  # Only proceed if there are transactions
        G, total_value_transferred, unique_addresses = build_graph(transactions)
        plot_graph(G, WALLET_ADDRESS, NUM_TRANSACTIONS)
        print_insights(transactions, WALLET_ADDRESS, total_value_transferred, unique_addresses)
    else:
        print("No data to analyze. Exiting.")