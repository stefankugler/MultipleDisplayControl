"""
Python implementation of Samsung Multiple Display Control Protocol
http://www.samsung.com/us/pdf/RS232_MX_CX_PDPseries.pdf
"ExLink over IP"

usage:
  # get status control
  python mdc.py 0x00

  # get power status
  python mdc.py 0x11

  # power on/off
  python mdc.py 0x11 0x1
  python mdc.py 0x11 0x0

"""

import sys
import socket

IP      = '192.168.1.112'
PORT    = 1515
BUFFER  = 1024
ID      = 0xFF   #ID 0 should he 0xFF

def sendCmd(commands):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print 'Socket error!'

    s.connect((IP, PORT))

    # default command: status control (0x00)
    if (len(commands)) == 0:
        commands = [0x00]

    # parse all parameters as bytes
    commands = [int(c,16) for c in commands]
    # data length (see mdc protocol)
    datalength = len(commands) - 1
    # create communication string
    msg = [0xAA, commands[0], ID, datalength] + commands[1:]
    # calculate checksum and append to communication string
    # checksum = sum of all bytes except header (0xAA) mod 256
    checksum = sum(msg[1:]) % 256
    msg.append(checksum)

    # create byte string
    msgs = ''.join(format(m, '02x') for m in msg).decode('hex')

    try:
        s.send(msgs)
    except socket.error:
        sys.exit()

    data = s.recv(BUFFER)
    s.close()

    # convert received bytes
    rec = data.encode('hex')
    # split list into chunks of two
    list = [int(rec[i:i+2],16) for i in range(0,len(rec), 2)]
    # calculate checksum
    rchecksum = sum(list[1:-1]) % 256

    # compare calculated checksum with received data (last byte)
    if rchecksum != list[-1]:
        print "checksum error"

    # check Ack/Nack
    if chr(list[4]) != 'A':
        #print list[6]
        return -1

    else:
        # return map(hex,list[6:-1])
        return list[6:-1]

print sendCmd(sys.argv[1:])
