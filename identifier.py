
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="keras")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow")
import datetime
import time
from pathlib import Path
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import os
import sys
import csv


class CallIdentifier:
    def __init__(self,main_queue, output_path, writer_queue):
        self.analyzer = Analyzer()
        self.queue  = main_queue
        self.writer_queue = writer_queue
        self.output_path = output_path 
        



    def run(self):
        while True:
            filename = self.queue.get()
            try:

                # Save original stdout/stderr
                stdout_orig = sys.stdout
                stderr_orig = sys.stderr

                # Suppress output
                sys.stdout = open(os.devnull, 'w')
                sys.stderr = open(os.devnull, 'w')



                recording = Recording(
                    analyzer=self.analyzer,
                    path=Path(filename),
                    lat=40.9807,  
                    lon=-73.6837,
                    date=datetime.date.today(), # This could be changed but whatever
                    sensitivity=0.1,
                    return_all_detections=False
                )  


                recording.analyze()
                # # Restore original
                sys.stdout.close()
                sys.stderr.close()
                sys.stdout = stdout_orig
                sys.stderr = stderr_orig


                timestamp = time.strftime("%Y%m%d_%H%M%S")
                timestamp2 = time.strftime("%m-%d-%Y %H:%M:%S")
                csv_file = self.output_path + f"/detections_{timestamp}.csv"
                with open(csv_file, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "common_name", "confidence"])
                    for d in recording.detections:
                        writer.writerow([
                            f"{timestamp2}",
                            d['common_name'],
                            f"{d['confidence']:.3f}"
                        ])


                self.writer_queue.put(csv_file)
                for d in recording.detections:
                    print(
                        f"[{timestamp2}]"
                        f"{d['common_name']} | "
                        f"{d['confidence']:.3f}"
                    )
            finally:
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")
                self.queue.task_done()