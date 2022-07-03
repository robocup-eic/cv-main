import socket
from argparse import ArgumentParser
from custom_socket import CustomSocket


def main(args):
    c = CustomSocket(socket.gethostname(), args["port"])
    c.clientConnect()
    c.req(args["state"])

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--state", dest="state", default="default",
                        help="target state to be changed", metavar="STATE")
    parser.add_argument("-p", "--port", dest="port", default="15000",
                        help="server port", metavar="PORT", type=int, choices=range(0, 65536))
    args = vars(parser.parse_args())
    main(args)