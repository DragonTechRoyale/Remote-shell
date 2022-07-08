import socket
import os
import glob
import shutil
import subprocess
import platform
from pathlib import Path
import datetime
import pyscreenshot
import datetime
import random
from pathlib import Path
import ntpath
import tqdm


__LITTLE = "little"
__IP = socket.gethostbyname(socket.gethostname())
__IP = "localhost"
__PORT = 5050
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096


def command(cmd):
    # gets a string of the command and runs the correct function
    if cmd == "EXIT":
        return "exit connection"
    elif cmd == "TAKE_SCREENSHOT":
        return take_screenshot()
    elif len(cmd.split()) == 2:
        if cmd.split(' ')[0] == "DIR":
            return str(dir(cmd.split(' ')[1]))
        elif cmd.split(' ')[0] == "DELETE":
            return str(delete(cmd.split(' ')[1]))
        elif cmd.split(' ')[0] == "EXECUTE":
            return str(execute(cmd.split(' ')[1]))
        else:
            return "try again"
    elif len(cmd.split()) == 3:
        if cmd.split(' ')[0] == "COPY":
            return str(copy(cmd.split(' ')))
        else:
            return "try again"
    else:
        return "try again"



def dir(path):
    # gets a path to a folder and returns a list of the files in the folder
    files = []
    if path[len(path) - 1] == '/':
        files = glob.glob(f"{path}*")
    else:
        files = glob.glob(f"{path}/*")
    return files


def delete(path):
    if os.path.exists(path):
        os.remove(path)
        return f"deleted {path} successfully"
    else:
        return "The file does not exist"


def copy(cmd):
    source = r'{}'.format(cmd[1])
    target = r'{}'.format(cmd[2])
    try:
        shutil.copy(source, target)
        return f"copied {source} to {target} successfully"
    except IOError as e:
        return "Unable to copy file. %s" % e
    except:
        return "Unexpected error"


def execute(path):
    path = Path(path)
    if path.is_file() or os.path.exists(path):  # needed to add "or os.path.exists(path)" because apps are packages
        temp = "open " + str(path)
        os.system(temp)
        return f"executed {path} successfully"
    else:
        return "file not exist"


def take_screenshot():
    os.system("mkdir screenshots")
    now = datetime.datetime.now()
    file_name = now.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
    full_file_name = "./screenshots/" + file_name
    image = pyscreenshot.grab()
    rgb_im = image.convert('RGB')
    rgb_im.save(full_file_name)
    print("file name: ", end="")
    print(file_name)
    print("file size: ", end="")
    print(os.stat(full_file_name).st_size, "bytes")
    return f"taken screenshot {file_name} successfully"


def send_screenshot(client_socket):
    if len(os.listdir('./screenshots/*')) == 0:
        take_screenshot()
    list_of_files = glob.glob('./screenshots/*')
    file_name = max(list_of_files, key=os.path.getctime)
    print(f"send {file_name}")
    full_file_name = file_name
    file_size = os.stat(full_file_name).st_size

    # send server "photo" indecating youre sending a photo
    answer = "photo"
    answer = answer.encode()
    client_socket.send(len(answer).to_bytes(4, byteorder=__LITTLE))
    client_socket.send(answer)

    # send the file name
    answer = str(path_leaf(file_name))
    answer = answer.encode()
    client_socket.send(len(answer).to_bytes(4, byteorder=__LITTLE))
    client_socket.send(answer)

    # send the file size
    answer = str(file_size)
    answer = answer.encode()
    client_socket.send(len(answer).to_bytes(4, byteorder=__LITTLE))
    client_socket.send(answer)

    # send the actual file
    #progress = tqdm.tqdm(range(file_size), f"Sending {full_file_name}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(full_file_name, 'rb') as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            client_socket.sendall(bytes_read)
            #progress.update(len(bytes_read))

    #client_socket.send(image)
    #image.close()


def latest_screenshot():
    # uses a list of the files in the current dir and returns the name of the newest screenshot
    list_of_files = glob.glob(f'./screenshots/*')

    if len(list_of_files) == 0:
        take_screenshot()
        list_of_files = glob.glob(f'./screenshots/*')

    # remove "./" from file names
    for i in range(len(list_of_files)):
        list_of_files[i] = path_leaf(list_of_files[i])

    # remove ".jpg"
    for i in range(len(list_of_files)):
        list_of_files[i] = list_of_files[i].split('.')[0]

    print(list_of_files)
    # remove all that arent from the latest year
    latest_year = int(list_of_files[0].split('-')[2])
    for file in list_of_files:
        if int(file.split('-')[2]) > latest_year:
            latest_year = int(file.split('-')[2])
    for file in list_of_files:
        if int(file.split('-')[2]) < latest_year:
            list_of_files.remove(file)

    # remove all that arent from the latest month
    latest_month = int(list_of_files[0].split('-')[1])
    for file in list_of_files:
        if int(file.split('-')[1]) > latest_month:
            latest_month = int(file.split('-')[1])
    for file in list_of_files:
        if int(file.split('-')[1]) < latest_month:
            list_of_files.remove(file)

    # remove all that arent from the latest day
    latest_day = int(list_of_files[0].split('-')[0])
    for file in list_of_files:
        if int(file.split('-')[0]) > latest_day:
            latest_day = int(file.split('-')[0])
    for file in list_of_files:
        if int(file.split('-')[0]) < latest_day:
            list_of_files.remove(file)

    # remove all that arent from the latest hour
    latest_hour = int(list_of_files[0].split('-')[3])
    for file in list_of_files:
        if int(file.split('-')[3]) > latest_hour:
            latest_hour = int(file.split('-')[3])
    for file in list_of_files:
        if int(file.split('-')[3]) < latest_hour:
            list_of_files.remove(file)

    # remove all that arent from the latest minute
    latest_minute = int(list_of_files[0].split('-')[4])
    for file in list_of_files:
        if int(file.split('-')[4]) > latest_minute:
            latest_minute = int(file.split('-')[4])
    for file in list_of_files:
        if int(file.split('-')[4]) < latest_minute:
            list_of_files.remove(file)

    # remove all that arent from the latest second
    latest_second = int(list_of_files[0].split('-')[5])
    for file in list_of_files:
        if int(file.split('-')[5]) > latest_second:
            latest_second = int(file.split('-')[5])
    for file in list_of_files:
        if int(file.split('-')[5]) < latest_second:
            list_of_files.remove(file)

    file_name = random.choice(list_of_files)
    return f"{file_name}.jpg"


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def main():
    # init client connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((__IP, __PORT))
    server_socket.listen()
    while True:
        client_socket, address = server_socket.accept()

        cmd = ""  # variable for the command received from the client
        answer = ""  # variable for the answer the sever sends
        while True:
            length = int.from_bytes(client_socket.recv(4), __LITTLE)  # get the cmd's length from the client
            try:
                # try to get the actual cmd from the client
                cmd = client_socket.recv(length).decode()
            except:
                # replace with an empty string if it fails
                cmd == ""
            print(cmd)
            # send the answer to the server
            if cmd == "SEND_PHOTO":
                send_screenshot(client_socket)
            else:
                answer = command(cmd).encode()
                client_socket.send(len(answer).to_bytes(4, byteorder=__LITTLE))
                client_socket.send(answer)
            if cmd == "EXIT":
                print("Client exited")
                break

        client_socket.close()


if __name__ == '__main__':
    main()
