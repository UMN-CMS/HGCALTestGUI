import getpass
import sshtunnel
import sys
from sshtunnel import SSHTunnelForwarder

# creates an SSH tunnel to the server machine
class Tunnel:

    def __init__(self):

        username = input("Username for CMSLAB3: ")
        passwd = getpass.getpass()

        ssh_host = "cmslab3.spa.umn.edu"
        ssh_username = username
        ssh_password = passwd

        localhost = "127.0.0.1"

        self.tunnel = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username = ssh_username,
            ssh_password = ssh_password,
            remote_bind_address = ('127.0.0.1', 80),
            local_bind_address = ('127.0.0.1', 8080)
        )

        self.tunnel.start()

        print("Tunnel created successfully!")

    def close(self):

        print("Closing SSH tunnel")

        self.tunnel.close

