# -*- coding: utf-8 -*- 

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pymysql
import requests
from lxml import etree
from openpyxl import Workbook
from bs4 import BeautifulSoup
import random        


class AddNameDialog(QDialog):

	def __init__(self, parent=None):
		super(AddNameDialog, self).__init__(parent) 		
		self.setWindowTitle("CNKI")
		self.resize(350,300)

		AddName_label1=QLabel(self.tr("Input your account Info："))
		AddName_label2=QLabel(self.tr("Host Name："))
		AddName_label3=QLabel(self.tr("User Name："))
		AddName_label4=QLabel(self.tr("Password："))

		self.AddName_hostname=QLineEdit("localhost")
		self.AddName_uesrname=QLineEdit("root")
		self.AddName_password=QLineEdit()
		self.AddName_password.setEchoMode(QLineEdit.Password)

		AddName_ok_button=QPushButton(self.tr("Ok"))

		layout=QGridLayout()
		layout.addWidget(AddName_label1,0,0,1,2)
		layout.addWidget(AddName_label2,1,0)
		layout.addWidget(self.AddName_hostname,1,1)
		layout.addWidget(AddName_label3,2,0)
		layout.addWidget(self.AddName_uesrname,2,1)
		layout.addWidget(AddName_label4,3,0)
		layout.addWidget(self.AddName_password,3,1)
		layout.addWidget(AddName_ok_button,4,0,1,2,Qt.AlignHCenter)

		self.setLayout(layout)
		#Set the signal slot function corresponding to the OK button
		AddName_ok_button.clicked.connect(self.showdialog)
		#AddName_ok_button.clicked.connect(self.hide)

	def showdialog(self):
		#Get the information of the input edit box
		AddName_get_hostname=str(self.AddName_hostname.text())
		AddName_get_uesrname=str(self.AddName_uesrname.text())
		AddName_get_password=str(self.AddName_password.text())
		#Try to connect to the database
		try:
			global conn
			conn = pymysql.connect(host='127.0.0.1', port=3306, user='%s'%(AddName_get_uesrname), passwd='%s'%(AddName_get_password),charset='utf8')

			QMessageBox.information(self,"OK",self.tr("Login successful"))
			self.form1=AddDatabaseDialog()#Open the Add Database dialog box
			self.form1.show()
		except:
			#Failed to enter information, error message box pops up
			QMessageBox.critical(self,"error",self.tr("Entry information failed, please re-enter"))



class AddDatabaseDialog(QDialog):
	def __init__(self,parent=None):
		super(AddDatabaseDialog,self).__init__(parent)#Init AddDatabaseDialog class
		global conn
		global cur

		self.setWindowTitle(self.tr("Please choose the database"))
		#Set the left control
		label_left=QLabel(self.tr("Select or Create a database"))
		#label_left.setFont(QFont("SimSun",12,QFont.Bold))
		
		self.input_database=QLineEdit()##Initially display this database
		adddatabase_ok_button=QPushButton(self.tr("Ok"))

		#Set the left layout of the window
		layout_left=QVBoxLayout()
		#layout_left.setMargin(10) #Set the border margin of the left layout
		layout_left.addWidget(label_left)
		layout_left.addStretch()#Enlarge the space between the label and the button
		layout_left.addWidget(self.input_database)
		layout_left.addWidget(adddatabase_ok_button)
		#Set the controls on the right side of the window
		label_right=QLabel(self.tr("Show existing databases"))
		label_right.setFont(QFont("SimSun",12,QFont.Bold))
		label_right.setAlignment(Qt.AlignCenter)#Centering the label
		self.show_database_text=QTextEdit()
		self.show_database_text.setFontPointSize(15)
		self.show_database_text.setTextColor(Qt.darkCyan)
		self.show_database_text.setFontFamily("Arial")
		#QTextEdit
		self.show_database_text.setReadOnly(True)#Set the text content as read-only and unchangeable

		#Set the layout of the right side of the window
		layout_right=QVBoxLayout()
		#layout_right.setMargin(8) 
		layout_right.addWidget(label_right)
		layout_right.addWidget(self.show_database_text)
		#Set general layout
		layout_combin=QHBoxLayout()
		layout_combin.addLayout(layout_left)
		layout_combin.addLayout(layout_right)

		self.setLayout(layout_combin)

		#Get a pointer to a con object
		cur=conn.cursor()
		#Run the command to display the database name
		cur.execute("SHOW databases")
		
		#Display the database name in the text box
		a=[]
		for i in cur.fetchall():#Iterate through each database name in the result
			c=str(i)[2:][0:-3]#Strip out the colons and brackets from the database name, leaving the database name alone
			a.append(c)#Add to an empty list

		self.show_database_text.setText(self.tr(str(a).replace("'","").strip("[").strip("]")))
		#Display the list in a text box, remove the "'[]" character from the string, and get the data name and comma

		#Signal slot function for connecting ok button
		#self.connect(adddatabase_ok_button,SIGNAL("clicked()"),self.adddatabase_ok)
		adddatabase_ok_button.clicked.connect(self.adddatabase_ok)


	def adddatabase_ok(self):
		#Get the text in the edit box
		get_input_database=str(self.input_database.text())
		#Execute the display data frame operation
		cur.execute("SHOW databases")
		find_=False #Set the match success variable
		for i in cur.fetchall():
			c=str(i)[2:][0:-3]
			if get_input_database==str(c):#Determine if the data in the data box is equal to the corrected database name
				conn.select_db("%s"%get_input_database)#Perform a select database operation
				find_=True#Change Match Success Variables
				break
		if find_:#
			#QMessageBox.information(self,"Information", self.tr("Connect Successfully"))
			self.form2=MainWorkWindows()
			self.form2.show()#self life cycle is not released when the function is called
		else :
			button=QMessageBox.question(self,"Question",self.tr("This database was not found, is a new database named %s created?"%get_input_database),QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Ok)
			if button==QMessageBox.Ok:
				cur.execute("create Database %s"%get_input_database)
				#Update the text box to show the newly added database
				cur.execute("SHOW databases")
				a=[]
				for i in cur.fetchall():#Iterate through each database name in the result
					c=str(i)[2:][0:-3]#Strip out the colons and brackets from the database name, leaving the database name alone
					a.append(c)#Add to an empty list
				self.show_database_text.setText(self.tr(str(a).replace("'","").strip("[").strip("]")))#Display the list in a text box


class MainWorkWindows(QMainWindow):
	global cur,conn

	def __init__(self):
		QMainWindow.__init__(self)#Initialize the main interface

		self.setWindowTitle(self.tr("Web Crawler"))
		self.resize(300,300)#Set the title and size of the main interface
		self.ii=0
		self.pagestart=0


		#Setup Menu
		bar=self.menuBar()
		file1=bar.addMenu('File')
		file1.addAction("New")
		file2=bar.addMenu('Tool')
		search_action=QAction("Search",self)
		file2.addAction(search_action)
		file2.triggered[QAction].connect(self.processtrigger)
		
		#label
				
		Label1=QLabel(self.tr("Input Key Words："))
		Label2=QLabel(self.tr("Condition sorting："))
		Label3=QLabel(self.tr("Save table name："))
		Label4=QLabel(self.tr("Search Location："))
		Label5=QLabel(self.tr("Number of crawled pages："))

		#Edit Line
		self.search_key_word=QLineEdit()
		self.set_tab_name=QLineEdit('please input in English')

		#Set English or numeric validator
		reg = QRegExp("[a-zA-Z0-9]+$")
		pValidator = QRegExpValidator(self)
		pValidator.setRegExp(reg)	
		self.set_tab_name.setValidator(pValidator)

		#Search Button
		self.search_button=QPushButton(self.tr("Search"))
		self.search_button.clicked.connect(self.click_search)

		#Counter
		self.pageend=5
		self.sp=QSpinBox()
		self.sp.setMinimum(1)
		self.sp.setMaximum(15)
		self.sp.setValue(5)
		self.sp.valueChanged.connect(self.valuechange)


		#dropdown box
		self.cb=QComboBox()
		self.cb_text="qw:"
		self.cb.addItem(self.tr("Literature"))
		self.cb.addItem(self.tr("Topic"))
		self.cb.addItem(self.tr("Title"))
		self.cb.addItem(self.tr("Author"))
		self.cb.addItem(self.tr("Abstract"))
		self.cb.currentIndexChanged.connect(self.selectionchange)


		#check box
		self.a_radio="relevant"
		layout_radio1 = QVBoxLayout()
		self.btn1 = QRadioButton(self.tr("Relevancy"))
		self.btn1.setChecked(True)
		self.btn1.toggled.connect(lambda:self.btnstate1(self.btn1))
		layout_radio1.addWidget(self.btn1)
		self.btn2 = QRadioButton(self.tr("Citation frequency"))
		self.btn2.toggled.connect(lambda:self.btnstate1(self.btn2))
		layout_radio1.addWidget(self.btn2)
		self.btn3 = QRadioButton(self.tr("Download count"))
		self.btn3.toggled.connect(lambda:self.btnstate1(self.btn3))
		layout_radio1.addWidget(self.btn3)
		self.btn4 = QRadioButton(self.tr("Publish time"))
		self.btn4.toggled.connect(lambda:self.btnstate1(self.btn4))
		layout_radio1.addWidget(self.btn4)

		#Layout
		layout1h=QHBoxLayout()
		layout1h.addWidget(Label1)
		layout1h.addWidget(self.search_key_word)

		layout2h=QHBoxLayout()
		layout2h.addWidget(Label2)
		layout2h.addLayout(layout_radio1)

		layout4h=QHBoxLayout()
		layout4h.addWidget(Label3)		
		layout4h.addWidget(self.set_tab_name)

		layout3h=QHBoxLayout()
		layout3h.addWidget(Label4)
		layout3h.addWidget(self.cb)

		layout5h=QHBoxLayout()
		layout5h.addWidget(Label5)
		layout5h.addWidget(self.sp)


		layoutv=QVBoxLayout()
		layoutv.addLayout(layout1h)
		layoutv.addLayout(layout2h)
		layoutv.addLayout(layout3h)
		layoutv.addLayout(layout5h)
		layoutv.addLayout(layout4h)
		layoutv.addWidget(self.search_button)

		widget=QWidget()
		widget.setLayout(layoutv)
		self.setCentralWidget(widget)

	def processtrigger(self,q):
		if q.text()=='Search':
			self.form_search=SearTabDialog()
			self.form_search.show()


	def valuechange(self):
		print (type(self.sp.value()))
		print (type(self.pageend))
		self.pageend=self.sp.value()
		#print (self.pageend+'77777777777')

	def selectionchange(self,i):
		print (self.cb.currentText())
		if self.cb.currentText()=="Literature":
			self.cb_text="qw:"
		if self.cb.currentText()=="Topic":
			self.cb_text="theme:"		
		if self.cb.currentText()=="Title":
			self.cb_text="title:"
		if self.cb.currentText()=="Author":
			self.cb_text="author:"
		if self.cb.currentText()=="Abstract":
			self.cb_text="abstract:"

	def btnstate1(self,btn):
		
		if btn.text()=="Relevancy":
			if btn.isChecked() == True:
				self.a_radio="relevant"
				print( btn.text() + "relevant is selected" )
			else:
				pass		
		if btn.text()=="Citation frequency":
			if btn.isChecked()== True :
				self.a_radio="citeNumber"
				print( btn.text() + "citeNumber is selected" )
			else:
				pass
		if btn.text()=="Download count":
			if btn.isChecked()== True :
				self.a_radio="download"
				print( btn.text() + "download is selected" )
			else:
				pass
		if btn.text()=="Publish time":
			if btn.isChecked()== True :
				self.a_radio="data"
				print( btn.text() + "date is selected" )
			else:
				pass

	#--Get proxy IP list
	def get_ip_list(self,urlip,headers2):
		web_data = requests.get(urlip,headers=headers2)
		soup = BeautifulSoup(web_data.text, 'lxml')
		ips = soup.find_all('tr')
		ip_list = []
		for k in range(1, len(ips)):
			ip_info = ips[k]
			tds = ip_info.find_all('td')
			ip_list.append(tds[1].text + ':' + tds[2].text)
		return ip_list

	#-Select one randomly from the proxy IP list
	def get_random_ip(self,ip_list):
		proxy_list= []
		for ip in ip_list:
			proxy_list.append('http://' + ip)
		proxy_ip = random.choice(proxy_list)
		proxies = {'http': proxy_ip}
		return proxies

	#Click the search button to start building the database
	def click_search(self):

		#conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='bdcghs',charset='utf8')
		#cursor = conn.cursor()
		#cur.execute("use test")
		cur.execute("create table %s (title varchar(100),author varchar(100),jounral varchar(100),keyword varchar(100),abstract varchar(2000) )"%(self.set_tab_name.text()))


		print(self.a_radio)
		self.pagestart=1

		keywords=self.search_key_word.text()
		if keywords == '':
			keywords='gravity'
		keywords=self.cb_text+keywords#Add text to enter search location


		url='http://search.cnki.net/search.aspx?q='+str(keywords)+'&rank='+str(self.a_radio)+'&cluster=all&val=&p='
		urlip = 'http://www.xicidaili.com/nt/'
		headers={
				'Referer':'http://search.cnki.net/search.aspx?q=qw:%e7%b2%be%e5%87%86%e6%89%b6%e8%b4%ab&cluster=all&val=&p=0',
				'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
				'Cookie':'cnkiUserKey=158f5312-0f9a-cc6a-80c1-30bc5346c174; Ecp_ClientId=4171108204203358441; UM_distinctid=15fa39ba58f5d2-0bbc0ba0169156-31637c01-13c680-15fa39ba5905f1; SID_search=201087; ASP.NET_SessionId=glrrdk550e5gw0fsyobrsr45; CNZZDATA2643871=cnzz_eid%3D610954823-1510276064-null%26ntime%3D1510290496; CNZZDATA3636877=cnzz_eid%3D353975078-1510275934-null%26ntime%3D1510290549; SID_sug=111055; LID=WEEvREcwSlJHSldRa1FhcTdWZDhML1NwVjBUZzZHeXREdU5mcG40MVM4WT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!',
				}
		headers2={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
		for i in range(self.pagestart,self.pageend+1):
			self.ii=i
			try:
				ip_list = self.get_ip_list(urlip,headers2)
				proxies = self.get_random_ip(ip_list)
				url_all=url+str(15*(self.ii-1))
				response=requests.get(url_all,headers=headers)
				file=response.text.encode(response.encoding).decode('utf-8')
				r=etree.HTML(file)
				urllist=r.xpath("//div[@class='wz_content']/h3/a[1]/@href")
				self.get_data(urllist,headers,proxies)
			except:
				print('On No.'+str(self.ii)+' page an error occurred')

		conn.commit()
		cur.close()
		conn.close()

	def get_data(self,urllist,headers,proxies):
		print (urllist)
		j=0
		for urli in urllist:
			try:
				j=j+1
				num=15*(self.ii-self.pagestart)+j
				test=str(urli)
				f=requests.get(test,headers=headers)
				ftext=f.text.encode(f.encoding).decode('utf-8')
				ftext_r=etree.HTML(ftext)
				pachong_title=str(ftext_r.xpath('//title/text()')[0]).replace(' - 中国学术期刊网络出版总库','').replace(' - 中国博士学位论文全文数据库','').replace(' - 中国优秀硕士学位论文全文数据库','')
				print(pachong_title)
				pachong_author=str(ftext_r.xpath("//div[@class='author summaryRight']/p[1]/a/text()"))
				pachong_author=pachong_author.replace('[','').replace(']','').replace("'",'')
				print(pachong_author)
				pachong_journal_time=str(ftext_r.xpath("//div[@id='weibo']/input/@value")[0])
				print(pachong_journal_time)
				pachong_keyword=str(ftext_r.xpath("//span[@id='ChDivKeyWord']/a/text()"))
				pachong_keyword=pachong_keyword.replace('[','').replace(']','').replace("'",'')
				print(pachong_keyword)
				pachong_abstract=str(ftext_r.xpath("//span[@id='ChDivSummary']/text()")[0])
				print (type(pachong_title),type(pachong_author),type(pachong_journal_time),type(pachong_keyword),type(pachong_abstract))
				#print(pachong_abstract)
				aaa="insert into kkk7 values('%s','%s','%s','%s','%s')"%(pachong_title,pachong_author,pachong_journal_time,pachong_keyword,pachong_abstract)
				print(aaa)
				cur.execute("insert into %s values('%s','%s','%s','%s','%s')"%(self.set_tab_name.text(),pachong_title,pachong_author,pachong_journal_time,pachong_keyword,pachong_abstract))
				conn.commit()
				#cursor.execute("insert into kkk values(pachong_title,pachong_author,pachong_journal_time,pachong_keyword,pachong_abstract)")
				print('Crwal'+str(num)+' of '+str(15*(self.pageend-self.pagestart+1))+' is successful！！')
			except:
				print('Crwal '+str(j)+'on page'+str(self.ii)+'is failed~')



#Search Existence Table Dialog
class SearTabDialog(QDialog):

	def __init__(self, parent=None):
		super(SearTabDialog, self).__init__(parent) 		
		self.setWindowTitle("search table")
		self.resize(350,300)

		search_tab_label1=QLabel(self.tr("Search Table Name："))

		self.search_tablename=QLineEdit("")


		search_ok_button=QPushButton(self.tr("OK"))
		search_show_button=QPushButton(self.tr("Existing Table Name"))

		layout=QGridLayout()
		layout.addWidget(search_tab_label1,1,0)
		layout.addWidget(self.search_tablename,1,1)
		layout.addWidget(search_ok_button,2,0)
		layout.addWidget(search_show_button,2,1)


		self.setLayout(layout)

		#Set the signal slot function corresponding to the OK button
		search_ok_button.clicked.connect(self.search_ok)
		search_show_button.clicked.connect(self.search_show)

		#AddName_ok_button.clicked.connect(self.hide)
	
	def search_show(self):
		print('ok')
		self.search_show_open=ShowExistTabDialog()
		self.search_show_open.show()

	def search_ok(self):
		print('on')
		global get_cur_table
		get_cur_table=str(self.search_tablename.text())
		self.search_ok_open=ShowChooseDialog()
		self.search_ok_open.show()
		'''
		AddName_get_hostname=str(self.AddName_hostname.text())
		AddName_get_uesrname=str(self.AddName_uesrname.text())
		AddName_get_password=str(self.AddName_password.text())
		try:
			global conn
			conn = pymysql.connect(host='127.0.0.1', port=3306, user='%s'%(AddName_get_uesrname), passwd='%s'%(AddName_get_password),charset='utf8')
			QMessageBox.information(self,"OK",self.tr("Login Successfully"))
			self.form1=AddDatabaseDialog()
			self.form1.show()
		except:
			QMessageBox.critical(self,"error",self.tr("Failed, re-try"))
		'''

#Show Existence Table Dialog
class ShowExistTabDialog(QDialog):

	def __init__(self, parent=None):
		super(ShowExistTabDialog, self).__init__(parent) 
		global conn,cur		
		self.setWindowTitle("Show exist table")
		self.resize(350,300)

		show_tab_label1=QLabel(self.tr("Existing Table："))

		self.show_exist_tab=QTextEdit()

		layout=QVBoxLayout()
		layout.addWidget(show_tab_label1)
		layout.addWidget(self.show_exist_tab)
		self.setLayout(layout)

		conn.commit()

		cur.execute("SHOW tables")

		a=[]
		for i in cur.fetchall():
			c=str(i)[2:][0:-3]
			a.append(c)
		self.show_exist_tab.setText(self.tr(str(a).replace("'","").strip("[").strip("]")))#Display the list in a text box


class ShowChooseDialog(QTableWidget):
	#A class that displays a table, this class summarizes all the information into a single table
	def __init__(self,parent=None):
		super(ShowChooseDialog,self).__init__(parent)

		self.resize(600,400)
		self.setWindowTitle(self.tr("Show form information"))
		
		global get_cur_table,cur#Define global variables and read previous data

		#Set the number of columns and read the number of items in the table
		row_num=0
		cur.execute('select * from %s'%get_cur_table)
		for i in cur.fetchall():
			row_num=row_num+1
		self.setRowCount(row_num)
		self.setColumnCount(5)

		self.setHorizontalHeaderLabels(['Topic','Author','Journal','Key Words','Abstract'])
		cur.execute('select * from %s'%get_cur_table)
		j=0
		for i in cur.fetchall():
			self.setItem(j,0,QTableWidgetItem(self.tr(i[0])))
			self.setItem(j,1,QTableWidgetItem(self.tr(i[1])))
			self.setItem(j,2,QTableWidgetItem(self.tr(i[2])))
			self.setItem(j,3,QTableWidgetItem(self.tr(i[3])))
			self.setItem(j,4,QTableWidgetItem(self.tr(i[4])))
			j=j+1


if __name__ == '__main__':
	app = QApplication(sys.argv)
	demo = AddNameDialog()
	demo.show()
	#conn.close()
	sys.exit(app.exec_())

