#small feed notificator
#Released under the GNU GPL licence.
#Copyright Dario Calvijo (daedalus2027@gmail.com)
#!/usr/bin/env python
#-*- coding: latin-1 -*-

import gtk,Image,cStringIO
import urllib2,urllib
import re
import os,sys,getpass,tempfile
import feedparser
import pynotify
import time
from user import home
#--------------------------------------------------------------------------------------------------------
#clase principal
class FeedRSS():
	def __init__(self,bloglink):
		printdebug("cargando lista...")
		temp = self.getcachename()
		try:
			lista = cargar_archivo(temp)
		except:
			lista = ['']
		#try:
		try:
			self.rss = feedparser.parse(bloglink)
			parsed = True
		except:
			parsed = false
		if (parsed):
			blogtitle = self.gettitle()
			print blogtitle	
			icon = self.geticon()
			if not pynotify.init('pyrssnotify'):
				printdebug('pynotify was not initiated')
                        	sys.exit(1)	
			for element in self.rss.entries:
				#try:
				if(True):
					eID = self.getID(element)
					f = self.seekval(lista,eID)
					printdebug("[\nEntryID: " +  eID + " \nlink: "  +  element.link   +   " \nupdated: " +  element.updated +  " \npos: " + str(f) + " \nicon: " + icon + "]")
					if (element.link != '' and f == -1 and eID != ''):
						etitle = element.title
						link = self.compactlink(element.link)
						printdebug("Compactlink: " + link)
						msg = "<a href='" + link   + "'>" + etitle + "</a>"
						self.display(blogtitle,msg,icon)
						lista.append(eID)
						time.sleep(3.0)
				#except:
				else:
					printdebug("exception handled!")
			printdebug("salvando lista...")
			salvar_archivo(lista,temp)
			printdebug("ok")
			#except:
		else:
			printdebug("exception at feedparser handled!...maybe connectivity was lost...")

	def getID(self,element):
		try:
			Id = element.id
		except:
			Id = element.link
		return Id

	def getcachename(self):
		return home + "/.cache/pyrssnotify.list"
	
	def display(self,title,msg,icon):
		n = pynotify.Notification(title,msg)
		icondata = self.geticonpixbuf(icon)
		n.set_icon_from_pixbuf(icondata)
		n.set_timeout(10000)
		n.show
		if not n.show():
			printdebug("fail to show info!")
			sys.exit(1)
		
	def compactlink(self,link,nuevo = ''):
		data = urllib.urlencode([('url', link)])
		req = urllib2.Request('http://tinyurl.com/create.php')
		pagina = urllib2.urlopen(req, data)
		while True:
			data = pagina.read(1024)
			if not len(data):
				break	
			nuevo += data
		r = re.compile('<b>http://tinyurl.com/([a-zA-Z0-9]+)</b>',re.S)
                x = r.findall(nuevo)
		return "http://tinyurl.com/" + x[0]

        def gettitle(self):
		try:
			title = self.rss.feed.title
		except:
			title = rss 
		return title

	def geticonpixbuf(self,link):
		icondata = self.url2pixbuf(link)
		if (icondata == None):
			icondata = self.url2pixbuf('file:///usr/share/liferea/pixmaps/default.png')
		return icondata

	def geticon(self):
		try:	
			icon = self.rss.feed.icon
		except:
			try: 
				icon = self.rss.feed.image.href
			except:
				icon = "file:///usr/share/liferea/pixmaps/default.png" 
		return icon

	def seekval(self,lista,valor):
		try:
			f = lista.index(valor)
		except:
			f = -1
		return f

	def url2pixbuf(self,imgurl):
		try:
			img_feed = None
			img_feed = urllib.urlopen(imgurl).read()
			if img_feed:
				im = Image.open(cStringIO.StringIO(img_feed)).convert("RGB")
				imgdata = gtk.gdk.pixbuf_new_from_data(im.tostring(),gtk.gdk .COLORSPACE_RGB,False,8,im.size[0],im.size[1],3*im.size[0])
			else:
				imgdata = None
		except:
			printdebug("failed to load a image")	
			imgdata = None
		return imgdata


def printdebug(msg):
        pid = os.getpid()
	fullmsg = "PID: " + str(pid)  + ", "  + msg
	print fullmsg

#---------------------------------------------------------------------------------------------------------
#funcion para cargar un archivo de texto en una linea.		
def cargar_archivo(archivo): 
		f = open(archivo,"r")
		lineas = ['']
		while True:
      			linea = f.readline()
      			if not linea: break
      			lineas.append(linea.replace("\n",""))
		return lineas
#--------------------------------------------------------------------------------------------------------
#funcion para salvar una lista a un archivo					
def salvar_archivo(lineas,archivo):
		f = open(archivo,"w")
		for line in lineas:
			if (line != "" and line != "\n"): 
				f.writelines(line + "\n")
#---------------------------------------------------------------------------------------------------------
#main loop
blogs = cargar_archivo(home + "/blogs.list")
while True:	
	for blog in blogs:
		if (blog != ''):
			pid=os.fork()
			if pid:
				printdebug("Child Forked!")
				lm = FeedRSS(blog)
				sys.exit(0)
			else:
				printdebug("failed to fork a child")
	time.sleep(300.0)
