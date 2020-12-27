from mitmproxy import http, ctx
from multiprocessing import Lock

class Filter:
    def __init__(self, filter_info):
        self.log_info=""
        self.mutex=Lock()
        self.filter_info=filter_info
        self.response_file=None
        self.switch_on = False
        self.log_file="mitm_log.txt"

    def log(self,info) -> None:
        self.log_info += f"{info}\n"
    
    def write_log(self, mode="w+") -> None:
        self.mutex.acquire()
        with open(self.log_file, mode) as f:
            f.write(self.log_info)
        self.mutex.release()

    def is_target_flow(self, flow: http.HTTPFlow) -> bool:
        # to judge whether the request is the target request
        return True

    def modify_response(self, flow: http.HTTPFlow) -> http.HTTPFlow:
        return flow
    
    def requests(self,flow: http.HTTPFlow) -> None:
        if self.is_target_flow(flow):
            self.log_info=""
            self.log(f"——METHOD——\n{flow.request.method}")
            self.log(f"——HOST——\n{flow.request.pretty_host}")
            self.log(f"——URL——\n{flow.request.pretty_url}")
            self.write_log()



if __name__ == "__main__":
    print("start the proxy")
