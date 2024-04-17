import socket
import sys
import subprocess

def get_ip():
    return subprocess.check_output('hostname -I', shell=True).decode('utf-8').split(' ')[0]

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((get_ip(), int(sys.argv[1])))
    s.listen(10)
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        if not data:
            break
        with open('./test_write.txt', 'w') as f:
            f.write(data.decode('utf-8'))
        output = subprocess.check_output(['hostname', '-I'])
        conn.sendall(output)
        conn.close()