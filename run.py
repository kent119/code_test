import realized_pnl_calculator


# Setting paths for input and output
path_input = 'data.tsv'
path_output = 'output.tsv'


# Run the script and save as tsv
realized_pnl_calculator.rank_trader_rpnl(path_input, path_output)