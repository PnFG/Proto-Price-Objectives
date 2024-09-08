from pypnf import PointFigureChart
import numpy as np, pandas as pd

# TODO: add _ as prefix before these 6 internal function/method names when merging into PointFigureChart class

def find_most_recent_sell_signal(self):

    # Returns Column Index of most recent Buy Signal
    # Based upon fivethreeo's reply 

    at_column = np.size(self.signals['type'])

    while (at_column > 0):

        signal = self.signals['type']
        if signal is 1:     # 1 for Sell
            break
        at_column = at_column - 1

    return(at_column)          

def find_most_recent_buy_signal(self):
  
    # Returns Column Index of most recent Buy Signal
    # Based upon fivethreeo's reply

    at_column = np.size(self.signals['type'])

    while (at_column > 0):

        signal = self.signals['type']
        if signal is 0:     # 0 for Buy
            break
        at_column = at_column - 1

    return(at_column)                                     

def identify_measure_column(self, method, signal):  # TODO: Issue: signal or trend?

    '''
    Breakout Method - Bullish:

    If using the Breakout Method and the active signal is a P&F buy signal:
        Find the most recent P&F sell signal.
        Identify the Measure Column that reversed the P&F sell signal.

    Breakout Method - Bearish:

    If using the Breakout Method and the active signal is a P&F sell signal:
        Find the most recent P&F buy signal
        Identify the Measure Column that reversed the P&F buy signal.

    Reversal Method - Bullish:

    If using the Reversal Method and the active signal is a P&F buy signal:
        Find the most recent P&F sell signal.
        The X-Column next to the sell signal column becomes the Measure Column.

    Reversal Method - Bearish:

    If using the Reversal Method and the active signal is a P&F sell signal:
        Find the most recent P&F buy signal.
        The O-Column next to the buy signal column becomes the Measure Column.
 
    '''

    measure_column_index = pd.nan                       # including NOT currently implemented 'horizontal_counts' or 'vertical_counts' methods

    placeholder = pd.nan

    if (method is 'breakout'):    

        if (signal is 'buy'):                           # Bullish - or is this latest trend per next_simple_signal?

            measure_column_index = find_most_recent_sell_signal(self)

        elif (signal is 'sell'):                        # Bearish

            measure_column_index = find_most_recent_buy_signal(self)

    elif (method is 'reversal'):

        if (signal is 'buy'):                           # Bullish

            measure_column_index = placeholder          # TODO: X-Column next to the Sell signal

        elif (signal is 'sell'):                        # Bearish

            measure_column_index = placeholder          # TODO: O-Column next to the Buy signal
    
    return(measure_column_index)

def calculate_height(self):    
    
    # Calculate the height of the Measure Column.

    counts = get_counts(self)
    height = counts.length

    return(height)

def get_low_of_previous_column(self, from_colindex):

    # Returns Low of previous column (from_colindex)
    # Why: Add the result to the low of the column before the Measure Column to get the Bullish Price Objective.

    if not self.highs_lows_heights_trends:
        self.get_highs_lows_heights_trends()

        highs, lows, heights, trends = self.highs_lows_heights_trends
        if trends[from_colindex] == -1: 
            return lows[from_colindex-2]
        return lows[from_colindex-1]

def get_high_of_column_before(self, from_colindex):

    # Returns High of previous column (from_colindex)
    # Why: Subtract the result from the high of the column before the Measure Column to get the Bearish Price Objective.

    if not self.highs_lows_heights_trends:
        self.get_highs_lows_heights_trends()

        highs, lows, heights, trends = self.highs_lows_heights_trends
        if trends[from_colindex] == -1: 
            return highs[from_colindex-2]
        return highs[from_colindex-1]

def get_price_objective(self, method='reversal', squares=3):

    """

    Get Price Objective (described in https://github.com/swaschke/pypnf/issues/12 and https://chartschool.stockcharts.com/table-of-contents/chart-analysis/point-and-figure-charts/p-and-f-price-objectives/p-and-f-price-objectives-breakout-and-reversal-method 

    Parameters:
    ===========

    self: pnf structure

    method: str
        'reversal' or 'breakout'. 
        default('reversal')
   
    squares: int
        number of squares used to determine price objective.  
        default(3).

    Returns:  
    ========

    price_objective: dict
        objective:
            float: price objective.

        signal:
            str: 'Bullish', 'Bearish'

        confidence: str     # described at https://chartschool.stockcharts.com/table-of-contents/chart-analysis/point-and-figure-charts/p-and-f-price-objectives/p-and-f-price-objectives-breakout-and-reversal-method#met_price_objectives
            str: 'Met', 'Tentative'

    """

    price_objective = {    # Dictionary structure definition
        "objective": 0.0,  # float: price objective
        "signal": "",      # str: 'Bullish', 'Bearish'
        "confidence": ""   # str: 'Met', 'Tentative'
    }

    # Identify Signal Type - when is self.active_signal set, by calling next_simple_signal, or? 

    Debug = True

    if Debug:

        print(next_simple_signal(self))                 # implemented in swasche's Counts branch 
        print(self.active_signal)
        print(find_most_recent_buy_signal(self))        # implemented per fivethreeo's comments
        print(find_most_recent_sell_signal(self))       # implemented per fivethreeo's comment

    #   Bullish Price Objective

    if (self.active_signal == 'buy'):

        price_objective["signal"] = 'Bullish'

        # Find the most recent P&F sell signal
        sell_signal = self.find_most_recent_sell_signal()

        # Identify the Measure Column that reversed the P&F sell signal
        measure_column = self.identify_measure_column(sell_signal)

        # Calculate the height of the Measure Column
        height = self.calculate_height(measure_column)

        # Multiply the height by the box reversal amount
        result = height * self.box_reversal_amount

        # Add the result to the low of the column before the Measure Column to get the Bullish Price Objective
        bullish_price_objective = result + self.get_low_of_column_before(measure_column)

        price_objective["objective"] = bullish_price_objective

    #   Bearish Price Objective

    elif (self.active_signal == 'sell'):

        price_objective["signal"] = 'Bearish'

        # Find the most recent P&F buy signal
        buy_signal = self.find_most_recent_buy_signal()                                                 

        # Identify the Measure Column that reversed the P&F buy signal
        measure_column = self.identify_measure_column(buy_signal)

        # Calculate the height of the Measure Column
        height = self.calculate_height(measure_column)

        # Multiply the height by 2/3 of the box reversal amount
        result = height * (2/3) * self.box_reversal_amount

        # Subtract the result from the high of the column before the Measure Column to get the Bearish Price Objective
        bearish_price_objective = self.get_high_of_column_before(measure_column) - result

        price_objective["objective"] = bearish_price_objective

    return(price_objective)