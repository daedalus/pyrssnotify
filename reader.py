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
#main class
class FeedRSS():
	def __init__(self,bloglink):
		printdebug("blog list loading...")
		temp = self.getcachename()
		try:
			lista = list_load(temp)
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
			printdebug("blog list saving...")
			list_save(lista,temp)
			printdebug("ok")
			#except:
		else:
			printdebug("exception at feedparser handled!...maybe connectivity was lost...")
		time.sleep(300.0)

	def getID(self,element):
		try:
			Id = element.id
		except:
			Id = element.link
		return Id

	def getcachename(self):
		return f"{home}/.cache/pyrssnotify.list"
	
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
		return f"http://tinyurl.com/{x[0]}"

        def gettitle(self):
		try:
			title = self.rss.feed.title
		except:
			title = rss 
		return title

	def geticonpixbuf(self,link):
		icondata = self.url2pixbuf(link)
		if icondata is None:
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
			if img_feed := urllib.urlopen(imgurl).read():
				im = Image.open(cStringIO.StringIO(img_feed)).convert("RGB")
				imgdata = gtk.gdk.pixbuf_new_from_data(im.tostring(),gtk.gdk .COLORSPACE_RGB,False,8,im.size[0],im.size[1],3*im.size[0])
			else:
				imgdata = None
		except:
			printdebug("failed to load a image")	
			imgdata = None
		return imgdata


#--------------------------------------------------------------------------------------------------------
# it prints out debugging text

def printdebug(msg):
        pid = os.getpid()
	fullmsg = "PID: " + str(pid)  + ", "  + msg
	print fullmsg

#---------------------------------------------------------------------------------------------------------
# it loads a text file into a variable

def list_load(archivo): 
	f = open(archivo,"r")
	lineas = ['']
	while True:
		if linea := f.readline():
			lineas.append(linea.replace("\n",""))
		else:
			break
	return lineas
#--------------------------------------------------------------------------------------------------------
# it saves the content of a variable into a text file					

def list_save(lineas,archivo):
	f = open(archivo,"w")
	for line in lineas:
		if line not in ["", "\n"]: 
			f.writelines(line + "\n")

#--------------------------------------------------------------------------------------------------------
# it tryes to fork from main process to create a child

def try_fork(blog):
	global childs
	global maxchilds
	if (childs <= maxchilds):
		if pid := os.fork():
			childs+=1
			printdebug(f"Child: {childs} forked: {str(pid)}")
			lm = FeedRSS(blog)
			sys.exit(0)
			childs-=1
		else:
			printdebug(f"Child: {str(childs)} failed to fork")
	else:
		lm = FeedRSS(blog)


#---------------------------------------------------------------------------------------------------------
#main loop
def main_loop():
	blogs = list_load(f"{home}/blogs.list")
	while True:	
		for blog in blogs:
			if (blog != ''):
				try_fork(blog)
		# do not ever think to remove this line 
		# it can and will hang up your computer
		time.sleep(300.0)

#---------------------------------------------------------------------------------------------------------
childs=1
maxchilds=10
main_loop()
