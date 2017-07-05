import pandas as pd
import numpy as np


# For calculating the realized profit and loss based on the traded prices, traded quantities and fees
class GetRealizedPnl:
   
    def __init__(self, traded_price=0, traded_quantity=0, fee=0):
        """
        self.avg_price is always positive no matter 'Buy' or 'Sell'.
        self.start_quantity is signaled number with positive as 'Sell' and negative as 'Buy'.
        self.realized_pnl is signaled number with positive as profit and negative as loss.
        """
            
        # Initiate the start price and quantity
        # The avg_price is the average price of the remaining stocks
        # The start_quantity is the remaining stocks
        self.avg_price = 0
        self.start_quantity = 0
        
        # Initiate the realized pnl
        self.realized_pnl = 0
        
        # Method for updating the avg_price, start_quantity and the pnls
        self.update(traded_price, traded_quantity, fee)
        
    
    def update(self, traded_price, traded_quantity, fee):
        """
        traded_price must always be positive no matter 'Buy' or 'Sell'.
        traded_quantity is signaled number with positive as 'Sell' and negative as 'Buy'.
        fee must always be positive no matter 'Buy' or 'Sell'.
        """
        
        # 1st, no matter buy or sell, fee is always a cost.
        self.realized_pnl -= fee
                
        # 2nd, check if there is pnl realized. If both < 0 or both > 0, then not realized
        # XOR the signal of the two quantity values, it's false when signals are different
        is_realized = (traded_quantity > 0) ^ (self.start_quantity > 0)
        
        # Update realized_pnl if is_realized.
        if is_realized:
            # Get the minimum quantity for the realized quantities
            realized_quantity = min(abs(traded_quantity), abs(self.start_quantity))
                        
            # Since realized_quantity is always positive, the other one must be negative
            if self.start_quantity > 0:
                realized_start = realized_quantity
                realized_traded = realized_quantity * (-1)
            else:
                realized_start = realized_quantity * (-1)
                realized_traded = realized_quantity
            
            # Calculate the realized pnl            
            self.realized_pnl += realized_start * self.avg_price + realized_traded * traded_price
            
            # Since pnl realized, the start_quantity become smaller.
            # Simply add the traded quantity as they are both signed.
            # but the avg_price become the price of the larger quantity.
            self.avg_price = traded_price if abs(traded_quantity) > abs(self.start_quantity) else self.avg_price
            self.start_quantity += traded_quantity
        
        # If not realized, just update the avg_price and start_quantity
        else:
            # avg_price = total value / total quantity
            if self.start_quantity + traded_quantity == 0:
                self.avg_price = 0
                self.start_quantity = 0
                #print("No stock.")

            else:
                self.avg_price = (self.start_quantity * self.avg_price + 
                                  traded_price * traded_quantity) / (self.start_quantity + traded_quantity)
                self.start_quantity += traded_quantity
                #print("Updated successfully.")

    
    def rpnl(self):
        # Return the value of realized profit or loss rounding to 2 decimal points
        # Not using round() or np.round() because in some cases they are unpredictable
        return float(format(self.realized_pnl, '.2f'))


# main function
def rank_trader_rpnl(path_input, path_output):
    # Read input file
    orders_df = pd.read_table(path_input, sep='\t')

    # Encode trade type
    orders_df['TradeTypeEncode'] = orders_df['TradeType'].apply(
        lambda x: (1 if x == 'Sell' else -1))

    # Apply signals to TradeQuantity
    # with positive as Sell, and negative as Buy
    orders_df['TradedQuantity'] = orders_df['Quantity'] * orders_df['TradeTypeEncode']

    # Get the list of traders
    rpnl_ranking = pd.DataFrame({'Trader': orders_df.Trader.unique()})
    
    # Applying method for a dataframe
    # to get the realized profit and loss (rpnl) for a trader
    def rpnl_of_trader(row):
        # Get the slice for the trader
        trader_name = row.Trader
        trader_slice_df = orders_df.loc[orders_df.Trader == trader_name]

        # Calculate the rpnl
        realized_pnl = GetRealizedPnl()
        for row in trader_slice_df.itertuples():
            realized_pnl.update(row.Price, row.TradedQuantity, row.Fee)

        return realized_pnl.rpnl()

    # Apply function to get the realized profit and loss for each trader
    rpnl_ranking['RealizedPnl'] = rpnl_ranking.apply(rpnl_of_trader, axis=1)

    # Sort by rpnl from large to small
    rpnl_ranking = rpnl_ranking.sort_values('RealizedPnl', ascending=False)

    # Save the results
    rpnl_ranking.to_csv(path_output, index=False, header=False, sep='\t')
    
    print('The output is saved as "{}". \nDone.'.format(path_output))