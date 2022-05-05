from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QInputDialog, qApp, QMessageBox,QTableWidgetItem
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from pandas import read_sql
from psycopg2 import connect
from hashlib import sha256
from random import choice
from time import sleep
import sys

conn    = connect(host="localhost", user="postgres", password="123456", database="shop_data" )
cur     = conn.cursor()

class WelcomeScreen(QDialog):

    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)
 
    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex()+1)

class LoginScreen(QDialog):

    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("loginscreen.ui",self)
        self.passwordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        
    def loginfunction(self):
        #main menude username yazdirmak icin global yazdik
        global user,level
        user = self.usernameLine.text()
        password    = self.passwordLine.text()
        hassPass    = sha256(password.encode('utf-8')).hexdigest()
        cur.execute(""" SELECT username FROM login_info 
                        WHERE username LIKE %s """,(user,))
        result_username=cur.fetchone()

        if len(user)==0 or len(password)==0:
            self.errorLabel.setText("Please input all fields.")

        elif result_username==None:
            self.errorLabel.setText("Username not found.")
         
        else:            
            cur.execute(""" SELECT password FROM login_info 
                            WHERE username = %s """,(user,))                            
            passCheck = cur.fetchone()[0]
            cur.execute(""" SELECT level FROM login_info 
                            WHERE username =%s """,(user,))
            level=cur.fetchone()[0]
         
            if passCheck == hassPass:
                print("Successfully logged in.")
                self.errorLabel.setText("Successfully logged in.")
                #sifre ve kullanici adi dogru ise Main menu ekranina gecis
                ddd = MainMenu()
                widget.addWidget(ddd)
                #widget.setFixedHeight(600)
                #widget.setFixedWidth(450)
                widget.setCurrentIndex(widget.currentIndex()+1)

            else:
                self.errorLabel.setText("Invalid Password")
            
class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createaccountscreen.ui",self)
        self.passwordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)

    def signupfunction(self):
        user = self.usernameLine.text()
        password = self.passwordLine.text() 
        confirmpassword = self.confirmpasswordLine.text()
        cur.execute(""" SELECT username FROM login_info 
                        WHERE username LIKE %s """ , (user,))        
        check_username=cur.fetchone()

        if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
            self.errorLabel.setText("Please fill in all inputs.")

        elif password!=confirmpassword:
            self.errorLabel.setText("Passwords do not match.")
        
        else: 
            if  check_username!=None:
                self.errorLabel.setText("username is already defined")

            else:
                #password hassleme
                hassPass= sha256(password.encode('utf-8')).hexdigest()
                cur.execute(""" INSERT INTO login_info (username, password, level) 
                                VALUES (%s,%s,%s)""", (user, hassPass,1))
                conn.commit()
                #login ekranina gecis
                ddd = LoginScreen()
                widget.addWidget(ddd)
                widget.setCurrentIndex(widget.currentIndex()+1)  
                   
class MainMenu(QMainWindow,LoginScreen):
    def __init__(self):
        super(MainMenu,self).__init__()
        loadUi("mainmenuscreen.ui",self)
        #login classindan username ve level bilgisini cagirdik
        self.usernameLabel.setText(user)        
        self.levelLabel.setText(str(level))
        #play butonuna tiklaninca game ekranina gitmek icin
        self.playButton.clicked.connect(self.goplayButton)
        self.statisticsButton.clicked.connect(self.gostatisticsButton)
        #setting menu bar kismindaki exitin calismasi icin 
        self.exitAction.triggered.connect(qApp.quit)
        self.timerAction.triggered.connect(self.get_seconds)
        self.levelAction.triggered.connect(self.get_level)
        self.actionCustom_Level.triggered.connect(self.gocustomlevel)
        self.exitButton.clicked.connect(qApp.quit)
        self.progressBar.setMaximum(25)
        n=int(level)
        self.progressBar.setValue(n)
        self.timerLabel.setAlignment(QtCore.Qt.AlignCenter)      
            
    def goplayButton(self):
        play = GameScreen()
        widget.addWidget(play)
        widget.setFixedHeight(420)
        widget.setFixedWidth(500)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gostatisticsButton(self):
        statistics = StatisticsScreen()        
        widget.addWidget(statistics)       
        widget.setFixedHeight(800)
        widget.setFixedWidth(775)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gocustomlevel(self):
        customlevel = CustomLevelScreen()
        widget.addWidget(customlevel)
        widget.setCurrentIndex(widget.currentIndex()+1)

    #timer ayarlamasi
    def get_seconds(self):
        global second             
        second, ok = QInputDialog.getInt(self, 'Seconds', 'Enter seconds between 3-20 :',3, 3, 20, 1)
        
        if  ok :               
            self.timerLabel.setText(str(second))

    #oynadigi levelleri tekrar oynamk isterse
    def get_level(self):
        global neulevel
        neulevel, ok = QInputDialog.getInt(self, 'Level', "Enter level between 1" + "-"+ f"{level}" ,1 , 1, level, 1)
        
        if  ok :
            self.levelLabel.setText(str(neulevel))
     
class StatisticsScreen(QMainWindow):
    def __init__(self):
        super(StatisticsScreen,self).__init__()
        loadUi("statisticscreen.ui",self) 
        self.backmainmenuButton.clicked.connect(self.backMainMenu)
        self.showStatics()

    def showStatics(self):
        #toplam kullanici sayisini göstermek icin
        cur.execute("SELECT count(username) FROM login_info;")
        totalUsername=cur.fetchone()[0]
        self.totaluserLabel.setText(str(totalUsername))

        #level siralamasi icin ve levelde ilk 5 de degil ise sirasini yazdirmak icin
        self.label_5.setText("LEVEL"+f" {level} "+ "SUCCESS TABLE")
        cur.execute("""
                    SELECT row_number () OVER (ORDER BY level DESC), username, level 
                    FROM login_info ;
                    """)
        levelLabel=cur.fetchall()        
        for i in range(len(levelLabel)):
            users_row   =levelLabel[i][0]#siralama
            users_name  =levelLabel[i][1]#userame

            if i<=4:
                self.tableWidget.setItem(i,0,QTableWidgetItem(f"{users_name}"))
                self.tableWidget.setItem(i,1,QTableWidgetItem(f"{levelLabel[i][2]}"))
            #levelde ilk 5 de degil ise sirasini yazdirmak icin
            elif users_name == user and users_row>5 :
                self.userRowLabel.setText("you are in the" +f" {users_row}" +"th position")
            else:
                pass
      
        #en kötü oynama yüzdesi olan 3 level
        cur.execute(""" SELECT level, percentage  FROM success_percentage  
                        WHERE  username=%s 
                        ORDER BY percentage  
                        limit 3""" , (user,))
        zzz=cur.fetchall()
        for i in range(len(zzz)):
            self.tableWidget3.setItem(i,0,QTableWidgetItem(f"{zzz[i][0]}"))
            self.tableWidget3.setItem(i,1,QTableWidgetItem(f"{zzz[i][1]}"))
    
        #en iyi oynama yüzdesi olan 3 level
        cur.execute(""" SELECT level, percentage  FROM success_percentage  
                        WHERE  username=%s 
                        ORDER BY percentage DESC  
                        limit 3""" , (user,))
        yyy=cur.fetchall()
        for i in range(len(yyy)):
            self.tableWidget4.setItem(i,0,QTableWidgetItem(f"{yyy[i][0]}"))
            self.tableWidget4.setItem(i,1,QTableWidgetItem(f"{yyy[i][1]}"))

        #hangi levelde ise o leveldeki en iyi dereceler levelde ilk 5 de degil ise kacinci sirada oldugunu yazdirmak icin
        cur.execute(""" SELECT row_number () OVER (ORDER BY percentage DESC), username, percentage 
                        FROM success_percentage 
                        WHERE level=%s            
                        """, (level,))
        uuu=cur.fetchall()

        for i in range(len(uuu)):
            level_row   =uuu[i][0]
            level_user  =uuu[i][1]
            
            if i<=4:
                self.tableWidget2.setItem(i,0,QTableWidgetItem(f"{level_user}"))
                self.tableWidget2.setItem(i,1,QTableWidgetItem(f"{uuu[i][2]}"))

            elif level_row>5 and level_user==user:
                self.userRowLabel2.setText("you are in the" +f" {level_row}" +"th position")
            else:
                pass            
         
    def backMainMenu(self):
        ddd = MainMenu()
        widget.addWidget(ddd)
        widget.setFixedHeight(571)
        widget.setFixedWidth(380)
        widget.setCurrentIndex(widget.currentIndex()+1)
         
class GameScreen(QDialog):
    current_word    = {}
    def __init__(self):
        super(GameScreen,self).__init__()
        loadUi("gamescreen.ui",self)
        try     :self.count_value   = second
        except  :self.count_value   = 3
        self.start_flag             = True
        self.click                  = 0
      
        try     :
            #self.level = int(custlevel)
            self.level = int(neulevel) 
        except  :
            try     :
                #self.level = int(neulevel) 
                self.level = int(custlevel)

            except  :
                self.level = int(level) 
                   
        self.score_value            = int(level-1)*20
        self.levellineLabel.setText(str(self.level))
        self.timer = QTimer()  
        self.timer.timeout.connect(self.show_time)  
        self.timer.start(1000) 

        if self.level>0:            
            self.data            = read_sql('SELECT * FROM nl_words', con=conn)
            self.df              = self.data.loc[self.data['level_id'] == self.level]            

        else:
            self.data            = read_sql("SELECT * FROM custom_level", con=conn)
            self.df              = self.data.loc[self.data['username'] == user]  
              
        self.language_data   = self.df.to_dict(orient="records")
        self.restWords       = len(self.language_data) 
        self.restLabel.setText(str(self.restWords))
        #print(self.restWords)  
        self.mainmenuButton.clicked.connect(self.mainMenuButton)    
        self.applyButton.clicked.connect(self.known_words)
        self.cancelButton.clicked.connect(self.countClick)            
        self.nextCard() 

    def countClick(self):
        self.click+=1
        #print(self.click)
        self.nextCard() 
        #return self.click            

    def show_time(self):  
        if self.start_flag: 
            self.timerLabel.setText(str(self.count_value))
            if self.count_value == 0:
                self.start_flag  = False
                self.flipCard()              
        self.count_value -= 1                   
   
    def nextCard(self):
        self.start_flag = True        
        try     :self.count_value    = second
        except  :self.count_value    = 3
        self.pushButton.setStyleSheet(u"background-color: rgb(154, 229, 157);\n"
                                        "border-radius:20px;\n"
                                        "font: 33pt \"Bauhaus 93\";\n"
                                        "color: rgb(170, 57, 57);")
        self.langLabel.setText("Dutch")
        self.current_word   = choice(self.language_data)
        #print(self.current_word)
        word_nl             = self.current_word["dutch"]
        self.pushButton.setText(word_nl)       

    def known_words(self):
        self.score_value+=1
        self.restWords-=1   
        self.language_data.remove(self.current_word)
        self.restLabel.setText(str(self.restWords))
        #print(self.restWords)
        self.levellineLabel.setText(str(self.level))
        if self.level>0 and self.restWords == 0:
                percetage=(20/(self.click+20))*100
                #print(percetage)            
                cur.execute(""" INSERT INTO success_percentage (username,level,percentage)  
                                VALUES (%s,%s,%s)""", (user, self.level, percetage))
                conn.commit()            
                self.level  += 1            
                self.levelInfo(self.level)
                self.click=0
                self.levellineLabel.setText(str(self.level))
                #print(self.level)
                self.initUI()  

        elif self.level==0 and self.restWords == 0:
            
            self.mainMenuButton()
           
        else:
            self.nextCard()

    def initUI(self):
        self.setGeometry(0, 0, 500, 420)
        buttonReply = QMessageBox.question(self, 'Next Level', "Do you want to go to the next level?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.nexLevel()
            
        else:            
            self.mainMenuButton()

    def nexLevel(self):

        if self.level<=25:
            self.df              = self.data.loc[self.data['level_id'] == self.level]
            self.language_data   = self.df.to_dict(orient="records")
            self.restWords       = len(self.language_data)
            self.restLabel.setText(str(self.restWords))             
            self.nextCard()

        else:
            sleep(1)
            ddd = EndOfGame()
            widget.addWidget(ddd)
            widget.setFixedHeight(491)
            widget.setFixedWidth(471)
            widget.setCurrentIndex(widget.currentIndex()+1)             

    #kelime anlamini gormek icin asgidaki fonksinyonu tanimladik        
    def flipCard(self):        
        word_eng=self.current_word["english"]
        #print(word_eng)
        self.pushButton.setText(word_eng)                    
        self.langLabel.setText("English")       
        self.pushButton.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
                                        "border-radius:20px;\n"
                                        "font: 33pt \"Bauhaus 93\";\n"
                                        "color: rgb(170, 57, 57);")
        self.pushButton.clicked.connect(self.clickme)

    def clickme(self):
        word_wieder=self.current_word["dutch"]
        self.pushButton.setText(word_wieder)
        self.langLabel.setText("Dutch")
        self.pushButton.setStyleSheet(u"background-color: rgb(154, 229, 157);\n"
                                        "border-radius:20px;\n"
                                        "font: 33pt \"Bauhaus 93\";\n"
                                        "color: rgb(170, 57, 57);")
      
    def levelInfo(self,myLevel):

        if 25>= myLevel>level:
            #if myLevel<=25: 
                #sql de level kismi editlenecek
                cur.execute(""" UPDATE login_info 
                                SET level = %s 
                                WHERE username = %s""", (myLevel, user))
                conn.commit()
            
        else:
            pass

    def mainMenuButton(self):
        
        aaa = MainMenu()
        widget.addWidget(aaa)
        widget.setFixedHeight(571)
        widget.setFixedWidth(380)
        widget.setCurrentIndex(widget.currentIndex()+1)

class CustomLevelScreen(QDialog):
    def __init__(self):
        super(CustomLevelScreen,self).__init__()
        loadUi("custlomlevelscreen.ui",self)
        self.backmainmenuButton.clicked.connect(self.backMainMenu)
        self.playButton.clicked.connect(self.goplayButton)
        # self.dutchmeaningLine.setEchoMode(QtWidgets.QLineEdit.Password)
        # self.englishmeaningLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.wordsaveButton.clicked.connect(self.saveword)

    def saveword(self):
        dutchmeaning = self.dutchmeaningLine.text()
        englishmeaning = self.englishmeaningLine.text()
        cur.execute(""" SELECT dutch FROM custom_level 
                        WHERE dutch LIKE (%s)""" , (dutchmeaning,))
        check_word = cur.fetchone()
        #print(check_word)

        if check_word != None:
            self.errorLabel.setText("this word is already saved")

        else:
            word_set = [user,0, dutchmeaning, englishmeaning]
            cur.execute('INSERT INTO custom_level VALUES (%s,%s,%s,%s)', word_set)
            conn.commit()
            self.errorLabel.setText("word saved successfully")
            #self.duthcmeaningLine.setText("")
            #self.englishmeaningLine.setText("")

    def backMainMenu(self):
        ddd = MainMenu()
        widget.addWidget(ddd)
        widget.setFixedHeight(571)
        widget.setFixedWidth(380)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def goplayButton(self):
        global custlevel
        custlevel = 0
        cur.execute(""" SELECT username FROM custom_level 
                        WHERE username LIKE %s """,(user,))
        customLevelUser=cur.fetchone()

        if customLevelUser==None:
            self.errorLabel2.setText("There is not any saved words for you")

        else:
            #self.level=0
            #GameScreen.__init__(self.level) 
            play = GameScreen()
            widget.addWidget(play)
            widget.setFixedHeight(420)
            widget.setFixedWidth(500)
            widget.setCurrentIndex(widget.currentIndex()+1)

class EndOfGame(QDialog):
    def __init__(self):
        super(EndOfGame,self).__init__()
        loadUi("congscreen.ui",self)

# main
if __name__ == "__main__":
    app     = QApplication(sys.argv)
    welcome = WelcomeScreen()
    widget  = QtWidgets.QStackedWidget()
    widget.addWidget(welcome)
    widget.setFixedHeight(571)
    widget.setFixedWidth(380)
    widget.show()

    try:
        sys.exit(app.exec_())

    except:
        print("Exiting")