import argparse, sys, socket
import multiprocessing
import traceback
import json

class Client:
    def __init__(self):
        self.messages = []
        
        self.parser()
        self.start()

    def parser(self):
        parser = argparse.ArgumentParser(
        prog="anonchat-cli",
        description = "Connect to the anonchat V2",
        epilog="---- Oh, hello there!")
 
        parser.add_argument("ip", help = "IP of anonchat-server", type=str)
        parser.add_argument("-n", "--nick", help = "Your nick", type=str, dest = "nick", default="Anon")
        
        args = parser.parse_args()

        self.nick = args.nick

        ip = args.ip.split(":")
        ip.append(6968)

        self.ip = ip[0]
        try:
            self.port = int(ip[1])
        except:
            print(f"Cannot parse port {ip[1]} as number. Aborting.")
            sys.exit()

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

        self.request = multiprocessing.Process(target=self.mp_request, args=())
        self.request.start()
        try:
            while True:
                message = input("")
                if message.strip():
                    message = {"user": self.nick, "msg": message}                    
                    self.socket.send(json.dumps(message, ensure_ascii=False).encode())
        except:
            traceback.print_exc()
            self.request.terminate()
            self.socket.close()
            sys.exit()

    def mp_request(self):
        while True:
            if self.socket.fileno() != -1:
                try:
                    message = self.socket.recv(1024)
                except:
                    break

            if not message:
                break
            
            try:
                message = message.decode()
                try:
                    message = json.loads(message.strip())
                except:
                    message = {"user": "V1-Message", "msg": message}
                    
            except:
                self.messages.append({"user": "[CLIENT]", "msg": "Message was recieved, but the contents cannot be decoded :("})
            else:
                self.messages.append(message)
            print(f'<{self.messages[-1]["user"]}> ' + self.messages[-1]["msg"], end="\n", flush=True)

if __name__ == "__main__":
    cli = Client()
        
        
