from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from PyQt5.QtGui import QIcon

from reporterCore import Ui_MainWindow

from dbUtils import StorageUtilities

import sys

from datetime import datetime

import calendar

from reportIO import ReportMint

class ReporterInterface(QMainWindow):
	def __init__(self):
		super(ReporterInterface, self).__init__()

		# specify the title
		self.setWindowIcon(QIcon("../assets/LOGO.png"))

		# fixed size
		self.setFixedSize(1000, 600)

		self.reporterUi = Ui_MainWindow()

		self.reporterUi.setupUi(self)


class HelperUtils:
	monthsMap = {
		1: 'January',
		2: 'February',
		3: 'March',
		4: 'April',
		5: 'May',
		6: 'June',
		7: 'July',
		8: 'August',
		9: 'September',
		10: 'October',
		11: 'November',
		12: 'December'
	}

	def __init__(self):
		pass


	def getMonthsList(self):
		"""
		Get a list of months
		"""
		return list([eachMonth.upper() for eachMonth in self.monthsMap.values()])


	def resolveMonthToTag(self, monthName):
		# reversed
		reversedMonthMap = { eachMonth.upper() : eachTag for eachTag, eachMonth in self.monthsMap.items() }

		return reversedMonthMap[monthName]


	def getCurrentYearAndMonth(self):
		# get current instance
		currentDate = datetime.now()

		return currentDate.year, currentDate.month


	def getYearsListOrYear(self, getState):
		# get present
		currentDate = datetime.now()


		if getState == 1:
			# create a list of years
			dataToken = [
				str(i) for i in range(2022, currentDate.year + 1)
			]

		else:
			# current
			dataToken = str(currentDate.year)

		return dataToken

	def getPresentDateOrMonth(self, getState):
		# get the date
		todaysDate = datetime.now()

		if getState == 1:
			returnValue = todaysDate.strftime("%b, %d, %Y")

		else:
			returnValue = todaysDate.strftime("%B").upper()

		return returnValue


class ReporterBase:
	# application instance
	app = QApplication(sys.argv)

	# reporter interface instance
	reporterGui = ReporterInterface()

	def __init__(self):
		# load interface controls
		self.loadInterfaceControls()



	def gotoTab(self, tabToVisit):
		# go to the tab
		self.reporterGui.reporterUi.panel_tabs_holder.setCurrentIndex(tabToVisit)


	def displayModalMessage(self, messageToDisplay, messageTag=1):
		"""
		Display message with message box
		"""
		alertBox = QMessageBox()

		# set title
		alertBox.setWindowTitle("SmartReporter Alerts \u00A9 2023")

		# set icon
		alertBox.setWindowIcon(QIcon("../assets/LOGO.png"))

		# set the message
		alertBox.setText(messageToDisplay)

		# set the icon
		if messageTag == 1:
			# info icon
			alertBox.setIcon(QMessageBox.Information)

		elif messageTag == 2:
			alertBox.setIcon(QMessageBox.Warning)

		else:
			alertBox.setIcon(QMessageBox.Critical)


		# add ok button
		alertBox.addButton(QMessageBox.Ok)


		# display
		if alertBox.exec():
			# just display
			alertBox.show()

		else:
			# execute
			alertBox.exec()


		return



	def employeeRegisterControl(self):
		# get the name
		submittedName = self.reporterGui.reporterUi.employee_name_input.text().strip()

		submittedRole = self.reporterGui.reporterUi.employee_role_input.currentText().strip()

		# validate
		isValid = len(submittedName) > 0

		if isValid is True:
			# check for roles
			if len(submittedRole) > 0:
				# try saving it
				duplicateStatus = StorageUtilities().recordNewEmployee(employeeName=submittedName, employeRole=submittedRole)

				if duplicateStatus is True:
					messageToDisplay = f"The Employee '{submittedName.upper()}' already exists!"

					messageTag = 2

				else:
					# update the list
					self.loadEmployeeNames()

					# clean
					self.resetHomeInterface()

					# update
					self.loadPaidOverPendingStatistics()

					messageToDisplay = f"The Employee '{submittedName.upper()}' was saved successfully!"

					messageTag = 1

			
			else:
				messageToDisplay = f"No role was selected, please add some if they are missing!"

				messageTag = 2


		else:
			messageToDisplay = "Please Enter a name!"

			messageTag = 2


		# clear area
		self.reporterGui.reporterUi.employee_name_input.clear()

		# reset roles
		self.reporterGui.reporterUi.employee_role_input.setCurrentIndex(0)


		# # alert
		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return



	def deleteSelectedEmployeeProfile(self):
		# get the selected name
		selectedEmployeeName = self.reporterGui.reporterUi.employees_list_register.currentItem().text()

		# delete the profile of the employee
		StorageUtilities().deleteSelectedEmployee(employeeName=selectedEmployeeName)

		# update
		self.loadEmployeeNames()

		# deactivate the delete button
		self.toggleEmployeeDelete(False)

		# wipe
		self.resetHomeInterface()

		# update
		self.loadPaidOverPendingStatistics()

		# alert
		messageToDisplay=f"The Details Of '{selectedEmployeeName}' was deleted successfully!"

		messageTag = 1


		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return




	def rolesRegisterControl(self):
		# StorageUtilities
		submittedRole = self.reporterGui.reporterUi.role_register_input.text().strip()

		# length validity
		isValid = len(submittedRole) > 0

		if isValid is True:
			# try saving it
			duplicateStatus = StorageUtilities().recordNewRole(roleName=submittedRole)

			if duplicateStatus is True:
				messageToDisplay = f"The role '{submittedRole.upper()}' already exists!"

				messageTag = 2

			else:
				# update the list
				self.loadEmployeeRoles()

				messageToDisplay = f"The role '{submittedRole.upper()}' was saved successfully!"

				messageTag = 1

		else:
			messageToDisplay = "Please Type something!"

			messageTag = 2



		# clear area
		self.reporterGui.reporterUi.role_register_input.clear()


		# # alert
		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return


	def deleteEmployeeRole(self):
		# get
		roleToDelete = self.reporterGui.reporterUi.available_roles_list.currentText()

		# print(roleToDelete)

		if len(roleToDelete) > 0:
			# make the deletion
			StorageUtilities().deleteSelectedRole(roleName=roleToDelete)

			# update
			self.loadEmployeeRoles()

			# alert
			messageToDisplay=f"The role '{roleToDelete}' was deleted successfully!"

			messageTag = 1

		else:
			# absent
			messageToDisplay="There are no roles added yet!"

			messageTag = 2

		# alert
		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return



	def updateBasicPayAmount(self):
		# get selected amount
		selectedBasicPay = self.reporterGui.reporterUi.basic_pay_earned.value()

		# save the new pay
		StorageUtilities().writeNewBasicAmount(selectedBasicPay)

		# wipe
		self.resetHomeInterface()

		# alert
		messageToDisplay=f"The Basic Pay Amount was successfully set to Shs.{selectedBasicPay} !"

		messageTag = 1


		# update
		self.dailyBasicPay = selectedBasicPay

		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return




	def issuePaymentToEmployee(self):
		# writeNewPaymentDetail

		gottenWorkedDays = self.reporterGui.reporterUi.days_worked_selector.value()

		if gottenWorkedDays == 0 or self.dailyBasicPay == 0:
			# alert
			messageToDisplay = "Check the Days worked or the Basic Pay either of them is 0 !"

			messageTag = 3


		else:
			# year and month
			gottenYear, gottenMonth = HelperUtils().getCurrentYearAndMonth()

			# employee
			associatedEmployee = self.reporterGui.reporterUi.employee_preview_finance.currentItem().text()

			# save
			StorageUtilities().writeNewPaymentDetail(
				employeeName=associatedEmployee,
				currentMonth=gottenMonth,
				currentYear=gottenYear,
				currentBasicPay=self.dailyBasicPay,
				daysWorked=gottenWorkedDays)

			# after, do the cleanup
			self.loadEmployeeNames()

			# clean
			self.resetHomeInterface()

			# stat
			self.loadPaidOverPendingStatistics()

			# update preview
			self.updateReportViewData(changeEvent=None)

			# amount
			totalPaymentAmount = gottenWorkedDays * self.dailyBasicPay

			# success
			messageToDisplay = f"Payment Of Shs.{totalPaymentAmount} was recorded for {associatedEmployee} !"

			messageTag = 1


		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)


		return




	def reversePaymentMadeToEmployee(self):
		# reverse payment
		# greater
		gottenYear, gottenMonth = HelperUtils().getCurrentYearAndMonth()

		# employee
		associatedEmployee = self.reporterGui.reporterUi.employee_preview_finance.currentItem().text()

		# revoke
		StorageUtilities().revokePaymentDetail(employeeName=associatedEmployee, currentMonth=gottenMonth, currentYear=gottenYear)

		# after, do the cleanup
		self.loadEmployeeNames()

		# clean
		self.resetHomeInterface()

		# stat
		self.loadPaidOverPendingStatistics()

		# update preview
		self.updateReportViewData(changeEvent=None) 


		# success
		messageToDisplay = f"A Payment that was made to {associatedEmployee} has been cancelled!"

		messageTag = 1


		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return



	def updateEmployeePaymentTotal(self, newValue):
		# calc
		calculatedTotalPayment = newValue * self.dailyBasicPay


		# display
		self.displayPaymentTotal(amountToDisplay=calculatedTotalPayment)


		return




	def loadRolesControlEvents(self):
		# add new role
		self.reporterGui.reporterUi.save_new_role.clicked.connect(self.rolesRegisterControl)

		self.reporterGui.reporterUi.delete_present_role.clicked.connect(self.deleteEmployeeRole)

		self.reporterGui.reporterUi.save_employee_button.clicked.connect(self.employeeRegisterControl)

		self.reporterGui.reporterUi.delete_employee_trigger.clicked.connect(self.deleteSelectedEmployeeProfile)

		self.reporterGui.reporterUi.save_basic_pay.clicked.connect(self.updateBasicPayAmount)

		self.reporterGui.reporterUi.pay_employee_button.clicked.connect(self.issuePaymentToEmployee)

		self.reporterGui.reporterUi.delete_cash_out.clicked.connect(self.reversePaymentMadeToEmployee)

		self.reporterGui.reporterUi.days_worked_selector.valueChanged.connect(self.updateEmployeePaymentTotal)

		self.reporterGui.reporterUi.generate_report_trigger.clicked.connect(self.generateMonthlyPaymentReport)

		return





	def loadEmployeeRoles(self):
		# wipe
		self.reporterGui.reporterUi.available_roles_list.clear()

		self.reporterGui.reporterUi.employee_role_input.clear()

		self.reporterGui.reporterUi.available_roles_list.addItems(StorageUtilities().getPresentRoles())

		self.reporterGui.reporterUi.employee_role_input.addItems(StorageUtilities().getPresentRoles())


		return



	def loadBasicAmount(self):
		# get basic amount
		foundAmount = StorageUtilities().getPresentBasicAmount()

		# make the pay value available
		self.dailyBasicPay = foundAmount

		# display
		self.reporterGui.reporterUi.basic_pay_earned.setValue(foundAmount)

		return



	def recordsPresenceCheck(self):
		# year and month
		todaysYear, todaysMonth = HelperUtils().getCurrentYearAndMonth()

		# count
		paidEmployeesCount = StorageUtilities().getCountOfAlreadyPaidEmployees(currentMonth=todaysMonth, currentYear=todaysYear)

		return paidEmployeesCount > 0



	def generateStampName(self, monthTag, yearValue):
		# month name
		monthName = HelperUtils().monthsMap[monthTag]

		# feed in
		formedName = f"{monthName}-{yearValue}"

		return formedName


	def generateMonthlyPaymentReport(self):
		# check if there are records
		areThereRecords = self.recordsPresenceCheck()

		if areThereRecords is True:
			# get the month and year
			selectedYear, selectedMonth = self.getResolvedMonthAndYear()

			# get the records
			presentRecords = StorageUtilities().getReportRecords(currentMonth=selectedMonth, currentYear=selectedYear)

			# get stamp name
			reportStampName = self.generateStampName(monthTag=selectedMonth, yearValue=selectedYear)

			# create the report
			ReportMint().exportReportDetails(reportData=presentRecords, reportStamp=reportStampName, monthName=HelperUtils().monthsMap[selectedMonth], yearValue=selectedYear)


			# alert
			messageToDisplay = "Your generated report is stored at your computer desktop!"

			messageTag = 1



		else:
			# success
			messageToDisplay = "There are no payment records yet!"

			messageTag = 2


		self.displayModalMessage(messageToDisplay=messageToDisplay, messageTag=messageTag)

		return







	def loadEmployeeNames(self):
		# clean viewers
		self.reporterGui.reporterUi.employee_preview_finance.clear()

		self.reporterGui.reporterUi.employees_list_register.clear()

		self.reporterGui.reporterUi.employee_preview_finance.addItems(StorageUtilities().getPresentEmployees())

		self.reporterGui.reporterUi.employees_list_register.addItems(StorageUtilities().getPresentEmployees())


		return


	def toggleEmployeeDelete(self, activationStatus):
		# activate / deactivate delete button
		self.reporterGui.reporterUi.delete_employee_trigger.setEnabled(activationStatus)

		return


	def toggleCashoutCancel(self, activationStatus):
		# hide / show
		self.reporterGui.reporterUi.delete_cash_out.setVisible(activationStatus)

		if activationStatus is True:
			self.reporterGui.reporterUi.pay_employee_button.setVisible(False)

		return


	def toggleCashOutEmployee(self, activationStatus):
		# appear / hide
		self.reporterGui.reporterUi.pay_employee_button.setVisible(activationStatus)

		if activationStatus is True:
			self.reporterGui.reporterUi.delete_cash_out.setVisible(False)

		return


	def activateEmployeeDeleteButton(self, itemClickedEvent):
		if itemClickedEvent is None:
			pass

		else:
			# activate the delete button
			self.toggleEmployeeDelete(True)


		return



	def employeeRoleLoader(self, roleToLoad="---"):
		# load roles
		self.reporterGui.reporterUi.employee_role_display.setText(roleToLoad)

		return


	def paymentStatusLoader(self, paymentStatus=None):
		# initial color
		defaultColor = "#566D7E"

		# load status
		if paymentStatus is None:
			statusMessage = "---"

			displayColor = defaultColor

		else:
			# draft a message
			statusMessage = "PAID" if paymentStatus is True else "PENDING"

			# display colors
			displayColor = defaultColor if paymentStatus is False else "#008000"

		# update the colors
		self.reporterGui.reporterUi.payment_status_show.setStyleSheet(f"font: 75 15pt 'Courier';background-color: {displayColor}; color: rgb(255, 255, 255);")

		# display the message
		self.reporterGui.reporterUi.payment_status_show.setText(statusMessage)

		return



	def makeWorkDaySpinBoxEditable(self, readonlyState):
		# result
		self.reporterGui.reporterUi.days_worked_selector.setReadOnly(readonlyState)

		return



	def loadPaidEmployeeDetail(self, employeeName, presentYear, presentMonth):
		# get the details
		workedDaysCount, accumulatedValue = StorageUtilities().getDaysWorkedAndTotalForEmployee(employeeName=employeeName, yearValue=presentYear, monthValue=presentMonth)

		# value
		self.reporterGui.reporterUi.days_worked_selector.setValue(workedDaysCount)

		# display cash amount
		self.displayPaymentTotal(amountToDisplay=accumulatedValue)

		return


	def activateCashoutButton(self, itemClickedEvent):
		if itemClickedEvent is None:
			pass

		else:
			# reset
			self.resetHomeInterface()

			# get the name of the employee
			selectedName = itemClickedEvent.text()

			# year and month
			foundYear, foundMonth = HelperUtils().getCurrentYearAndMonth()


			# get role and status of employee
			foundRole, foundStatus = StorageUtilities().getEmployeeRoleAndStatus(employeeName=selectedName, currentYear=foundYear, currentMonth=foundMonth)

			# print(f"Role:{foundRole} , Status:{foundStatus}")

			if foundStatus is True:
				# load their detail
				self.loadPaidEmployeeDetail(employeeName=selectedName, presentYear=foundYear, presentMonth=foundMonth)

				# activate or deactivate spinbox
				self.makeWorkDaySpinBoxEditable(readonlyState=True)

			else:
				# make it changeable
				self.makeWorkDaySpinBoxEditable(readonlyState=False)

			# display role
			self.employeeRoleLoader(roleToLoad=foundRole)

			# load status
			self.paymentStatusLoader(paymentStatus=foundStatus)


			# activate the cashout button or cancel
			if foundStatus is True:
				# show
				self.toggleCashoutCancel(True)

			else:
				# show
				self.toggleCashOutEmployee(True)

		return


	def displayPaymentTotal(self, amountToDisplay=None):
		# determine the display value
		displayAmountValue = "0/=" if amountToDisplay is None else f"{amountToDisplay}/="

		self.reporterGui.reporterUi.employee_total_amount.setText(displayAmountValue)

		return


	def resetHomeInterface(self):
		# disable cashout
		self.toggleCashOutEmployee(False)

		# hide cancel
		self.toggleCashoutCancel(False)

		# clean total area
		self.displayPaymentTotal()

		# role cleaner
		self.employeeRoleLoader()

		# load status
		self.paymentStatusLoader()

		# reset worked days
		self.reporterGui.reporterUi.days_worked_selector.setValue(0)

		# make it editable
		self.makeWorkDaySpinBoxEditable(readonlyState=False)

		return



	def loadMonthDaysData(self):
		# get the month and year
		currentYear, currentMonth = HelperUtils().getCurrentYearAndMonth()

		# get the number of days in the month
		numberOfDaysInMonth = calendar.monthrange(currentYear, currentMonth)[1]

		# set the maximum
		self.reporterGui.reporterUi.days_worked_selector.setMaximum(numberOfDaysInMonth)

		return


	def loadPaidOverPendingStatistics(self):
		# get count of those present
		presentEmployeesCount = StorageUtilities().getCountOfAllEmployees()

		# year and month
		todaysYear, todaysMonth = HelperUtils().getCurrentYearAndMonth()

		# count
		paidEmployeesCount = StorageUtilities().getCountOfAlreadyPaidEmployees(currentMonth=todaysMonth, currentYear=todaysYear)


		# message
		statisticsMessage = f"{paidEmployeesCount} Of {presentEmployeesCount}"

		
		# update
		self.reporterGui.reporterUi.paid_no_paid_statistics.setText(statisticsMessage)

		return



	def loadReportPreview(self, previewText):
		# clean
		self.reporterGui.reporterUi.report_details.clear()

		# display
		self.reporterGui.reporterUi.report_details.setPlainText(previewText)

		return



	def getResolvedMonthAndYear(self):
		# month name
		selectedMonthName = self.reporterGui.reporterUi.report_month_list.currentText()

		# resolved tag
		resolvedMonthTag = HelperUtils().resolveMonthToTag(monthName=selectedMonthName)

		# get the year
		resolvedYearValue = int(self.reporterGui.reporterUi.report_year_list.currentText())

		return resolvedYearValue, resolvedMonthTag



	def updateReportViewData(self, changeEvent):
		# get the month and the year selected
		resolvedYearValue, resolvedMonthTag = self.getResolvedMonthAndYear()


		# get the display text
		reportPreview = StorageUtilities().getRecentReportData(currentMonth=resolvedMonthTag, currentYear=resolvedYearValue)

		# display
		self.loadReportPreview(previewText=reportPreview)

		return

	def loadInterfaceControls(self):
		"""
		Add event triggers
		"""
		# navigation

		self.reporterGui.reporterUi.visit_finance.clicked.connect(lambda:self.gotoTab(0))

		self.reporterGui.reporterUi.visit_register.clicked.connect(lambda:self.gotoTab(1))

		self.reporterGui.reporterUi.visit_history.clicked.connect(lambda:self.gotoTab(2))


		# load the date
		self.reporterGui.reporterUi.date_display_label.setText(HelperUtils().getPresentDateOrMonth(1))

		# disable delete
		self.toggleEmployeeDelete(False)


		# reset
		self.resetHomeInterface()
		

		# click on viewers
		self.reporterGui.reporterUi.employees_list_register.itemClicked.connect(self.activateEmployeeDeleteButton)

		self.reporterGui.reporterUi.employee_preview_finance.itemClicked.connect(self.activateCashoutButton)

		# load data
		self.loadEmployeeRoles()

		# load data on viewers
		self.loadEmployeeNames()

		# load basic pay
		self.loadBasicAmount()

		# load month data
		self.loadMonthDaysData()

		# load paid over pending stat
		self.loadPaidOverPendingStatistics()


		# main
		self.reporterGui.reporterUi.current_month_display.addItems(HelperUtils().getMonthsList())

		self.reporterGui.reporterUi.current_month_display.setCurrentText(HelperUtils().getPresentDateOrMonth(2))

		self.reporterGui.reporterUi.current_month_display.setEnabled(False)

		# reports
		self.reporterGui.reporterUi.report_month_list.addItems(HelperUtils().getMonthsList())

		self.reporterGui.reporterUi.report_month_list.setCurrentText(HelperUtils().getPresentDateOrMonth(2))

		self.reporterGui.reporterUi.report_year_list.addItems(HelperUtils().getYearsListOrYear(1))

		self.reporterGui.reporterUi.report_year_list.setCurrentText(HelperUtils().getYearsListOrYear(2))

		# load data
		self.updateReportViewData(changeEvent=None)


		# track item change
		self.reporterGui.reporterUi.report_month_list.currentIndexChanged.connect(self.updateReportViewData)

		self.reporterGui.reporterUi.report_year_list.currentIndexChanged.connect(self.updateReportViewData)


		self.loadRolesControlEvents()




	def startReporter(self):
		# create reporter interface instance
		self.reporterGui.show()

		# sys
		sys.exit(self.app.exec_())


# start the application
ReporterBase().startReporter()


