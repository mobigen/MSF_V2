# -*- coding: utf-8 -*-

from ClientHandler import ClientHandler
from MasterHandler import MasterHandler
from Server.AsyncServer import AsyncServer

def startC(port, conf) :
	return AsyncServer(port, ClientHandler, conf)

def startM(port, conf):
	return AsyncServer(port, MasterHandler, conf)
