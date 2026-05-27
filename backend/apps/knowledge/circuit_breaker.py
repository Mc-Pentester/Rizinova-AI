import time

class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=120):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout

        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def allow_request(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
