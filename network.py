import ssl
import socket


def get_connection(config):
    hostname = config['watcher']['hostname']
    if not hostname:
        hostname = ''
    port = config['watcher']['port']
    print(hostname + ":" + port)
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslcontext.options |= ssl.OP_NO_SSLv2
    sslcontext.options |= ssl.OP_NO_SSLv3
    newsock = socket.create_connection((hostname, port))
    connection = sslcontext.wrap_socket(newsock)
    return connection

