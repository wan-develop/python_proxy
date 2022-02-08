import socket
import os
from threading import Thread
import parser_filter as parser
from sys import argv

from importlib import reload

## Currently works on Terraria Android Server. mitm server


class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.game = None # game client socket not known yet
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    # run in thread
    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                #print "[{}] <- {}".format(self.port, data[:100].encode('hex'))
                try:
                    reload(parser)                        
                    parser.parse(data, self.port, 'server')
                except Exception as e:
                    print(f'server[{self.port}]',e)
                # forward to client
                self.game.sendall(data)
                
                
             
                
    def send_data(self,data):
        #sends hex data to server.
        byte_data = bytes.fromhex(data)
        
        print(byte_data)
        self.game.send(byte_data)
        
        
        

class Game2Proxy(Thread):

    def __init__(self, host, port):
        super(Game2Proxy, self).__init__()
        self.server = None # real server socket not known yet
        #connection setup
        self.port = port
        self.host = host
        
        #connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        # waiting for a connection
        self.game, addr = sock.accept()

    def run(self):
        while True:
            data = self.game.recv(4096)
            if data:
                #print(f"[{self.port}] -> {data.decode(ENCRYPTION)}")
                try:
                    reload(parser)        
                    parser.parse(data, self.port, 'client')
                except Exception as e:
                    print('client[{self.port}]', e)
                # forward to server
                self.server.sendall(data)

class Proxy(Thread):

    def __init__(self, from_host, to_host, from_port, to_port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.from_port = from_port
        self.to_port = to_port
        
        self.g2p = None
        self.p2s = None
        
        

    def run(self):
        while True:
            print(f"[proxy from {self.from_port} to {self.to_port}] setting up...")
            self.g2p = Game2Proxy(self.from_host, self.from_port) # waiting for a client
            
            self.p2s = Proxy2Server(self.to_host, self.to_port)
            print("[proxy from {self.from_port} to {self.top_port}] connection established.")
            self.g2p.server = self.p2s.server
            self.p2s.game = self.g2p.game

            self.g2p.start()
            self.p2s.start()


PROXY_IP = argv[1]

PROXY_PORT = argv[2]

# argv 3 == "--target"

SERVER_IP = argv[4]

SERVER_PORT = argv[5]


proxy = Proxy(PROXY_IP,SERVER_IP, PROXY_PORT,SERVER_PORT)

proxy.run()

#game_servers = []

"""
for port in range(5900, 5901):
    _game_server = Proxy('0.0.0.0', ip, port)
    _game_server.start()
    game_servers.append(_game_server)
"""

#_game_server = Proxy('0.0.0.0', ip, 5901)
#_game_server.start()
#game_servers.append(_game_server)



while True:
    try:
        cmd = input('(proxy) > ')
        if cmd[:4] == 'stop':
            os._exit(0)
            
            
        if cmd[:4] == 'send':
            
            package = cmd.split(" ")[1]
            print(f"package {package} sended")
            
            proxy.p2s.send_data(package);
            
            
            
            
        '''
        if cmd[:4] == 'show':
            for game_server in game_servers:
        	    print(game_servers)
        '''
        
            
    except Exception as e:
        print(e)
        