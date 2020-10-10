# -*- coding:utf-8 -*-
"""
server
"""
import os
import socket
import select
import json
import struct
import asyncore
from cStringIO import StringIO

def ping(manager, params):
    manager.send_result(2001, params)

class ConnManager(object):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.RECV_BUFFER_SIZE = 4096
        self.register_handler_func()
        self.rbuf = StringIO()  # each connection has its own buffer

    def register_handler_func(self):
        self.handlers = {
            1001: ping,
        }

    def handle_close(self):
        print self.sock, self.addr, 'bye'
        self.sock.close()

    def handle_read(self):
        content = self.sock.recv(self.RECV_BUFFER_SIZE)
        if content:
            self.rbuf.write(content)
        else:
            self.handle_close()
            return -1
        self.handle_rpc()

    def handle_rpc(self):
        while True:  # 可能一次性收到了多个请求消息，所以需要循环处理
            self.rbuf.seek(0)
            length_prefix = self.rbuf.read(4)
            if len(length_prefix) < 4:  # 不足一个消息
                break
            length, = struct.unpack("I", length_prefix)
            body = self.rbuf.read(length)
            if len(body) < length:  # 不足一个消息
                break
            request = json.loads(body)
            cmd = request['cmd']
            params = request['params']
            print cmd, params
            handler = self.handlers[cmd]
            handler(self, params)  # 处理消息
            left = self.rbuf.getvalue()[length + 4:]  # 消息处理完了，缓冲区要截断
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2)  # 将游标挪到文件结尾，以便后续读到的内容直接追加. 2:end of file

    def send_result(self, cmd, result):
        response = {"cmd": cmd, "result": result}
        body = json.dumps(response)
        length_prefix = struct.pack("I", len(body))
        self.sock.send(length_prefix)  # 写入缓冲区
        self.sock.send(body) # 写入缓冲区

class BasicServer(object):
    def __init__(self, port=5000, manager=ConnManager):
        self.conn_dict = {}  # List to keep track of socket descriptors
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("127.0.0.1", port))
        self.server_socket.listen(10)
        self.prefork(5)
        self.conn_dict[self.server_socket] = 0
        self.manager_class = manager
        print "server started on port " + str(port) + ", ConnManager:" + self.manager_class.__name__

    def loop(self):
        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.conn_dict, [], [])
            for sock in read_sockets:
                # New connection
                if sock == self.server_socket:
                    new_sock, new_addr = self.server_socket.accept()
                    new_sock.setblocking(0)  # 开启非阻塞模式
                    manager = self.manager_class(new_sock, new_addr)
                    self.conn_dict[new_sock] = manager
                    print "Client (%s:%s) connected" % new_addr
                else:
                    ret = self.conn_dict[sock].handle_read()
                    if ret and ret == -1:
                        del self.conn_dict[sock]

    def prefork(self, n):
        for i in range(n):
            pid = os.fork()   # linux fork!
            if pid < 0:  # fork error
                return
            if pid > 0:  # parent process
                continue
            if pid == 0:
                print "new process"
                break  # child process

if __name__ == "__main__":
    server = BasicServer(5000, ConnManagerBusiness)
    server.loop()