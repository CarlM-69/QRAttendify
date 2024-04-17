from PyQt6.QtWidgets import QDialog, QMainWindow, QMessageBox, QInputDialog, QApplication, QLineEdit
from PyQt6.QtGui import QPixmap, QIcon, QRegularExpressionValidator
from PyQt6.QtCore import QEvent, Qt, QTimer, QRegularExpression
from dotenv import find_dotenv, load_dotenv
from Resources.resources import *
from PyQt6.QtTest import QTest
from datetime import datetime
from PyQt6.uic import loadUi
import configparser
import sqlite3
import qrcode
import random
import bcrypt
import segno
import sys
import cv2
import os

load_dotenv(find_dotenv())

## variables ---------------------------------------------------

actual_setup_passw = os.getenv("ATTENDANCE_DEV_SETUP_PASSWORD")

config = configparser.ConfigParser()

## defines -----------------------------------------------------

def check_special_chars(text):
	special_chars = "!@#$%^&*()-_=+[{]}:|\;',<.>/?`~"

	for char in text:
		if char in special_chars:
			return True
		
	return False

def check_number_chars(text):
	numbers = "0123456789"

	for num in text:
		if num in numbers:
			return True
		
	return False

def check_upper_chars(text):
	for char in text:
		if char.isupper():
			return True
		
	return False

def res_path(rel_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
		
	return os.path.join(base_path, rel_path)

## Main --------------------------------------------------------

class firstTimeSetup(QDialog):
	def __init__(self):
		super().__init__()

		self.ui = loadUi(res_path("UIs/Setup.ui"), self)
		self.setWindowIcon(QIcon(res_path("./Resources/Icons/sfhs_logo.ico")))

		self.ui.choosepass_fill_eye.setPixmap(QPixmap(""))
		self.ui.confirmpass_fill_eye.setPixmap(QPixmap(""))
		
		self.ui.choosepass_fill.textChanged.connect(self.choosepass_fill_event)
		self.ui.choosepass_fill_eye.installEventFilter(self)
		self.ui.confirmpass_fill.textChanged.connect(self.confirmpass_fill_event)
		self.ui.confirmpass_fill_eye.installEventFilter(self)

		self.ui.create.clicked.connect(self.create_b)
		self.ui.cancel.clicked.connect(self.cancel_b)

	def choosepass_fill_event(self, text):
		if len(text) > 0:
			self.ui.choosepass_fill_eye.setPixmap(QPixmap(res_path("./Resources/Icons/eye-close.png")))
		else:
			self.ui.choosepass_fill_eye.setPixmap(QPixmap(""))

	def confirmpass_fill_event(self, text):
		if len(text) > 0:
			self.ui.confirmpass_fill_eye.setPixmap(QPixmap(res_path("./Resources/Icons/eye-close.png")))
		else:
			self.ui.confirmpass_fill_eye.setPixmap(QPixmap(""))

	def eventFilter(self, obj, event):
		match obj:
			case self.ui.choosepass_fill_eye:
				if event.type() == QEvent.Type.MouseButtonPress:
					self.ui.choosepass_fill_eye.setPixmap(QPixmap(res_path("./Resources/Icons/eye-open.png")))
					self.ui.choosepass_fill.setEchoMode(QLineEdit.EchoMode.Normal)
				elif event.type() == QEvent.Type.MouseButtonRelease:
					self.ui.choosepass_fill_eye.setPixmap(QPixmap(res_path("./Resources/Icons/eye-close.png")))
					self.ui.choosepass_fill.setEchoMode(QLineEdit.EchoMode.Password)
			case self.ui.confirmpass_fill_eye:
				if event.type() == QEvent.Type.MouseButtonPress:
					self.ui.confirmpass_fill_eye.setPixmap(QPixmap(res_path("./Resources/Icons/eye-open.png")))
					self.ui.confirmpass_fill.setEchoMode(QLineEdit.EchoMode.Normal)
				elif event.type() == QEvent.Type.MouseButtonRelease:
					self.ui.confirmpass_fill_eye.setPixmap(QPixmap(res_path("./Resources/Icons/eye-close.png")))
					self.ui.confirmpass_fill.setEchoMode(QLineEdit.EchoMode.Password)

		return super().eventFilter(obj, event)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key.Key_Escape:
			event.ignore()

	def closeEvent(self, event):
		self.cancel_b()

	def cancel_b(self):
		sys.exit()

	def create_b(self):
		def toggle_Selectables():
			self.ui.create.setEnabled(not self.ui.create.isEnabled())
			self.ui.cancel.setEnabled(not self.ui.cancel.isEnabled())
			self.ui.name_fill.setReadOnly(not self.ui.name_fill.isReadOnly())
			self.ui.choosepass_fill.setReadOnly(not self.ui.choosepass_fill.isReadOnly())
			self.ui.confirmpass_fill.setReadOnly(not self.ui.confirmpass_fill.isReadOnly())
			self.ui.setuppass_fill.setReadOnly(not self.ui.setuppass_fill.isReadOnly())

		toggle_Selectables()

		name_fill = self.name_fill.text()
		choosepass_fill = self.choosepass_fill.text()
		confirmpass_fill = self.confirmpass_fill.text()
		setuppass_fill = self.setuppass_fill.text()

		if not name_fill:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> You need to put your section or subject name.</p>")
			toggle_Selectables()
			return
		
		if len(name_fill) <= 3:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> Your section or subject name must be longer than 3 characters.</p>")
			toggle_Selectables()
			return
		
		if not choosepass_fill:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> You must create an administrator password.</p>")
			toggle_Selectables()
			return
		
		if len(choosepass_fill) <= 8:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> Your administrator password must be longer than 8 characters.</p>")
			toggle_Selectables()
			return
		
		check = []

		if not check_special_chars(choosepass_fill): check.append("special character(s)")
		if not check_number_chars(choosepass_fill): check.append("number(s)")
		if not check_upper_chars(choosepass_fill): check.append("uppercase letter(s)")

		if check:
			if len(check) >= 2 and check[-1] == "uppercase letter(s)":
				self.ui.error_message.setText(f"<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> Your administrator password should have at least one { ', ' .join(check[:-1]) } and an { check[-1] }.</p>")
			else:
				self.ui.error_message.setText(f"<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> Your administrator password should have at least one { ', ' .join(check) }.</p>")
			toggle_Selectables()
			return
		
		if not confirmpass_fill:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> You must confirm your Administrator password.</p>")
			toggle_Selectables()
			return
		
		if choosepass_fill != confirmpass_fill:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> Administrator password confirmation does not match.</p>")
			toggle_Selectables()
			return
		
		if not setuppass_fill:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> You must type the setup password.</p>")
			toggle_Selectables()
			return

		if setuppass_fill != actual_setup_passw:
			self.ui.error_message.setText("<p><span style=' font-weight:700; color:#ff0000;'>FAILED:</span> Setup password incorrect.</p>")
			toggle_Selectables()
			return
		
		self.ui.error_message.setText("")
		
		message = QMessageBox.question(
			self,
			"QRAttendify - Confirmation",
			"\nAre you sure that you want to proceed with this information?\n\nYou can still change the informations later.\n",
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
		)
		
		if message == QMessageBox.StandardButton.Yes:
			pass
		elif message == QMessageBox.StandardButton.Cancel:
			toggle_Selectables()
			return

		self.ui.error_message.setText("<p><span style=' font-weight:700; color:#00ff00;'>SUCCESS:</span> Setup done, please wait.</p>")

		process_adminPass = choosepass_fill.encode()
		secured_adminPass = bcrypt.hashpw(process_adminPass, bcrypt.gensalt())

		config["Info"] = {
			"Name": name_fill,
			"AdminPass": secured_adminPass.decode("utf-8")
		}

		QTest.qWait(random.randint(1000, 3000))

		with open("./config.ini", "w") as info:
			config.write(info)

		self.hide()

class promptScreen(QMainWindow):
	def __init__(self):
		super().__init__()

		self.ui = loadUi(res_path("UIs/MainMenu.ui"), self)
		self.setWindowIcon(QIcon(res_path("./Resources/Icons/sfhs_logo.ico")))

		if not os.path.exists("./config.ini"):
			firstTimeSetup().exec()
		
		config.read("./config.ini")
		self.setWindowTitle("QRAttendify - Main Menu - " + config["Info"]["Name"])
		self.ui.class_name.setText(f"<span style='font-weight:600; color:#ffffff;'>{ config['Info']['Name'] }</span>")

		self.ui.attendance.installEventFilter(self)
		self.ui.register_.installEventFilter(self)

		objs = [
			self.ui.attendance,
			self.ui.register_,
			self.ui.settings,
			self.ui.students
		]

		for i in objs:
			i.enterEvent = lambda event, obj = i, type = "enter": self.buttons_m(event, obj, type)
			i.leaveEvent = lambda event, obj = i, type = "leave": self.buttons_m(event, obj, type)

		self.ui.attendance_icon.setPixmap(QPixmap(res_path("")))
		self.ui.register_icon.setPixmap(QPixmap(res_path("")))
		self.ui.settings_icon.setPixmap(QPixmap(res_path("")))
		self.ui.students_icon.setPixmap(QPixmap(res_path("")))
	
	def eventFilter(self, obj, event):
		match obj:
			case self.ui.attendance | self.ui.register_:
				if event.type() == QEvent.Type.MouseButtonPress:
					self.inputPassword(obj)

		return super().eventFilter(obj, event)
	
	def inputPassword(self, obj, text=""):
		password, ok = QInputDialog.getText(
			self,
			"QRAttendify - Administrator Login",
			f"Enter the Administrator Password to Continue.\n{ text }",
			QLineEdit.EchoMode.Password
		)

		if ok:
			if password:
				if bcrypt.checkpw(password.encode("utf-8"), config["Info"]["AdminPass"].encode("utf-8")):
					match obj:
						case self.ui.attendance:
							Attendance().show()
							self.close()
						case self.ui.register_:
							Register().show()
							self.close()
				else:
					self.inputPassword(obj, "\nWrong Administrator Password.\n")
			else: 
				self.inputPassword(obj, "\nEnter the Administrator Password.\n")

	def buttons_m(self, event, obj, type):
		if type == "enter":
			match obj:
				case self.ui.attendance:
					self.ui.left_top.setStyleSheet("#left_top { border-radius: 15px; background: rgba(255, 255, 255, 0.9); }")
					self.ui.attendance_icon.setPixmap(QPixmap(res_path("./Resources/Icons/attendance.png")))
				case self.ui.register_:
					self.ui.right_top.setStyleSheet("#right_top { border-radius: 15px; background: rgba(255, 255, 255, 0.9); }")
					self.ui.register_icon.setPixmap(QPixmap(res_path("./Resources/Icons/reg_student.png")))
				case self.ui.settings:
					self.ui.left_bottom.setStyleSheet("#left_bottom { border-radius: 15px; background: rgba(255, 255, 255, 0.9); }")
					self.ui.settings_icon.setPixmap(QPixmap(res_path("./Resources/Icons/settings.png")))
				case self.ui.students:
					self.ui.right_bottom.setStyleSheet("#right_bottom { border-radius: 15px; background: rgba(255, 255, 255, 0.9); }")
					self.ui.students_icon.setPixmap(QPixmap(res_path("./Resources/Icons/students.png")))
		elif type == "leave":
			match obj:
				case self.ui.attendance:
					self.ui.left_top.setStyleSheet("#left_top { border-radius: 15px; background: rgba(255, 255, 255, 0.6); }")
					self.ui.attendance_icon.setPixmap(QPixmap(res_path("")))
				case self.ui.register_:
					self.ui.right_top.setStyleSheet("#right_top { border-radius: 15px; background: rgba(255, 255, 255, 0.6); }")
					self.ui.register_icon.setPixmap(QPixmap(res_path("")))
				case self.ui.settings:
					self.ui.left_bottom.setStyleSheet("#left_bottom { border-radius: 15px; background: rgba(255, 255, 255, 0.6); }")
					self.ui.settings_icon.setPixmap(QPixmap(res_path("")))
				case self.ui.students:
					self.ui.right_bottom.setStyleSheet("#right_bottom { border-radius: 15px; background: rgba(255, 255, 255, 0.6); }")
					self.ui.students_icon.setPixmap(QPixmap(res_path("")))

class Attendance(QMainWindow):
	def __init__(self):
		super().__init__()

		self.ui = loadUi(res_path("UIs/Attendance.ui"), self)
		self.setWindowIcon(QIcon(res_path("./Resources/Icons/sfhs_logo.ico")))
		
		config.read("./config.ini")
		self.ui.class_name.setText(f"<p><span style='font-weight:600; color:#ffffff;'>{ config['Info']['Name'] }</span></p>")
		self.ui.student_name.setText("<p><span style='font-size:20pt; font-weight:600; color:#ffffff;'>Searching</span></p>")
		self.ui.student_section.setText("<p><span style='color:#ffffff;'></span></p>")
		self.ui.student_message.setText("<p><span style='font-size:10pt; font-weight:600; color:#ffffff;'></span></p>")

		objs = [
			self.ui.birthdate,
			self.ui.birthdate_fill,
			self.ui.age,
			self.ui.age_fill,
			self.ui.login_time,
			self.ui.login_time_fill,
			self.ui.present_streak,
			self.ui.present_streak_fill
		]

		for i in objs:
			i.setText("<p><span style='font-size:14pt; font-weight:600; color:#ffffff;'></span></p>")

		self.ui.display_status.setText("<p><span style='font-size:12pt; font-weight:600; color:#ffffff;'>INITIALIZING CAMERA</span></p>")
		self.ui.time.setText(f"<p><span style='font-size:20pt; font-weight:600; color:#ffffff;'>{ datetime.now().strftime('%I:%M %p') }</span></p>")
		self.ui.date.setText(f"<p><span style='font-size:20pt; font-weight:600; color:#ffffff;'>{ datetime.now().strftime('%A, %B %d') }</span></p>")
		self.showFullScreen()

		self.ui.back.installEventFilter(self)
		self.ui.register_.installEventFilter(self)

		self.update_timer = QTimer(self)
		self.update_timer.timeout.connect(self.heartBeat)
		self.update_timer.start(1000)
	
	def eventFilter(self, obj, event):
		match obj:
			case self.ui.back | self.ui.register_:
				if event.type() == QEvent.Type.MouseButtonPress:
					self.inputPassword(obj)

		return super().eventFilter(obj, event)
	
	def inputPassword(self, obj, text=""):
		password, ok = QInputDialog.getText(
			self,
			"QRAttendify - Administrator Login",
			f"Enter the Administrator Password to Continue.\n{ text }",
			QLineEdit.EchoMode.Password
		)

		if ok:
			if password:
				if bcrypt.checkpw(password.encode("utf-8"), config["Info"]["AdminPass"].encode("utf-8")):
					match obj:
						case self.ui.back:
							promptScreen().show()
							self.close()
						case self.ui.register_:
							Register().show()
							self.close()
				else:
					self.inputPassword(obj, "\nWrong Administrator Password.\n")
			else: 
				self.inputPassword(obj, "\nEnter the Administrator Password.\n")
	
	def heartBeat(self):
		self.ui.time.setText(f"<p><span style='font-size:20pt; font-weight:600; color:#ffffff;'>{ datetime.now().strftime('%I:%M %p') }</span></p>")
		self.ui.date.setText(f"<p><span style='font-size:20pt; font-weight:600; color:#ffffff;'>{ datetime.now().strftime('%A, %B %d') }</span></p>")

class Register(QMainWindow):
	def __init__(self):
		super().__init__()

		self.ui = loadUi(res_path("UIs/Register.ui"), self)
		self.setWindowIcon(QIcon(res_path("./Resources/Icons/sfhs_logo.ico")))
		
		config.read("./config.ini")
		self.ui.class_name.setText(f"<p><span style='font-weight:600; color:#ffffff;'>{ config['Info']['Name'] }</span></p>")
		self.ui.error_message.setText("")
		# self.showFullScreen()

		suffixes = [
			"",
			"Jr.",
			"Sr.",
			"I",
			"II",
			"III",
			"IV",
			"V"
		]

		months = [
			"Select a month.",
			"January",
			"February",
			"March",
			"April",
			"May",
			"June",
			"July",
			"August",
			"September",
			"October",
			"November",
			"December"
		]

		objs = [
			self.ui.first_name_fill,
			self.ui.middle_name_fill,
			self.ui.surname_fill,
			self.ui.suffix_fill,
			self.ui.section_fill,
			self.ui.lrn_fill,
			self.ui.email_fill,
			self.ui.confirm_email_fill,
			self.ui.birthdate_month_fill,
			self.ui.birthdate_day_fill,
			self.ui.birthdate_year_fill,
			self.ui.register_student
		]

		eventFilters = [
			self.ui.back,
			self.ui.attendance,
			self.ui.first_name_fill,
			self.ui.middle_name_fill,
			self.ui.surname_fill,
			self.ui.suffix_fill,
			self.ui.section_fill,
			self.ui.lrn_fill,
			self.ui.email_fill,
			self.ui.confirm_email_fill,
			self.ui.birthdate_month_fill,
			self.ui.birthdate_day_fill,
			self.ui.birthdate_year_fill,
			self.ui.register_student
		]

		for i in suffixes:
			self.ui.suffix_fill.addItem(i)

		for i in months:
			self.ui.birthdate_month_fill.addItem(i)

		self.ui.birthdate_day_fill.addItem("Select a day.")
		for i in range(1, 32):
			self.ui.birthdate_day_fill.addItem(f"{i}")

		self.ui.birthdate_year_fill.addItem("Select a year.")
		for i in reversed(range(1950, int(datetime.now().strftime("%Y")) + 1)):
			self.ui.birthdate_year_fill.addItem(f"{i}")

		for i in eventFilters:
			i.installEventFilter(self)

		for i in objs:
			i.enterEvent = lambda event, obj = i, type = "enter": self.fills_m(event, obj, type)
			i.leaveEvent = lambda event, obj = i, type = "leave": self.fills_m(event, obj, type)

		self.ui.first_name_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z\s]+$")))
		self.ui.middle_name_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z]+$")))
		self.ui.surname_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z\s]+$")))
		self.ui.section_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z\s]+$")))
		self.ui.lrn_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d+$")))
		self.ui.email_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$")))
		self.ui.confirm_email_fill.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$")))

		self.ui.birthdate_month_fill.model().item(0).setEnabled(False)
		self.ui.birthdate_day_fill.model().item(0).setEnabled(False)
		self.ui.birthdate_year_fill.model().item(0).setEnabled(False)

	def eventFilter(self, obj, event):
		match obj:
			case self.ui.register_student:
				if event.type() == QEvent.Type.MouseButtonPress:
					error_message = self.ui.error_message

					def checkEmail(email):
						allowed_domains = [
							"@gmail.com",
							"@yahoo.com",
							"@outlook.com",
							"@hotmail.com",
							"@depedqc.ph"
						]

						for domain in allowed_domains:
							if email.endswith(domain):
								return True
							
						return False

					if not self.ui.first_name_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must enter your First Name.</span></p>")
						return False
					
					if not self.ui.surname_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must enter your Surname.</span></p>")
						return False
					
					if not self.ui.section_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must enter your Section.</span></p>")
						return False
					
					if not self.ui.lrn_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must enter your LRN.</span></p>")
						return False
					
					if not self.ui.email_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must enter your Email.</span></p>")
						return False
					
					if not checkEmail(self.ui.email_fill.text()):
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must enter a valid Email.</span></p>")
						return False
					
					if not self.ui.confirm_email_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must re-enter your Email.</span></p>")
						return False
					
					if self.ui.email_fill.text() != self.ui.confirm_email_fill.text():
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>The email didn't match.</span></p>")
						return False
					
					if self.ui.birthdate_month_fill.currentIndex() == 0:
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must select your Birthdate Month.</span></p>")
						return False
					
					if self.ui.birthdate_day_fill.currentIndex() == 0:
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must select your Birthdate Day.</span></p>")
						return False
					
					if self.ui.birthdate_year_fill.currentIndex() == 0:
						error_message.setText("<p><span style='color:#ff0000;'>ERROR: </span><span style='color:#ffffff;'>You must select your Birthdate Year.</span></p>")
						return False
					
					print("success create")
			case self.ui.back | self.ui.attendance:
				if event.type() == QEvent.Type.MouseButtonPress:
					self.inputPassword(obj)
			case self.ui.suffix_fill | self.ui.birthdate_month_fill | self.ui.birthdate_day_fill | self.ui.birthdate_year_fill:
				if event.type() == QEvent.Type.MouseButtonPress:
					obj.setStyleSheet("#infos QComboBox { selection-background-color: transparent; background: transparent; color: white; } #infos QComboBox::down-arrow { image: url(:/icons/Icons/drop-down_focus.png); margin-right:15px; } ")
				elif event.type() == QEvent.Type.FocusOut:
					obj.setStyleSheet("#infos QComboBox { selection-background-color: transparent; background: transparent; color: white; } #infos QComboBox::down-arrow { image: url(:/icons/Icons/drop-down_focus.png); margin-right:15px; } ")

					if obj.currentIndex() == 0:
						obj.setStyleSheet("#infos QComboBox { selection-background-color: transparent; background: transparent; color: rgb(110, 110, 110); } #infos QComboBox::down-arrow { image: url(:/icons/Icons/drop-down_unfocus.png); margin-right:15px; } ")
			case _:
				if event.type() == QEvent.Type.FocusIn:
					obj.setStyleSheet("#infos QLineEdit { background: transparent; color: white; border-bottom: 2px solid white; }")
				elif event.type() == QEvent.Type.FocusOut:
					if len(obj.text()) > 0:
						obj.setStyleSheet("#infos QLineEdit { background: transparent; color: white; }")
					else:
						obj.setStyleSheet("#infos QLineEdit { background: transparent; color: rgb(145, 145, 145); }")

		return super().eventFilter(obj, event)
	
	def inputPassword(self, obj, text=""):
		password, ok = QInputDialog.getText(
			self,
			"QRAttendify - Administrator Login",
			f"Enter the Administrator Password to Continue.\n{ text }",
			QLineEdit.EchoMode.Password
		)

		if ok:
			if password:
				if bcrypt.checkpw(password.encode("utf-8"), config["Info"]["AdminPass"].encode("utf-8")):
					match obj:
						case self.ui.back:
							promptScreen().show()
							self.close()
						case self.ui.attendance:
							Attendance().show()
							self.close()
				else:
					self.inputPassword(obj, "\nWrong Administrator Password.\n")
			else: 
				self.inputPassword(obj, "\nEnter the Administrator Password.\n")
	
	def fills_m(self, event, obj, type):
		if type == "enter":
			match obj:
				case self.ui.suffix_fill | self.ui.birthdate_month_fill | self.ui.birthdate_day_fill | self.ui.birthdate_year_fill:
					if not obj.hasFocus():
						obj.setStyleSheet("#infos QComboBox { selection-background-color: transparent; background: transparent; color: white; } #infos QComboBox::down-arrow { image: url(:/icons/Icons/drop-down_focus.png); margin-right:15px; } ")
				case self.ui.register_student:
					self.ui.register_student.setStyleSheet("#register_student { background: rgba(50, 50, 50, 0.4); padding: 5px 10px; }")
				case _:
					if not obj.hasFocus():
						obj.setStyleSheet("#infos QLineEdit { background: transparent; color: white; }")
		elif type == "leave":
			match obj:
				case self.ui.suffix_fill | self.ui.birthdate_month_fill | self.ui.birthdate_day_fill | self.ui.birthdate_year_fill:
					if not obj.hasFocus():
						if obj.currentIndex() <= 0:
							obj.setStyleSheet("#infos QComboBox { selection-background-color: transparent; background: transparent; color: rgb(110, 110, 110); } #infos QComboBox::down-arrow { image: url(:/icons/Icons/drop-down_focus.png); margin-right:15px; } ")
				case self.ui.register_student:
					self.ui.register_student.setStyleSheet("#register_student { background: rgba(0, 0, 0, 0.4); padding: 5px 10px; }")
				case _:
					if not obj.hasFocus():
						if len(obj.text()) <= 0:
							obj.setStyleSheet("#infos QLineEdit { background: transparent; color: rgb(145, 145, 145); }")

if __name__ == "__main__":
	prompt = QApplication(sys.argv)
	window = promptScreen()
	window.show()

	sys.exit(prompt.exec())