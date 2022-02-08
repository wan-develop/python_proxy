import os

def parse(data, port, origin):
    if origin == 'server': #or origin == 'client':
        return
        pass
    
        
    hex_data = data.hex()
    
    print(f"[{origin} {port}] => {hex_data}")
    
    
