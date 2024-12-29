#!/usr/bin/env python
# coding: utf-8

# IMPORTS

import time
import threading
from collections import deque


# GLOBAL VARIABLES
#t
# Rates
MAX_REQUESTS_PER_SECOND = 20
MAX_REQUESTS_PER_2MINUTE = 100

class RateLimiter_Method:
    """
        Second (Generic) Rate Limiter class for method rate limits
    """
    def __init__(self, limits):
        """
            Args:
                limits: A list of tuples, where each tuple contains (max_requests, period_in_seconds)
        """
        self.limits = limits
        self.lock = threading.Lock()
        self.request_times = {limit: deque() for limit in self.limits}

    def acquire(self):
        # Only one thread at a time
        with self.lock:
            while True:
                now = time.time()
                allowed = True

                # Go through every request and ensure rates are being followed
                for max_requests, time_window in self.limits:
                    q = self.request_times[(max_requests, time_window)]
                    # Remove timestamps older than the time window
                    while q and q[0] < now - time_window:
                        q.popleft()

                    if len(q) >= max_requests:
                        # Rate limit has been hit, will sleep for this one and then update all rates again / continue checking
                        allowed = False
                        wait_time = time_window - (now - q[0])
                        print(f"Rate limit reached for {max_requests}/{time_window}s. Sleeping for {wait_time:.2f} seconds.")
                        time.sleep(wait_time)
                        break

                if allowed:
                    # If here that means got through every limit check
                    for max_requests, time_window in self.limits:
                        # For every limit, add this timestamp
                        self.request_times[(max_requests, time_window)].append(now)
                    break
                    
# In[ ]:

# Custom RateLimiter class
class RateLimiter:
    def __init__(self, max_calls_1, period_1, max_calls_2, period_2):
        # Init for keeping tracking of calls per second (period_1) and 2min (period2)
        self.max_calls_1 = max_calls_1
        self.period_1 = period_1
        self.calls_1 = 0
        self.start_time_1 = time.time()

        self.max_calls_2 = max_calls_2
        self.period_2 = period_2
        self.calls_2 = 0
        self.start_time_2 = time.time()

        self.lock = threading.Lock() 

    def acquire(self):
        # Called everytime right before API is used to time it and ensure no requests more than x per sec and y per 2min
        # Only one thread at a time
        with self.lock:
            current_time = time.time()
    
            # Find time elapsed since first 
            elapsed_1 = current_time - self.start_time_1
            elapsed_2 = current_time - self.start_time_2
    
            # Reset calls and start time if period passed
            if elapsed_1 > self.period_1:
                self.calls_1 = 0
                self.start_time = current_time
    
            if elapsed_2 > self.period_2:
                self.calls_2 = 0
                self.start_time_2 = current_time
    
            # Proceed to sleep or not depending on if max calls per second exceeded
            if self.calls_1 < self.max_calls_1:
                self.calls_1 += 1
            else:
                time_to_wait = self.period_1 - elapsed_1
                if time_to_wait > 0:
                    print(f"Rate limit reached for {MAX_REQUESTS_PER_SECOND}/1s. Sleeping for {time_to_wait:.2f} seconds.")
                    time.sleep(time_to_wait)
                self.calls_1 = 1
                self.start_time_1 = time.time()
    
            # Proceed to sleep or not depending on if max calls per 2min exceeded
            if self.calls_2 < self.max_calls_2:
                self.calls_2 += 1
            else:
                time_to_wait = self.period_2 - elapsed_2
                if time_to_wait > 0:
                    print(f"Rate limit reached for {MAX_REQUESTS_PER_2MINUTE}/2m. Sleeping for {time_to_wait:.2f} seconds.")
                    time.sleep(time_to_wait)
                self.calls_2 = 1
                self.start_time_2 = time.time()


