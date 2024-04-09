# Uncomment this to pass the first stage
import socket

class Http_Request:

    @staticmethod
    def parse_request(header_string:str) -> tuple[list[str], list[str]]:
        lines = header_string.split("\r\n")
        header_idx=-1
        try:
            header_idx = lines.index("")
        except:
            pass
        header_lines = lines[:header_idx] if header_idx!=-1 else lines
        body_lines = lines[header_idx+1:] if header_idx!=-1 else []
        return header_lines, body_lines
    
    @staticmethod
    def parse_headers(header_lines) -> dict:
        request_header = dict()
        start_line = header_lines[0].split(" ")
        request_header["method"], request_header["path"], request_header["version"] = start_line
        for i in range(1, len(header_lines)):
            key, value = header_lines[i].split(":", 1)
            request_header[key] = value.strip()
        return request_header

    def __init__(self, request_string):
        self.header_lines, self.body_lines = Http_Request.parse_request(request_string)
        self.header = Http_Request.parse_headers(self.header_lines)
        self.body = self.body_lines



def main():
    print("Server started!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept() # wait for client

    print(client_socket, client_address)
    with client_socket:
        data, _ , _ , _  = client_socket.recvmsg(1024)
        if data:
            data = data.decode()
            request_obj = Http_Request(data)
            print("Headers: ", request_obj.header)
            print("Body: ", request_obj.body)
            request_path = request_obj.header["path"]
            print("Request path: ", request_path)
            if request_path=="/":
                client_socket.sendmsg([("HTTP/1.1 200 OK\r\n\r\n").encode()])
            elif request_obj.header['method']=="GET" and request_path.startswith("/echo"):
                echo_string = handle_echo(request_path)
                client_socket.sendmsg(
                    [(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}").encode()])
            elif request_obj.header['method']=="GET" and request_path=="/user-agent":
                user_agent = request_obj.header["User-Agent"]
                client_socket.sendmsg(
                    [(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}").encode()])
            else:
                client_socket.sendmsg([("HTTP/1.1 404 Not Found\r\n\r\n").encode()])

def handle_echo(path:str) -> str:
    parts = path.split("/", 2)
    print("Parts: ", parts)
    return parts[2]



if __name__ == "__main__":
    main()
