# CTCQAT
Crypto Currency Query & Analysis Tool

## Overview
CTCQAT is a Python script that fetches and analyzes Ethereum wallet transactions using the Etherscan API. It builds a directed graph where nodes represent wallet addresses and edges represent transactions, then visualizes the number of transactions per address in a bar chart.

The script also provides insights into transaction metrics and flags potential illicit activity using basic heuristics (e.g., high-value transactions or high-connectivity addresses).

## Installation

1. **Clone or download this repository.**
2. **Install required Python libraries:**
   ```bash
   pip install requests networkx matplotlib
   ```

## Usage

1. **Obtain a free Etherscan API key:**  
   Sign up at [Etherscan API](https://etherscan.io/apis) and copy your API key.

2. **Run the script:**
   ```bash
   python CTCQAT.py
   ```
   You will be prompted for:
   - Your Etherscan API key
   - The Ethereum wallet address to analyze
   - The number of transactions to fetch (e.g., 10-20)

## Example

```
Enter your Etherscan API key: YOUR_API_KEY
Enter the wallet address to analyze: 0x742d.....438f44e
Enter the number of transactions to fetch (e.g., 10-20): 15
```

The script will fetch transactions, display a bar chart of transaction counts per address, and print key insights and potential flags.

## Results

### Example Output

```
=== Key Insights and Metrics ===
Wallet Address: 0x742d35c......38f44e
Number of Transactions Analyzed: 15
Unique Addresses Involved: 12
Total Value Transferred (ETH): 25.1234
Average Transaction Value (ETH): 1.6749
Transactions in Last 24 Hours: 3
Insight: Low recent activity.

=== Illicit Activity Detection (Basic) ===
Potential Flag: 2 high-value transactions (>10 ETH) detected. Could indicate large transfers or wash trading.
  - Tx Hash: 0xabc12345... Value: 12.50 ETH
  - Tx Hash: 0xdef67890... Value: 11.00 ETH
No basic red flags detected. Activity appears routine.

Data Source: Etherscan API
```

### Example Screenshot

![Bar chart of transactions per address](screenshot1.png)

*Bar chart showing the number of transactions per wallet address (top 10 addresses).*

![Entire Output](screenshot2.png)
*Entire output after closing the graph.*
---