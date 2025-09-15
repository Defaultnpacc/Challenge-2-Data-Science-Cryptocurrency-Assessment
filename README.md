# CTCQAT
Crypto Currency Query & Analysis Tool

This Python script fetches and analyzes Ethereum wallet transactions using the Etherscan API. It builds a directed graph where nodes represent wallet addresses and edges represent transactions, then visualizes the number of transactions per address in a bar chart. 

The script also provides insights into transaction metrics and flags potential illicit activity using basic heuristics (e.g., high-value transactions or high-connectivity addresses).