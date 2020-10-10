# coding: utf-8
# client.py

import json
import time
import struct
import socket


def rpc(sock, cmd, params):
    request = json.dumps({"cmd": cmd, "params": params})  # 请求消息体
    length_prefix = struct.pack("I", len(request)) # 请求长度前缀
    sock.sendall(length_prefix)
    sock.sendall(request)
    length_prefix = sock.recv(4)  # 响应长度前缀
    length, = struct.unpack("I", length_prefix)
    body = sock.recv(length) # 响应消息体
    response = json.loads(body)
    return response["cmd"], response["result"]  # 返回响应类型和结果

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 5000))
    for i in range(10): # 连续发送 10 个 rpc 请求
        cmd, result = rpc(s, 1002, "test %d" % i)
        print 'response:', cmd, result
        time.sleep(1)  # 休眠 1s，便于观察
    s.close() # 关闭连接