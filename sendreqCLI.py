from socket import *
serverName = 'localhost'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = input('Input requests:\n')
clientSocket.send(sentence)
clientSocket.close()