'''
  █████████  ███████████               █████████  █████                           █████   
 ███░░░░░███░░███░░░░░███             ███░░░░░███░░███                           ░░███    
░███    ░░░  ░███    ░███ █████ ████ ███     ░░░  ░███████    ██████   ████████  ███████  
░░█████████  ░██████████ ░░███ ░███ ░███          ░███░░███  ░░░░░███ ░░███░░███░░░███░   
 ░░░░░░░░███ ░███░░░░░░   ░███ ░███ ░███          ░███ ░███   ███████  ░███ ░░░   ░███    
 ███    ░███ ░███         ░███ ░███ ░░███     ███ ░███ ░███  ███░░███  ░███       ░███ ███
░░█████████  █████        ░░███████  ░░█████████  ████ █████░░████████ █████      ░░█████ 
 ░░░░░░░░░  ░░░░░          ░░░░░███   ░░░░░░░░░  ░░░░ ░░░░░  ░░░░░░░░ ░░░░░        ░░░░░  
                           ███ ░███                                                       
                          ░░██████                                                        
                           ░░░░░░                                                                                                                                                               
'''

# --------------------------
# -** REQUIRED LIBRARIES **-
# --------------------------

import pandas as pd
import numpy as np
from plotly import graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

'''

------------------
-** REFERENCES **-
------------------

    
- https://towardsdatascience.com/quality-control-charts-guide-for-python-9bb1c859c051
- https://www.spcforexcel.com/knowledge/control-chart-basics/control-chart-rules-interpretation 
- https://www.spcforexcel.com/knowledge/control-chart-basics/applying-out-of-control-tests
- https://qi.elft.nhs.uk/wp-content/uploads/2018/10/Mohammed-et-al-2008-Plotting-basic-control-charts.pdf
    
'''    
 
    
class SPC:
 
    def __init__(self, data_in, target_col, date_col, chart_type, change_dates=None, baseline_date=None, sample_size=None):
        
 
        """                                                                                                   
                                                                             
        This class does the following SPC analysis steps:
        
            - Takes in pandas dataframe, with a date column and a target column to analyse 
            (note, some charts require a third column ("p-chart" & "u-chart"), 'n', giving the sample size).
            
            - Calculates control lines (for the specified SPC chart).
                
            - Evaluates the data alongside 8 rules, which detects potential special cause variation.
            
            - Returns an interactive SPC chart (in Plotly) and the data needed to build your own chart.
        
        NOTE: You need >= 15 data points to use this tool.
        
        Args:
        
            data_in (pandas.DataFrame): Data to analyse.
            
            target_col (str): Name of target column.
            
            date_col (str): Name of date column.
            
            chart_type (str): Choose from:
                 - "XmR-chart"
                 - "Individual-chart"
                 - "p-chart"  
                 - "c-chart"
                 - "u-chart"
                 - "XbarR-chart"
                 - "XbarS-chart"  
                 
             change_dates (list of str) (OPTIONAL): List of dates, which each represent a change in the underlying
             process being analysed. This will mean control lines will be re-calculated after each date in the list.
             
             baseline_date (str) (OPTIONAL): Data before this will be used to calculate control lines, and data after,
             will be ignored in the control lines calculation.
             
             sample_size (int): Required if using "XbarR-chart" or "XbarS-chart".             
        
        """
 
        self.rules_list_x = None
        self.rules_list_y = None
        self.dict_rules_x = None
        self.dict_rules_y = None
        self.formatted_data_x = None
        self.formatted_data_y = None
        self.target_col_x = None
        self.target_col_y = None
        
        self.change_dates = change_dates
        self.data_in = data_in.copy()
        self.target_col = target_col
        self.date_col = date_col
        self.chart_type = chart_type
        self.baseline_date = baseline_date
        self.sample_size = sample_size
        
        
    # -------------------------
    # -** UTILITY FUNCTIONS **-
    # -------------------------
 
    def rules_func(input_df, target_col):
        
        
        """ 
        
        Checks up to 8 SPC rules. Not all rules are suitable for all charts, therefore, fewer rules will
        be tested in these instances.
        
        Args:
            input_df (pandas.DataFrame): Data to analyse.
            target_col (str): Name of target column.

        Returns:
            dict: Dictionary of rule violations with Rule 1-8 as keys, and dates as values.

        """
        
        
        violations = {}

        # Rule 1: Any point outside the control limits
        rule1 = (input_df[target_col] > input_df['ucl']) | (input_df[target_col] < input_df['lcl'])
        violations['Rule 1 violation'] = input_df.index[rule1].tolist()

        # Rule 2: Two out of three consecutive points beyond the +-2 standard deviation lines
        rule2 = []
        for i in range(2, len(input_df)):
            subset = input_df.iloc[i-2:i+1]
            if ((subset[target_col] > subset['+2sd']).sum() >= 2) or ((subset[target_col] < subset['-2sd']).sum() >= 2):
                rule2.append(input_df.index[i])
        violations['Rule 2 violation'] = rule2

        # Rule 3: Four out of five consecutive points beyond the +-1 standard deviation lines
        rule3 = []
        for i in range(4, len(input_df)):
            subset = input_df.iloc[i-4:i+1]
            if ((subset[target_col] > subset['+1sd']).sum() >= 4) or ((subset[target_col] < subset['-1sd']).sum() >= 4):
                rule3.append(input_df.index[i])
        violations['Rule 3 violation'] = rule3

        # Rule 4: Eight consecutive points on the same side of the cl line
        rule4 = []
        for i in range(7, len(input_df)):
            subset = input_df.iloc[i-7:i+1]
            if (subset[target_col] > subset['cl']).all() or (subset[target_col] < subset['cl']).all():
                rule4.append(input_df.index[i])
        violations['Rule 4 violation'] = rule4

        # Rule 5: Six consecutive points steadily increasing or decreasing
        rule5 = []
        for i in range(5, len(input_df)):
            subset = input_df.iloc[i-5:i+1]
            if np.all(np.diff(subset[target_col]) > 0) or np.all(np.diff(subset[target_col]) < 0):
                rule5.append(input_df.index[i])
        violations['Rule 5 violation'] = rule5

        # Rule 6: Eight points in a row on both sides of the cl line, but none within one standard deviation of the cl line
        rule6 = []
        for i in range(7, len(input_df)):
            subset = input_df.iloc[i-7:i+1]
            within_std_dev = np.abs(subset[target_col] - subset['cl']) <= subset['+1sd'] - subset['cl']
            if np.all(np.sign(subset[target_col] - subset['cl']) != np.sign(subset['cl'])) and not np.any(within_std_dev):
                rule6.append(input_df.index[i])
        violations['Rule 6 violation'] = rule6

        # Rule 7: Fifteen points in a row within one standard deviation of the cl line
        rule7 = []
        for i in range(14, len(input_df)):
            subset = input_df.iloc[i-14:i+1]
            if np.all(np.abs(subset[target_col] - subset['cl']) <= subset['+1sd'] - subset['cl']):
                rule7.append(input_df.index[i])
        violations['Rule 7 violation'] = rule7

        # Rule 8: Fourteen points alternating up and down
        rule8 = []
        for i in range(13, len(input_df)):
            subset = input_df.iloc[i-13:i+1]
            diff = np.diff(subset[target_col])
            if np.all(diff[:-1] * diff[1:] < 0):
                rule8.append(input_df.index[i])
        violations['Rule 8 violation'] = rule8

        return violations

    def clean_time_series_data(self, data, date_column=None):
        
        """ 
        
        Checks data for any data quality issues.
        
        Args:
            data (pandas.DataFrame): Data to analyse.
            date_column (str): Name of date column.

        """
        
        
        # Check if date_column exists in the data
        if date_column not in data.columns:
            raise ValueError(f"Date column {date_column} not found in the data.")

        # Check if date_column is in datetime format and convert if required
        if not pd.api.types.is_datetime64_any_dtype(data[date_column]):
            data[date_column] = pd.to_datetime(data[date_column], errors='coerce')

        # Check if the date_column is the index and set it as the index if not
        if data.index.name != date_column:
            data.set_index(date_column, inplace=True)

        # Check for missing data
        missing_values = data.isnull().sum()

        if missing_values.any():
            print("Missing values detected:")
            print(missing_values)
            
    
    # -----------------------
    # -** MAIN CLASS CODE **-
    # -----------------------
 
    
    def setup(self):
        
        """ 
        
        Function enabling multiple runs of the setup_single_run() method. This is to allow 
        for control lines to be calculated multiple times (if specified by user using the change_dates parameter).
        
        If change_dates is not specified, it runs only once.
        

        """
       
        # Firstly, we check for any DQ issues.
        self.clean_time_series_data(self.data_in, self.date_col)
        
        # Check input arguments to determine number of runs of the setup_single_run() method.
        if self.change_dates is None:
            
            formatted_x_out, formatted_y_out = self.setup_single_run(data = self.data_in)
            self.formatted_data_x = formatted_x_out
            self.formatted_data_y = formatted_y_out
        else:
            list_dates = [self.data_in.index[0]] + self.change_dates + [self.data_in.index[-1]]
            list_dataframes=[]
            for idx in range(0, len(list_dates)-1):
                if idx == len(list_dates)-2:
                    list_dataframes.append(self.data_in.loc[list_dates[idx]:(pd.to_datetime(list_dates[idx+1]))])
                else:
                    list_dataframes.append(self.data_in.loc[list_dates[idx]:(pd.to_datetime(list_dates[idx+1]) -\
                                                                             pd.DateOffset(days=1))])
                    
            formatted_x=[]
            formatted_y=[]
            for data in list_dataframes:
                formatted_x_out, formatted_y_out = self.setup_single_run(data = data)
                formatted_x.append(formatted_x_out)
                formatted_y.append(formatted_y_out)
            self.formatted_data_x = pd.concat(formatted_x)
            if all(x is None for x in formatted_y):
                self.formatted_data_y = None
            else:
                self.formatted_data_y = pd.concat(formatted_y)
                
                
    
    def setup_single_run(self, data):
 
        """
        
       Type of SPC chart currently available:
       "XmR-chart", "Individual-chart", "p-chart",  "c-chart", "u-chart", "XbarR-chart", XbarS-chart"
 
       !!Can be extended to include others in the future!!
 
       Returns dataframe with control limits, upper/lower as well zones A, B, C which are the 3 zones between the
       upper/lower limits and the center line.
       
        Args:
            data_in (pandas.DataFrame): Data input.
            chart_type (str): SPC chart type.

        Returns:
            self.pandas.DataFrame: Pandas dataframe with control limits for each chart.
 
       """
 
        # Reference dictionary for X_bar chart control limits calculations. Different sample size will result in
        # different control limits for the xbar charts.
 
        x_bar_vals = {'A2': {2: '1.88', 3: '1.023', 4: '0.729', 5: '0.577', 6: '0.483', 7: '0.419',
                             8: '0.373', 9: '0.337', 10: '0.308', 11: '0.285', 12: '0.266',
                             13: '0.249', 14: '0.235', 15: '0.223', 16: '0.212', 17: '0.203',
                             18: '0.194', 19: '0.187', 20: '0.18', 21: '0.173', 22: '0.167',
                             23: '0.162', 24: '0.157', 25: '0.153'},
                      'A3': {2: '2.659', 3: '1.954', 4: '1.628', 5: '1.427', 6: '1.287', 7: '1.182',
                             8: '1.099', 9: '1.032', 10: '0.975', 11: '0.927', 12: '0.886', 13: '0.85',
                             14: '0.817', 15: '0.789', 16: '0.763', 17: '0.739', 18: '0.718',
                             19: '0.698', 20: '0.68', 21: '0.663', 22: '0.647', 23: '0.633',
                             24: '0.619', 25: '0.606'},
                      'd2': {2: '1.128', 3: '1.693', 4: '2.059', 5: '2.326', 6: '2.534', 7: '2.704',
                             8: '2.847', 9: '2.97', 10: '3.078', 11: '3.173', 12: '3.258', 13: '3.336',
                             14: '3.407', 15: '3.472', 16: '3.532', 17: '3.588', 18: '3.64', 19: '3.689',
                             20: '3.735', 21: '3.778', 22: '3.819', 23: '3.858', 24: '3.895',
                             25: '3.931'},
                      'D3': {2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0.076', 8: '0.136',
                             9: '0.184', 10: '0.223', 11: '0.256', 12: '0.283', 13: '0.307',
                             14: '0.328', 15: '0.347', 16: '0.363', 17: '0.378', 18: '0.391',
                             19: '0.403', 20: '0.415', 21: '0.425', 22: '0.434', 23: '0.443',
                             24: '0.451', 25: '0.459'},
                      'D4': {2: '3.267', 3: '2.574', 4: '2.282', 5: '2.114', 6: '2.004', 7: '1.924',
                             8: '1.864', 9: '1.816', 10: '1.777', 11: '1.744', 12: '1.717',
                             13: '1.693', 14: '1.672', 15: '1.653', 16: '1.637', 17: '1.622',
                             18: '1.608', 19: '1.597', 20: '1.585', 21: '1.575', 22: '1.566',
                             23: '1.557', 24: '1.548', 25: '1.541'},
                      'B3': {2: '0', 3: '0', 4: '0', 5: '0', 6: '0.03', 7: '0.118', 8: '0.185',
                             9: '0.239', 10: '0.284', 11: '0.321', 12: '0.354', 13: '0.382',
                             14: '0.406', 15: '0.428', 16: '0.448', 17: '0.466', 18: '0.482',
                             19: '0.497', 20: '0.51', 21: '0.523', 22: '0.534', 23: '0.545',
                             24: '0.555', 25: '0.565'},
                      'B4': {2: '3.267', 3: '2.568', 4: '2.266', 5: '2.089', 6: '1.97',
                             7: '1.882', 8: '1.815', 9: '1.761', 10: '1.716', 11: '1.679',
                             12: '1.646', 13: '1.618', 14: '1.594', 15: '1.572', 16: '1.552',
                             17: '1.534', 18: '1.518', 19: '1.503', 20: '1.49', 21: '1.477',
                             22: '1.466', 23: '1.455', 24: '1.445', 25: '1.435'}}
    
        # If we're not using baseline data, we set baseline data to last value of input data.
        if self.change_dates is not None:
            self.baseline_date = data.index[-1]
        
        if (self.baseline_date is None) & (self.change_dates is None):
            self.baseline_date = data.index[-1]

        if (self.chart_type == 'Individual-chart') or (self.chart_type == 'XmR-chart'):

            baseline_data = data.copy().loc[:pd.to_datetime(self.baseline_date), :]
            baseline_data['mR'] = data[self.target_col].diff().abs().loc[:pd.to_datetime(self.baseline_date)]
    
            # Individual chart
            data_I = data.copy()
            data_I['cl'] = baseline_data[self.target_col].mean()
            data_I['lcl'] = baseline_data[self.target_col].mean() - 3 * (
                    (baseline_data['mR'].iloc[1:len(baseline_data['mR'])]) /
                    1.128).mean()
            data_I['ucl'] = baseline_data[self.target_col].mean() + 3 * (
                    (baseline_data['mR'].iloc[1:len(baseline_data['mR'])]) /
                    1.128).mean()
            data_I['+1sd'] = baseline_data[self.target_col].mean() + 1 * (
                    (baseline_data['mR'].iloc[1:len(baseline_data['mR'])]) /
                    1.128).mean()
            data_I['-1sd'] = baseline_data[self.target_col].mean() - 1 * (
                    (baseline_data['mR'].iloc[1:len(baseline_data['mR'])]) /
                    1.128).mean()
            data_I['+2sd'] = baseline_data[self.target_col].mean() + 2 * (
                    (baseline_data['mR'].iloc[1:len(baseline_data['mR'])]) /
                    1.128).mean()
            data_I['-2sd'] = baseline_data[self.target_col].mean() - 2 * (
                    (baseline_data['mR'].iloc[1:len(baseline_data['mR'])]) /
                    1.128).mean()
    
            # mR chart
            data_mR = data.copy()
            data_mR['r'] = data[self.target_col].diff().abs().values
            data_mR['cl'] = baseline_data['mR'].mean()
            data_mR['lcl'] = baseline_data['mR'].mean() - 3 * ((baseline_data['mR'].iloc[1:len(baseline_data['mR'])])
                                                               * 0.8525).mean()
            data_mR['ucl'] = baseline_data['mR'].mean() + 3 * ((baseline_data['mR'].iloc[1:len(baseline_data['mR'])])
                                                               * 0.8525).mean()
            data_mR['+1sd'] = baseline_data['mR'].mean() - 1 * ((baseline_data['mR'].iloc[1:len(baseline_data['mR'])])
                                                                * 0.8525).mean()
            data_mR['-1sd'] = baseline_data['mR'].mean() + 1 * ((baseline_data['mR'].iloc[1:len(baseline_data['mR'])])
                                                                * 0.8525).mean()
            data_mR['+2sd'] = baseline_data['mR'].mean() - 2 * ((baseline_data['mR'].iloc[1:len(baseline_data['mR'])])
                                                                * 0.8525).mean()
            data_mR['-2sd'] = baseline_data['mR'].mean() + 2 * ((baseline_data['mR'].iloc[1:len(baseline_data['mR'])])
                                                                * 0.8525).mean()
            # Check lcl doesn't fall below 0.
            if data_mR['lcl'][0]<0:
                data_mR['lcl']=0
    
            if self.chart_type == 'Individual-chart':
                return data_I, None
            
            elif self.chart_type == 'XmR-chart':
                return data_I, data_mR
    
    
        elif self.chart_type == 'XbarR-chart':
    
            data_x_bar = data.copy().reset_index(drop=False)
            x_bar_df = data_x_bar.groupby(by=self.date_col).mean().reset_index(drop=False).rename(
                columns={self.target_col: 'x_bar'})
            x_bar_df['r'] = data_x_bar.groupby(by=self.date_col).max()[self.target_col].values - \
                            data_x_bar.groupby(by=self.date_col).min()[
                                self.target_col].values
    
            df_r = x_bar_df[['r', self.date_col]].set_index(self.date_col, \
                                                            drop=True).rename(columns={'x_bar': self.target_col})
            df_out = x_bar_df[['x_bar', self.date_col]].set_index(self.date_col, \
                                                                  drop=True).rename(columns={'x_bar': self.target_col})
            df_out['cl'] = df_out.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean()
            df_out['lcl'] = df_out.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - float(
                x_bar_vals['A2'][self.sample_size]) * \
                            df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean()
            df_out['ucl'] = df_out.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + float(
                x_bar_vals['A2'][self.sample_size]) * \
                            df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean()
    
            # Value to get each zone (A, B, C)
            zone = ((df_out['ucl'] - df_out['cl']) / 3)[0]
    
            df_out['+1sd'] = df_out['cl'] + zone
            df_out['-1sd'] = df_out['cl'] - zone
            df_out['+2sd'] = df_out['cl'] + 2 * zone
            df_out['-2sd'] = df_out['cl'] - 2 * zone
    
            # Check lcl doesn't fall below 0.
            df_out['lcl'] = [x if x > 0 else 0 for x in df_out['lcl']]
    
            df_out_R = pd.DataFrame()
            df_out_R[self.date_col] = x_bar_df[self.date_col].values
            df_out_R['r'] = x_bar_df['r'].values
            df_out_R['cl'] = df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean()
            df_out_R['lcl'] = df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean() * float(
                x_bar_vals['D3'][self.sample_size])
            df_out_R['ucl'] = df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean() * float(
                x_bar_vals['D4'][self.sample_size])
    
            zone_R = ((df_out_R['ucl'] - df_out_R['cl']) / 3)[0]
    
            df_out_R['+1sd'] = df_out_R['cl'] + zone_R
            df_out_R['-1sd'] = df_out_R['cl'] - zone_R
            df_out_R['+2sd'] = df_out_R['cl'] + 2 * zone_R
            df_out_R['-2sd'] = df_out_R['cl'] - 2 * zone_R
    
            df_out_R = df_out_R.set_index(self.date_col, drop=True)
        
            if df_out_R['lcl'][0]<0:
                df_out_R['lcl']=0
            
            return df_out, df_out_R
    
        elif self.chart_type == 'XbarS-chart':
    
            data_x_bar = data.copy().reset_index(drop=False)
    
            x_bar_df = data_x_bar.groupby(by=self.date_col).mean().reset_index(drop=False).rename(
                columns={self.target_col: 'x_bar'})
            x_bar_df['r'] = data_x_bar.groupby(by=self.date_col).max()[self.target_col].values - \
                            data_x_bar.groupby(by=self.date_col).min()[
                                self.target_col].values
    
            df_r = x_bar_df[['r', self.date_col]].set_index(self.date_col, drop=True).rename(columns={'x_bar': self.target_col})
            df_out = x_bar_df[['x_bar', self.date_col]].set_index(self.date_col, \
                                                                  drop=True).rename(columns={'x_bar': self.target_col})
            df_out['cl'] = df_out.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean()
            df_out['lcl'] = df_out.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - float(
                x_bar_vals['A3'][self.sample_size]) * \
                            df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean()
            df_out['ucl'] = df_out.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + float(
                x_bar_vals['A3'][self.sample_size]) * \
                            df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean()
    
            zone = ((df_out['ucl'] - df_out['cl']) / 3)
    
            df_out['+1sd'] = df_out['cl'] + zone
            df_out['-1sd'] = df_out['cl'] - zone
            df_out['+2sd'] = df_out['cl'] + 2 * zone
            df_out['-2sd'] = df_out['cl'] - 2 * zone
    
            # Check lcl doesn't fall below 0.
            df_out['lcl'] = [x if x > 0 else 0 for x in df_out['lcl']]
    
            df_out_S = pd.DataFrame()
            df_out_S[self.date_col] = x_bar_df[self.date_col].values
            df_out_S['r'] = x_bar_df['r'].values
            df_out_S['cl'] = df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean()
            df_out_S['lcl'] = df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean() * float(
                x_bar_vals['B3'][self.sample_size])
            df_out_S['ucl'] = df_r.loc[:pd.to_datetime(self.baseline_date)]['r'].mean() * float(
                x_bar_vals['B4'][self.sample_size])
    
            zone_R = ((df_out_S['ucl'] - df_out_S['cl']) / 3)
    
            df_out_S['+1sd'] = df_out_S['cl'] + zone_R
            df_out_S['-1sd'] = df_out_S['cl'] - zone_R
            df_out_S['+2sd'] = df_out_S['cl'] + 2 * zone_R
            df_out_S['-2sd'] = df_out_S['cl'] - 2 * zone_R
            
            # Check lcl doesn't fall below 0.
            if df_out_S['lcl'][0]<0:
                df_out_S['lcl']=0
    
            df_out_S = df_out_S.set_index(self.date_col, drop=True)
        
            return df_out, df_out_S
    
        elif self.chart_type == 'c-chart':
    
            data_in = data.copy()
    
            data_in['cl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean()
            data_in['lcl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - \
                             (3 * ((data_in[self.target_col].mean()) ** 0.5))
            data_in['ucl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + \
                             (3 * ((data_in[self.target_col].mean()) ** 0.5))
    
            # Check lcl doesn't fall below 0.
            data_in['lcl'] = [x if x > 0 else 0 for x in data_in['lcl']]
    
            data_in['+1sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + \
                              (1 * ((data_in[self.target_col].mean()) ** 0.5))
            data_in['-1sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - \
                              (1 * ((data_in[self.target_col].mean()) ** 0.5))
            data_in['+2sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + \
                              (2 * ((data_in[self.target_col].mean()) ** 0.5))
            data_in['-2sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - \
                              (2 * ((data_in[self.target_col].mean()) ** 0.5))
            
            return data_in, None

    
        elif self.chart_type == 'p-chart':
    
            data_in = data.copy()
    
            data_in[self.target_col] = data_in[self.target_col] / data_in['n']
    
            data_in['cl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean()
            data_in['lcl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - 3 * (
                    (data_in[self.target_col].mean() *
                     (1 - data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean())) /
                    data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['ucl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + 3 * (
                    (data_in[self.target_col].mean() * (
                            1 - data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean())) /
                    data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['+1sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + 1 * (
                    (data_in[self.target_col].mean() *
                     (1 - data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean())) /
                    data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['-1sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - 1 * (
                    (data_in[self.target_col].mean() * (
                            1 - data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean())) /
                    data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['+2sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + 2 * (
                    (data_in[self.target_col].mean() *
                     (1 - data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean())) /
                    data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['-2sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - 2 * (
                    (data_in[self.target_col].mean() * (
                            1 - data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean())) /
                    data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            # Check lcl doesn't fall below 0.
            data_in['lcl'] = [x if x > 0 else 0 for x in data_in['lcl']]
            
            return data_in, None
    
    
        elif self.chart_type == 'u-chart':
    
            data_in = data.copy()
        
            data_in[self.target_col] = data_in[self.target_col]/data_in['n']
            
            data_in['cl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean()
            data_in['lcl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - 3 * \
                             (data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() /
                              data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
            data_in['ucl'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + 3 * \
                             (data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() /
                              data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['+1sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + 1 * \
                              (data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() /
                               data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['-1sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - 1 * \
                              (data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() /
                               data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['+2sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() + 2 * \
                              (data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() /
                               data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            data_in['-2sd'] = data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() - 2 * \
                              (data_in.loc[:pd.to_datetime(self.baseline_date)][self.target_col].mean() /
                               data_in.loc[:pd.to_datetime(self.baseline_date)]['n']) ** 0.5
    
            # Check lcl doesn't fall below 0.
            data_in['lcl'] = [x if x > 0 else 0 for x in data_in['lcl']]
            
            return data_in, None
    
        else:
            print('Chart type must be one of "XmR-chart", "Individual-chart", "p-chart",  "c-chart", "u-chart"'
                  '"XbarR-chart", XbarS-chart"')
 
    def check_rules(self):
 
        """
 
        Requires setup() method to be called first.
        
        Checks the calcualted control lines, and tests up to 8 rules.
 
        """
 
        if self.chart_type in ("XmR-chart", "XbarR-chart", "XbarS-chart"):
            self.target_col_x = self.target_col
            self.target_col_y = 'r'
        else:
            self.target_col_x = self.target_col
            self.target_col_y = None
 
        # Check rules for both graphs (checking second graph data is not None)
        self.dict_rules_x = SPC.rules_func(self.formatted_data_x, self.target_col_x)
        if self.formatted_data_y is None:
            self.dict_rules_y = None
        else:
            self.dict_rules_y = SPC.rules_func(self.formatted_data_y, self.target_col_y)
 
        # Defining rules applicable to each SPC chart type.
        if self.chart_type in ('XmR-chart', 'Individual-chart', 'XbarR-chart', 'XbarS-chart'):
            self.rules_list_x = ['Rule 1 violation', 'Rule 2 violation', 'Rule 3 violation', 'Rule 4 violation',
                                 'Rule 5 violation', 'Rule 6 violation', 'Rule 7 violation', 'Rule 8 violation']
        elif self.chart_type in ('p-chart', 'u-chart', 'c-chart'):
            self.rules_list_x = ['Rule 1 violation', 'Rule 4 violation', 'Rule 5 violation', 'Rule 8 violation']
 
        if self.dict_rules_y is not None:
            self.rules_list_y = ['Rule 1 violation', 'Rule 4 violation', 'Rule 5 violation', 'Rule 8 violation']
        else:
            self.rules_list_y = None
            
 
    def plot_spc(self, title='SPC Chart'):
        
        """
        
        Requires setup() & check_rules() methods to be called first. 
        
        Returns Plotly interactive plots for chosen SPC chart.
        
        """
 
        changepoint = self.baseline_date
    
        # This will create charts for SPC with only one chart.
        if self.formatted_data_y is None:
 
            data = self.formatted_data_x
 
            rules_dict_first = self.dict_rules_x
            rules_list_first = self.rules_list_x
 
            fig = px.line(x=data.index,
                          y=data[self.target_col],
                          markers=False)
 
            fig.add_scatter(x=data.index, y=data['cl'], line_width=3, opacity=0.5, line_dash='dash', line_color='green',
                            name='CENTRAL LINE')
            fig.add_scatter(x=data.index, y=data['lcl'], line_width=2, opacity=0.5, line_dash='dash', line_color='red',
                            name='LOWER CONTROL LINE')
            fig.add_scatter(x=data.index, y=data['ucl'], line_width=2, opacity=0.5, line_dash='dash', line_color='red',
                            name='UPPER CONTROL LINE')
 
            for idx, rule in enumerate(rules_list_first):
                fig.add_trace(
                    go.Scatter(name=rule, x=rules_dict_first[rule], y=data.loc[rules_dict_first[rule]][self.target_col],
                               mode='markers',
                               marker=dict(symbol='circle-open', opacity=1,
                                           size=12,
                                           line=dict(width=3))))
 
            fig['layout']['xaxis']['title'] = 'Date'
            fig['layout']['yaxis']['title'] = ''
            fig.update_layout(title=title)
 
            fig['layout']['yaxis'].update(autorange=True)
            fig['layout']['xaxis'].update(autorange=True)
 
            return fig
 
        else:
 
            data = self.formatted_data_x
            data_var = self.formatted_data_y
 
            rules_dict_first = self.dict_rules_x
            rules_list_first = self.rules_list_x
 
            rules_dict_second = self.dict_rules_y
            rules_list_second = self.rules_list_y
 
            fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], shared_xaxes=True, vertical_spacing=0.01)
 
            fig.add_trace(go.Scatter(x=data.index, legendgroup='1',
                                     y=data[self.target_col], line=dict(color="blue"), name='Value'), row=1, col=1)
 
            fig.add_scatter(x=data.index, y=data['cl'], line_width=3, opacity=0.5, line_dash='dash', line_color='green',
                            name='CENTRAL LINE', row=1, col=1, legendgroup='1')
            fig.add_scatter(x=data.index, y=data['lcl'], line_width=2, opacity=0.5, line_dash='dash', line_color='red',
                            name='LOWER CONTROL LINE', row=1, col=1, legendgroup='1')
            fig.add_scatter(x=data.index, y=data['ucl'], line_width=2, opacity=0.5, line_dash='dash', line_color='red',
                            name='UPPER CONTROL LINE', row=1, col=1, legendgroup='1')
 
            for idx, rule in enumerate(rules_list_first):
                fig.add_trace(
                    go.Scatter(name=rule, x=rules_dict_first[rule], y=data.loc[rules_dict_first[rule]][self.target_col],
                               mode='markers',
                               marker=dict(symbol='circle-open', opacity=1,
                                           size=12,
                                           line=dict(width=3)), legendgroup='1'), row=1, col=1)
 
            fig.add_trace(go.Scatter(x=data_var.index,
                                     y=data_var['r'], line=dict(color="grey"), name='Moving Range', legendgroup='2'),
                          row=2, col=1)
 
            fig.add_scatter(x=data_var.index, y=data_var['cl'], line_width=3, opacity=0.5, line_dash='dash',
                            line_color='green',
                            name='CENTRAL LINE', row=2, col=1, legendgroup='2')
            fig.add_scatter(x=data_var.index, y=data_var['lcl'], line_width=2, opacity=0.5, line_dash='dash',
                            line_color='red',
                            name='LOWER CONTROL LINE', row=2, col=1, legendgroup='2')
            fig.add_scatter(x=data_var.index, y=data_var['ucl'], line_width=2, opacity=0.5, line_dash='dash',
                            line_color='red',
                            name='UPPER CONTROL LINE', row=2, col=1, legendgroup='2')
 
            for idx, rule in enumerate(rules_list_second):
                fig.add_trace(go.Scatter(name=rule, x=rules_dict_second[rule],
                                         y=data_var.loc[rules_dict_second[rule]]['r'],
                                         mode='markers',
                                         marker=dict(symbol='circle-open', opacity=1,
                                                     size=12,
                                                     line=dict(width=3)), legendgroup='2'), row=2, col=1)
 

 
            fig.update_layout(title=title, legend_tracegroupgap=45)
 
            fig['layout']['yaxis'].update(autorange=True)
            fig['layout']['xaxis'].update(autorange=True)
 
            return fig

    def return_data(self):
        
        """
        
        Requires setup() & check_rules() methods to be called first.
        
        Returns all data required to build your own SPC chart. Returns two dataframes: First, the data for the
        Variable Control Chart, secondly, the data for the Moving Range Control Chart
        
        Returns:
            self.pandas.DataFrame: Dataframe with data required to build the SPC chart from scratch.                
 
        """
        
        # Formatting datasets
        dictionary_x_first = self.dict_rules_x
        dictionary_x = {key: value for key, value in dictionary_x_first.items() if key in self.rules_list_x}
        df_x = self.formatted_data_x
        
        if self.dict_rules_y is not None:
            dictionary_y_first = self.dict_rules_y
            dictionary_y = {key: value for key, value in dictionary_y_first.items() if key in self.rules_list_y}
            df_y = self.formatted_data_y
        else:
            df_y = None
        
        
        # Function to check if a date exists in the dictionary list
        def check_date(date, date_list):
            return 1 if date in date_list else 0

        # Add columns with string headers and binary representation
        for header, date_list in dictionary_x.items():
            df_x[header] = df_x.reset_index()['ds'].apply(lambda x: check_date(x, date_list)).values
        df_x['chart type'] = 'Variable Control Chart'
        self.data_x = df_x.reset_index()
            
        if df_y is None:
                self.data_y = None
        else:
            for header, date_list in dictionary_y.items():
                df_y[header] = df_y.reset_index()['ds'].apply(lambda x: check_date(x, date_list)).values
            df_y['chart type'] = 'Moving Range Control Chart'

            self.data_y = df_y.reset_index()
            
        # Returning data required to build own SPC charts.
        return self.data_x, self.data_y
            
            
        
        
 
