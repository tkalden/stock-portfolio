import numpy as np

class optimization():
     # init method or constructor
    def __init__(self):
        self.optimal_number_stocks = 0
        self.previous_highest_expected_return = 0
        self.threshold = 0
        self.desired_return = 0
     
    """Returns the optimal number of stocks from the top strength stocks that give the expected
    return equal or higher than the desired expected return
        :param number_of_stocks: iterative number of stocks 
        :param threshold: minimum number of stocks
        :param desired_return: desired expected return 
        :returns: optimal portfolio 
    """
    def optimize_expected_return(self, df, number_of_stocks, threshold,desired_return):
        #we want to remove the lowest strength iteratively till we get the optimal expected return
        if number_of_stocks < float(threshold):
            return  
        df = df.head(number_of_stocks)
        self.calculate_weighted_expected_return(df)
        actual_return = df['weighted_expected_return']
        actual_expected_return = float(actual_return.sum())
        actual_greater_than_desired = actual_expected_return > float(desired_return)
        actual_greater_than_previous_actual = actual_expected_return > self.previous_highest_expected_return 
        if actual_greater_than_desired:
            self.optimal_number_stocks = number_of_stocks
        elif (actual_greater_than_previous_actual) & (not actual_greater_than_desired):
             self.optimal_number_stocks = number_of_stocks
             self.previous_highest_expected_return = actual_expected_return
        self.optimize_expected_return(df,number_of_stocks - 1,threshold,actual_expected_return)
        df = df.head(self.optimal_number_stocks)
        df = self.calculate_weighted_expected_return(df)
        return df
    
    def calculate_weighted_expected_return(self, df):
        strengthArray = df["strength"]
        strengthList = list(map(float, strengthArray))
        weight_array = np.divide(strengthList, sum(strengthList))
        df['weight'] = weight_array
        df['weighted_expected_return'] =  df['expected_annual_return'].astype(float) * df['weight']
        print ("WER", df['weighted_expected_return'])
        return df