from ctypes import *
import ctypes

#import calldll
import sys, getopt
import win32gui 
import win32api 
import win32con
import struct
import array,time

g_CopyFmt	= 'LLP'

logfile = open('d:\wa_client.log', 'w')

g_DEBUG_DICT =  {'CRITICAL':5,  "ERROR":4 , "WARNING":3 , "INFO":2, "DEBUG":1}
g_DEBUG_LEVEL = ''

class gsWindow: 
   def __init__(self, adtClassName, regKey ): 
      message_map = {
         win32con.WM_DESTROY: self.OnDestroy,     
         win32con.WM_COPYDATA: self.OnCopyData,
         }
      
      wc = win32gui.WNDCLASS() 
      wc.hIcon =  win32gui.LoadIcon(0, win32con.IDI_APPLICATION) 
      wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW) 
      wc.hbrBackground = win32con.COLOR_WINDOW 
      wc.lpszClassName = "Client_2" 
      wc.lpfnWndProc = message_map 
      self.hinst = wc.hInstance = win32api.GetModuleHandle(None) 

      self.cAtom = win32gui.RegisterClass(wc)      
        
      self.hwnd = win32gui.CreateWindowEx( 
         win32con.WS_EX_APPWINDOW, 
         self.cAtom, 
         "Client", 
         win32con.WS_OVERLAPPED | win32con.WS_SYSMENU, 
         win32con.CW_USEDEFAULT, 0, 
         win32con.CW_USEDEFAULT, 0, 
         0, 0, self.hinst, None) 

      print '    [INIT] client : hinst: ' , self.hinst, self.hwnd
      win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWDEFAULT) 
      win32gui.UpdateWindow(self.hwnd)

         
      #hWnd = win32gui.FindWindow("WinAdapter", None)
      hWnd = win32gui.FindWindow(adtClassName, None)
      ##################################################
      msg     =  "REG|^|%s|^|%s" % ( self.hwnd, regKey )
      ##################################################

      char_buffer          = array.array( "c", msg )

      int_data             = 1
      char_buffer_address  = char_buffer.buffer_info()[0] 
      char_buffer_size     = char_buffer.buffer_info()[1] 

      copy_struct        = struct.pack( g_CopyFmt, int_data, char_buffer_size, char_buffer_address )
      win32gui.SendMessage(hWnd, win32con.WM_COPYDATA, 0, copy_struct )
      
      print "    [SEND] client -> bus [%s]" % msg
      
   def OnCopyData(self, hwnd, msg, wparam, lparam):
      #print '======================================='
      #print 'client_2:copydata(%s, %s, %s, %s)' % (hwnd, msg, wparam, lparam)

      structure = ctypes.string_at( lparam, struct.calcsize(g_CopyFmt) )
      data = struct.unpack(g_CopyFmt, structure)
      
      int_data, str_len, str_adr = data
      my_string = ctypes.string_at( str_adr, str_len )

      noti_list = my_string.split('|^|')

      # 0: 'NTI', 1:handle, 2:key1, 3:key2, 4:message
      my_string   = noti_list[4]

      global    g_DEBUG_LEVEL
   
      if g_DEBUG_LEVEL == 'DEBUG' :      
         global logfile
         logfile.write( my_string )
         logfile.flush()

         print '    [RECV] client:recv len :',  str_len
         #print '    [RECV] client:recv :', my_string 
      


      #buf = win32gui.PyMakeBuffer(sizeof( lparam), lparam)
      ##buf = win32gui.PyMakeBuffer(struct.calcsize('PLP'), lparam)

      #print '======================================='
      """      
      #hdc=win32gui.GetDC(hwnd);
      #win32gui.DrawText(hdc, msg, 1, (15,20, 500,500), 1);
      #win32gui.ReleaseDC(hwnd, hdc);
      
      """
     
   def OnDestroy(self, hwnd, msg, wparam, lparam):     

      global logfile
      logfile.close()

      win32gui.DestroyWindow(self.hwnd) 
      try:    win32gui.UnregisterClass(self.cAtom, self.hinst) 
      except: pass 
      win32gui.PostQuitMessage(0)      


def main():

   try :
      optList, args = getopt.getopt(sys.argv[1:], 'p', ['level='] )
      print "OPT : ", optList, args  
      if len(args) < 2 : raise Exception
      opts = {}
      for optKey, optVal in optList : opts[optKey] = optVal
      
   except :
      print 'usage : %s [--level=] findClassName, key1 key2 ' % (sys.argv[0])
      print 'examp : %s --level=DEBUG WinAdapter key1 key2' % (sys.argv[0])
      print "        --level     : CRITICAL / ERROR / WARNING / INFO / DEBUG"

      time.sleep(10)
      sys.exit()

   print "OPT : ", opts

   global    g_DEBUG_LEVEL
   if opts.has_key( '--level' ): g_DEBUG_LEVEL = opts['--level'].strip()
   else : g_DEBUG_LEVEL = 'CRITICAL'

   adtClassName   = args[0]
   regKey         = args[1] + '|^|' + args[2] 
   
   w = gsWindow( adtClassName, regKey ) 
   win32gui.PumpMessages() 


main()


