import sys, socket, threading, argparse,subprocess
from dataclasses import dataclass


# global variables
@dataclass
class Settings: 
    listen: bool = False
    command: bool = False
    upload: bool = False
    execute: str = ""
    target: str = ""
    upload_destination: str = ""
    port: int = 0

def process_options():
    parser = argparse.ArgumentParser(description="Swiss Knife Tool")
    parser.add_argument('-t', '--target', default='')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('-l', '--listen', action='store_true')
    parser.add_argument('-e', '--execute', default='')
    parser.add_argument('-c', '--command', action='store_true', default=False)
    parser.add_argument('-u', '--upload', default='')
    args = parser.parse_args()

    Settings.listen = args.listen
    Settings.command = args.command
    Settings.upload = args.upload or False
    Settings.execute = args.execute
    Settings.target = args.target
    Settings.upload_destination = args.upload
    Settings.port = args.port

def client_sender(buffer):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        client.connect((Settings.target,Settings.port))
#
        if len(buffer):
            client.send(bytes(buffer,'utf8'))

        while True:
            recv_len = 1
            response = ''

            while recv_len:
                data = client.recv(4096)
                
                recv_len = len(data)
                response += str(data)

                if recv_len < 4096:
                    break
            
            print(response, end=" ")
            buffer = input("")
            buffer += "\n"


            client.send(bytes(buffer,'utf8'))

    except Exception as ex:
        print("[*] Exception! Exiting")

        client.close()
        raise ex
        

def server_loop():

    if not len(Settings.target):
        target  = '0.0.0.0'

    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    server.bind((Settings.target,Settings.port))
    
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print("[*] Accepted connection from: %s:%d" % (addr[0],addr[1]))

        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()


def run_command(command):
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr = subprocess.STDOUT, shell=True)
    except:
        output = 'Failed to execute command.\r\n'

    return output

def client_handler(client_socket):

    if len(Settings.upload_destination):
        file_buffer = ''

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer+=data

        try:
            file_description = open(upload_destination,'wb')
            file_description.write(file_buffer)
            file_description.close()

            client_socket.send("Successfully saved file to%s\r\n" % upload_destination)

        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)


    if len(Settings.execute):

        output = run_command(Settings.execute)

        client_socket.send(output)


    if Settings.command:
        while True:

            client_socket.send(bytes('<SwissKnife: #> ', 'utf8'))


            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(1024), 'utf8')


            response = run_command(cmd_buffer)


            client_socket.send(response)
        



def main():

    process_options()
    print(Settings.target)
    
    if not Settings.listen and len(Settings.target) and Settings.port > 0:
        buffer = sys.stdin.read()
        print(buffer)
        client_sender(buffer)

    elif Settings.listen:
        server_loop()
        



if __name__ == "__main__":
    main()
