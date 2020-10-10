# -*- coding:utf-8 -*-

# 业务开发的时候只需要继承一下ConnManager然后register一下cmd和方法的对应

from basicserver import ConnManager
from basicserver import BasicServer

# cmd = 1002
def introduce(manager, name):
	manager.send_result(2002, "My name is {}!".format(name))

class ConnManagerBusiness(ConnManager):
    def __init__(self, sock, addr):
        super(ConnManagerBusiness, self).__init__(sock, addr)
        self.register_new_handler_func()

    def register_new_handler_func(self):
    	D = {
            1002: introduce,
        }
        self.handlers.update(D)

if __name__ == '__main__':
	server = BasicServer(port=5000, manager=ConnManagerBusiness)
	server.loop()
