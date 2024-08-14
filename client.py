
# Tasks -
# 8 threads/processes will be sending requests to the server
# Each thread or process should send 100 randome requests to the server
# For each request that is sent individually from each thread, we randomly choose between SetNum or Fact
# For each request that is individually sent from a thread or a process, we randomly choose a key between 1 and 100 {100 possible keys}
# for the SetNum request, we randomly select a number between 1 and 15



# requirements of client.py are to - print cache hit rate, print p50 response time, print p99 response time, 

import grpc
import numstore_pb2
import numstore_pb2_grpc
import random
import time
import threading
import numpy as np
import argparse
from datetime import datetime


# Define the 100 possible keys and the 15 possible values of the key-value pairs
keys = [key_val for key_val in range(1, 101)]
values = [val for val in range(1, 16)]

# Define the number of threads that will sending requests to the server
num_threads = 8
num_requests = 100

# Defining locks for responses and cache hits to prevent multiple threads from accessing the same resource
response_lock = threading.Lock()
cache_hit_lock = threading.Lock()


# function statistics to calculate p50 and p99 response times
response_times = [] # to store the response times of each request
cache_hits = 0 # to keep a track of the number of cache hits


# creating a remote procedure call client
def rpc_call(port):
    channel = grpc.insecure_channel(f'localhost:{port}')
    stub = numstore_pb2_grpc.NumStoreStub(channel)
    return stub


# function to send random requests to the server
def send_requests(port):
    global cache_hits
    stub = rpc_call(port)
    for _ in range(num_requests):
        key = str(random.choice(keys))
        # Randomly choose between SetNum or Fact
        if random.choice([0,1]) == 0:
            value = random.choice(values)
            try:
                start = time.time()
                response = stub.SetNum(numstore_pb2.SetNumRequest(key=key, value=value))
                end = time.time()
                # print(response) # line to debug response attribute error
                with response_lock:
                    response_times.append(end-start)
            except grpc.RpcError as e:
                print(f"Error during SetNum request for key {key}: {e}")
            

        else: 
            try:
                start = time.time()
                response = stub.Fact(numstore_pb2.FactRequest(key=key))
                end = time.time()
                # print(response) # line to debug response attribute error
            
                with response_lock:
                    response_times.append(end-start)
                if response.hit == True:
                    with cache_hit_lock:
                        cache_hits += 1
            except grpc.RpcError as e:
                print(f"Error during Fact request for key {key}: {e}")
            


def main():
    parser = argparse.ArgumentParser(description='Client for sending requests to the server.')
    parser.add_argument('port', type=int, help='Port number of the server')
    args = parser.parse_args()
    port = args.port

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=send_requests, args=(port,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Calculate the p50 and p99 response times
    response_times_np = np.array(response_times)
    if len(response_times_np) > 0:
        p50_response_time = np.percentile(response_times_np, 50)
        p99_response_time = np.percentile(response_times_np, 99)
        cache_hit_rate = (cache_hits / (num_threads * num_requests)) * 100

        # Print results
        print(f'Cache Hit Rate: {cache_hit_rate:.2f}%')
        print(f'p50 Response Time: {p50_response_time:.4f} seconds')
        print(f'p99 Response Time: {p99_response_time:.4f} seconds')
    else:
        print('No response times recorded.')


if __name__ == "__main__":
    main()