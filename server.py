import numstore_pb2_grpc
import numstore_pb2
from concurrent import futures
import grpc
import math
from collections import OrderedDict
from threading import Lock

server_dict = {} # store the key-value pairs here
factorial_cache_dict = OrderedDict() # Cache for storing the factorial results here
lock = Lock()

class RouteGuideServer(numstore_pb2_grpc.NumStoreServicer):
    def SetNum(self, request, context):
        # store the key-value pairs here

        try:
            lock.acquire()
            server_dict[request.key] = request.value
            return numstore_pb2.SetNumResponse(total=sum(server_dict.values()))
        finally:
            lock.release()
            

    

    def Fact(self, request, context):
        # implementing locks to prevent other threads from accessing the dictionary while the current thread is working on this particular resource.

        hit = False
        value = None # to keep a track of wheter the value is in the server dictionary or not
        result = 0
        error = "Key Not Found"
        try:
            lock.acquire()
            if request.key in server_dict:
                value = server_dict[request.key]
                if value in factorial_cache_dict:
                    hit = True
                    result = factorial_cache_dict[value]
                    factorial_cache_dict.move_to_end(value, last=True)
                    error = ""

        finally:
            lock.release()

        # Factorial is being calculated outside the critical section where the lock is being held
        if hit == False and value != None:
            result = math.factorial(value)
            error = ""

        try:
            lock.acquire()
            # update the factorial cache dictionary with the new value
            factorial_cache_dict[value] = result
            if len(factorial_cache_dict) > 10:
                factorial_cache_dict.popitem(last = False) # remove the least recently used item from the ordered dictionary 

        finally:
            lock.release()

    

        return numstore_pb2.FactResponse(value=result, hit = hit, error=error)

        







def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    numstore_pb2_grpc.add_NumStoreServicer_to_server(
        RouteGuideServer(), server 
        )
    
    server.add_insecure_port('[::]:5440')
    server.start()
    print("Server started on port 5440")
    server.wait_for_termination()




if __name__ == '__main__':
    serve()
