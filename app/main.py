import os
import socket
import sys
import threading

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

class Http_Response:

    def __init__(self, version:str="1.1", status:str="200", message:str="OK", headers:dict=dict(), body:str=""):
        status_line = f'HTTP/{version} {status} {message}\r\n'
        headersList = []
        for k, v in headers.items():
            headersList.append(f"{k}: {v}")
        self.response_string = status_line + ("\r\n".join(headersList) + "\r\n\r\n" if headersList else "\r\n") + (body + "\r\n" if body else "")

# class RouteHandler:
#     def __init__(self):
#         self.route_lookup = dict()

#     def router(self, path:str, method:str, req, client_socket):
#         try:
#             self.route_lookup[path][method](req, client_socket)
#         except:
#             print(f"Exception while handling {method} on {path}!")
#             response = Http_Response(status="404", message="Not Found")
#             client_socket.sendmsg([(response.response_string).encode()])

#     def addRoute(self, path:str, handler:function, method:str="GET"):
#         path_methods = self.route_lookup[path]
#         if not path_methods:
#             self.route_lookup[path] = dict
#             path_methods = self.route_lookup[path]
#         path_methods[method] = handler

def slash_handler(req, client_socket):
    response = Http_Response()
    client_socket.sendmsg([response.response_string.encode()])

def echo_handler(req, client_socket):
    request_path = req.header["path"]
    echo_string = path_parts(request_path)
    response_headers = dict()
    response_headers["Content-Type"] = "text/plain"
    response_headers["Content-Length"] = len(echo_string)
    response =  Http_Response(headers=response_headers, body=echo_string)
    print(response.response_string)
    client_socket.sendmsg([(response.response_string).encode()])
    # client_socket.sendmsg(
    #     [(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}").encode()])

def user_agent_handler(req, client_socket):
    user_agent = req.header["User-Agent"]
    response_headers = dict()
    response_headers["Content-Type"] = "text/plain"
    response_headers["Content-Length"] = len(user_agent)
    response = Http_Response(headers=response_headers, body=user_agent)
    client_socket.sendmsg([(response.response_string).encode()])
    # client_socket.sendmsg(
    #     [(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}").encode()])

def file_read_handler(req, client_socket):
    request_path = req.header["path"]
    file_name = path_parts(request_path)
    directory = sys.argv[2]
    file_path = os.path.join(directory, file_name)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            contents = file.read()
        responseHeaders = dict()
        responseHeaders["Content-Type"]="application/octet-stream"
        responseHeaders["Content-Length"]=len(contents)
        response = Http_Response(headers=responseHeaders, body=contents)
    else:
        response=Http_Response(status="404", message="Not Found")
    client_socket.sendmsg([(response.response_string).encode()])

def file_write_handler(req, client_socket):
    request_path = req.header["path"]
    file_name = path_parts(request_path)
    directory = sys.argv[2]
    file_path = os.path.join(directory, file_name)
    contents = req.body[0]
    print("Contents: ", contents)
    with open(file_path, 'w') as file:
        file.write(contents)
    response = Http_Response(status="201", message="Created")
    client_socket.sendmsg([(response.response_string).encode()])

def main():
    print("Server started!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept() # wait for client
        print(client_socket, client_address)
        thread = threading.Thread(target=handleConnection, args=(client_socket, ))
        thread.start()
        # handleConnection(client_socket)

    # route_handler = RouteHandler()
    # route_handler.addRoute("/", slash_handler)
    # route_handler.addRoute("/echo", echo_handler)
    # route_handler.addRoute("/user-agent", user_agent_handler)
    # router = route_handler.router
    
    
def path_parts(path:str) -> str:
    parts = path.split("/", 2)
    return parts[2]

def handleConnection(client_socket):
    with client_socket:
        data, _ , _ , _  = client_socket.recvmsg(1024)
        if data:
            data = data.decode()
            request_obj = Http_Request(data)
            print("Request Headers: ", request_obj.header)
            print("Request Body: ", request_obj.body)
            request_path = request_obj.header["path"]
            print("Request path: ", request_path)
            if request_path=="/": 
                slash_handler(req=request_obj, client_socket=client_socket)
            elif request_obj.header['method']=="GET" and request_path.startswith("/echo"):
                echo_handler(req=request_obj, client_socket=client_socket)
            elif request_obj.header['method']=="GET" and request_path=="/user-agent":
                user_agent_handler(req=request_obj, client_socket=client_socket)
            elif request_obj.header['method']=="GET" and request_path.startswith("/file"):
                file_read_handler(req=request_obj, client_socket=client_socket)
            elif request_obj.header['method']=="POST" and request_path.startswith("/file"):
                file_write_handler(req=request_obj, client_socket=client_socket)
            else:
                response = Http_Response(status="404", message="Not Found")
                client_socket.sendmsg([(response.response_string).encode()])
                # client_socket.sendmsg([("HTTP/1.1 404 Not Found\r\n\r\n").encode()])


if __name__ == "__main__":
    main()
