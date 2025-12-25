import pandas as pd
import os
from datetime import datetime
class CSVWriter:
    def __init__(self, writer_queue, output_path="processed_csvs"):
        self.writer_queue = writer_queue
        self.output_path = output_path

    def run(self):
        # now = datetime.now()
        # year = now.strftime("%Y")
        # month = now.strftime("%m")
        # day = now.strftime("%d")
        # current_output_path = os.path.join(self.output_path, f"{year}", f"{month}", f"{day}")
        # os.makedirs(os.path.join(self.output_path, f"{year}", f"{month}", f"{day}"), exist_ok=True)
        csv_file = os.path.join(self.output_path, "output.csv")
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
        else:
            df = pd.DataFrame(columns=["timestamp", "common_name", "confidence"])
        while True:
            try:
                filename = self.writer_queue.get()
                temp_df = pd.read_csv(filename)
                if temp_df.empty:
                    continue
                df = pd.concat([df, temp_df], ignore_index=True)
                df.to_csv(csv_file, index=False)

            finally:
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")

                self.writer_queue.task_done()