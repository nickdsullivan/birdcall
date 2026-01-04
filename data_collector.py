



import matplotlib
matplotlib.use("Agg")  # ← REQUIRED for servers


import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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


		self.info = pd.read_csv("bird_info/bird_info.csv", low_memory=False)

	def create_chart(self, start_time, end_time, frequency, smoothing_frequency):
		# print("In method")

		# smoothed = self.df.copy()

		# # Optional smoothing
		# if smoothing_frequency != "":
		# 	smoothed = smoothed.groupby(pd.Grouper(freq=smoothing_frequency)).sum()
		# 	smoothed = (smoothed > 0).astype(int)

		# # Aggregate to requested frequency
		# grouped = smoothed.groupby(pd.Grouper(freq=frequency)).sum()

		# # Parse times
		# start_time = pd.to_datetime(start_time, format="%m-%d-%Y %H:%M:%S")
		# end_time = pd.to_datetime(end_time, format="%m-%d-%Y %H:%M:%S")
			
		# # Build full time index at SAME frequency
		# full_index = pd.date_range(start=start_time, end=end_time, freq=frequency)

		# # Reindex → fill missing with 0
		# df_final = grouped.reindex(full_index, fill_value=0)

		# # Ensure bird columns are ints (safe)
		# df_final = df_final.astype(int)

		# non_zero_rows = df_final[(df_final != 0).any(axis=1)]
		# print(non_zero_rows)
		smoothed = self.df.copy()
		if smoothing_frequency !="":
			smoothed = smoothed.groupby(pd.Grouper(freq=smoothing_frequency)).sum()
			smoothed = (smoothed > 0).astype(int)
		grouped_df = smoothed.groupby(pd.Grouper(freq=frequency)).sum().reset_index()
		
		start_time = pd.to_datetime(start_time, format="%m-%d-%Y %H:%M:%S")
		end_time = pd.to_datetime(end_time, format="%m-%d-%Y %H:%M:%S")
		time_range = pd.date_range(start=start_time, end=end_time, freq=frequency)
		df_time_range = pd.DataFrame(index=time_range)
		grouped_df = grouped_df[grouped_df["timestamp"] >= start_time]
		grouped_df= grouped_df.set_index("timestamp")
		# grouped_df.index = grouped_df.index.floor(frequency)
		# grouped_df = grouped_df.reindex(time_range, fill_value=0).astype(int)
		df_merged = pd.concat([grouped_df, df_time_range], axis=1)
		df_merged = pd.merge(
	        grouped_df,
	        df_time_range,
	        left_index=True,
	        right_index=True,
	        how="outer"
	    )
		df_merged = grouped_df.fillna(0).astype(int)




		df_merged.to_csv("chart_data/test.csv")
		# # --------- Plot ---------
		plt.figure(figsize=(14, 6))
		for col in df_merged.columns:
			if col != "timestamp":
				plt.plot(df_merged.index, df_merged[col], label=col)

		plt.xlabel("Time")
		plt.ylabel("Detections")
		plt.title("Bird Call Detections")

		ax = plt.gca()
		ax.xaxis.set_major_formatter(
		    mdates.DateFormatter('%I:%M %p %m/%d')
		)

		plt.xticks(rotation=45)
		plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
		plt.tight_layout()

		# Save chart for website
		plt.savefig("static/chart.png", dpi=150)
		plt.close()

		return df_merged

