#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = -1   # return -1 if code was not assigned through method
        d = data.split(' ', 2)
        c = None
        if len(d) > 1:
            c = d[1]
        if c is None:
            return code
        if c.isdigit():
            code = int(c)
        return code

    def get_headers(self, data):
        d = data.split('\r\n\r\n')[0]
        return d


    def get_body(self, data):
        d = data.split('\r\n\r\n')
        if len(d) > 1:
            return d[1]
        else:
            return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        code = 500

        p = urllib.parse.urlparse(url)
        port = p.port
        hostname = p.hostname
        path = p.path
        ip = socket.gethostbyname(hostname)

        if path == '':
            path = '/'
        if port is None:
            port = 80

        self.connect(ip, port)

        get_string = "GET " + path + " HTTP/1.1\r\n"
        get_string += "Host: " + str(hostname) + "\r\n"
        get_string += "Connection: close\r\n"
        get_string += "\r\n"
        self.sendall(get_string)
        data = self.recvall(self.socket)
        body = self.get_body(data)
        new_code = self.get_code(data)
        if new_code != -1:
            code = new_code


        self.socket.close()
        http_response = HTTPResponse(code, body)
        print('Response Code ' + str(http_response.code))
        print(str(http_response.body))
        return http_response

    def POST(self, url, args=None):
        code = 500

        p = urllib.parse.urlparse(url)
        port = p.port
        hostname = p.hostname
        path = p.path
        ip = socket.gethostbyname(hostname)
        if path == '':
            path = '/'
        if port is None:
            port = 80
        self.connect(ip, port)

        args_string = ''

        if args is not None:
            index = 0
            num_args = len(args)
            for a in args:
                index += 1
                args_string += str(a) + "=" + str(args[a])
                if index != num_args: # do not add & after last arg
                    args_string += "&"

        post_string = "POST " + path + " HTTP/1.1\r\n"
        post_string += "Host: " + str(hostname) + "\r\n"
        post_string += "Content-Type: application/x-www-form-urlencoded\r\n"
        post_string += "Content-Length: " + str(len(args_string)) + "\r\n"
        post_string += "Connection: close\r\n"
        post_string += "\r\n"
        post_string += args_string

        self.sendall(post_string)
        data = self.recvall(self.socket)
        self.close()

        body = self.get_body(data)
        new_code = self.get_code(data)
        if new_code != -1:
            code = new_code

        http_response = HTTPResponse(code, body)
        print('Response Code ' + str(http_response.code))
        print(str(http_response.body))

        return http_response

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
