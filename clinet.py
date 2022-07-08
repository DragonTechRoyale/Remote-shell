# Ed Lustig
import socket
import os
import tqdm



#IP = socket.gethostbyname(socket.gethostname())
__PORT = 5050
__COMMANDS = ["EXIT", "TAKE_SCREENSHOT", "DIR <folder name>", "DELETE <files name>", "EXECUTE <files name>", "COPY <directory to copy to> <file to copy>"]
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def main():
    IP = ""
    ip_valid = False
    while True:
        if ip_valid:
            break
        print("IP to connect to: (press enter for localhost)")
        input(IP)
        if IP == '':
            IP = 'localhost'
            ip_valid = True
        elif len(IP.split('.')) != 4:
            print("Invalid IP, try again")
        else:
            ip_valid = True
    # Init socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, __PORT))

    print("Available commands:")
    for command in __COMMANDS:
        print(command)
    print("Input commands:")  # Let the user know they can write commands
    cmd = ""  # command that'll be sent to the server
    data = ""  # data that'll be received from the server
    while True:
        cmd = input("~ ")  # input command from the user
        if cmd == "Q":  # adding an option to manually close the client
            exit(0)
        my_socket.send(len(cmd).to_bytes(4, byteorder="little"))  # send the command's length
        my_socket.send(cmd.encode())  # send the actual command
        dataLength = int.from_bytes(my_socket.recv(4), byteorder="little")  # get the length of the data from the server
        answer = my_socket.recv(dataLength).decode()  # get the actual data from the server
        if answer == "photo":
            # need to receive a picture here

            # receive file name
            dataLength = int.from_bytes(my_socket.recv(4), byteorder="little")
            answer = my_socket.recv(dataLength).decode()  # get the actual data from the server
            picture_name = answer
            print(f"receiving {picture_name}\n")

            # receive file size
            dataLength = int.from_bytes(my_socket.recv(4), byteorder="little")
            answer = my_socket.recv(dataLength).decode()  # get the actual data from the server
            picture_size = int(answer)

            size_counter = 0
            #progress = tqdm.tqdm(range(picture_size), f"Receiving {picture_name}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(picture_name, "wb") as f:
                while True:
                    bytes_read = my_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    if os.stat(picture_name).st_size >= picture_size:
                        break
                    size_counter += 4096
                    if size_counter >= picture_size:
                        break
                    f.write(bytes_read)
                    #progress.update(len(bytes_read))

            print(f"gotten picture {picture_name}")
        else:
            print(answer)
        if cmd == "EXIT":  # if the command is exit then close the client
            exit(0)

if __name__ == '__main__':
    main()
