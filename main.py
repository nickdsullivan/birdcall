import threading
import queue
import time
from listener import UDPListener
from identifier import CallIdentifier
from csv_writer import CSVWriter
duration = 3
audio_queue = queue.Queue(maxsize=10)
writer_queue = queue.Queue(maxsize=10)



listener = UDPListener(output_path="audios", main_queue=audio_queue, DURATION = duration)
identifier = CallIdentifier(audio_queue, output_path="raw_csvs", writer_queue=writer_queue)
csv_writer = CSVWriter(output_path="output",writer_queue=writer_queue)

listener_thread = threading.Thread(
    target=listener.run,
    daemon=True
)

identifier_thread = threading.Thread(
    target=identifier.run,
    daemon=True
)
csv_writer_thread = threading.Thread(
    target=csv_writer.run,
    daemon=True
)

listener_thread.start()
identifier_thread.start()
csv_writer_thread.start()
print("Listener and identifier are running... Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")