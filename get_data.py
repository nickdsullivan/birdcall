import pandas as pd
from datetime import timedelta



class DataCollector:
    def __init__(self, data):
        self.df = pd.read_csv('output/output.csv')
        self.df["timestamp"] = pd.to_datetime(
        self.df["timestamp"],
            format="%m-%d-%Y %H:%M:%S"
        )
        self.df = self.df.pivot_table(index='timestamp', columns='common_name', values='confidence')
        self.df.columns.name = None
        self.df = (self.df.fillna(0) >= 0.1).astype(int)
        self.df = self.df.drop(columns=self.df.columns[(self.df == 0).all()])


        self.info = pd.read_csv("bird_info/bird_info.csv")

    def create_chart(self, start_time, end_time, frequency, smoothing_frequency):
        """
        Create a chart by aggregating time-series data within a specified time range.
        
        This method groups bird call data by a specified frequency, optionally applies
        smoothing, and generates a complete time series with no missing values.
        
        Args:
            start_time (str): The start time for the chart in format "%m-%d-%Y %H:%M:%S".
            end_time (str): The end time for the chart in format "%m-%d-%Y %H:%M:%S".
            frequency (str): The frequency for grouping data (e.g., '1H', '1D', '1T').
            smoothing_frequency (str): The frequency for smoothing data before grouping.
                                       If empty string, no smoothing is applied.
        
        Returns:
            pd.DataFrame: A DataFrame indexed by time with no missing values in the
                          specified range, filled with zeros where data is absent.
                          Also saved to 'output/chart_data.csv'.
        
        Example:
            >>> chart = create_chart('01-01-2023 00:00:00', '01-02-2023 23:59:59', '1H', '1T')
        """

        smoothed = self.df.copy()
        if smoothing_frequency !="":
            smoothed = smoothed.groupby(pd.Grouper(freq=smoothing_frequency)).sum()
            smoothed = (smoothed > 0).astype(int)
        grouped_df = smoothed.groupby(pd.Grouper(freq=frequency)).sum().reset_index()
        start_time = pd.to_datetime(start_time, format="%m-%d-%Y %H:%M:%S")
        end_time = pd.to_datetime(end_time, format="%m-%d-%Y %H:%M:%S")

        time_range = pd.date_range(start=start_time, end=end_time, freq='1T')
        df_time_range = pd.DataFrame(index=time_range)

        df_merged = pd.concat([grouped_df, df_time_range], axis=1)
        df_merged = df_merged.fillna(0).astype(int)

        df_merged.to_csv('chart_data/chart_data.csv')

        return df_merged