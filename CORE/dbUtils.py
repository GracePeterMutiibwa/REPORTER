import sqlite3

import os


class StorageUtilities:
	# get the path
	storagePath = os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'SmartSkillReporter')

	print(storagePath)

	# folder path
	databasePath = os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'SmartSkillReporter', 'store.db')


	def __init__(self):
		# checks
		self.preActionRoutines()



	def getDatabaseConnection(self):
		# get a connection to the database
		return sqlite3.connect(self.databasePath)


	def writeQueryExecutor(self, queryToExecute):
		# get connection
		connectionToUse = self.getDatabaseConnection()

		# get a cursor object
		cursorObject = connectionToUse.cursor()

		# execute
		cursorObject.execute(queryToExecute)

		# save permanently
		connectionToUse.commit()

		# close
		connectionToUse.close()

		return



	def batchFetchExecutor(self, queryToExecute):
		# get a connection
		dbConnection = self.getDatabaseConnection()

		# get cursor
		cursorObject = dbConnection.cursor()

		# execute
		cursorObject.execute(queryToExecute)

		# get the objects
		extractedRecords = cursorObject.fetchall()

		# close
		dbConnection.close()

		return extractedRecords




	def fetchSingleDataToken(self, getTag:int, extraFilters=[]):
		# map of queries with tags
		if getTag == 1:
			queryToExecute = f'SELECT * FROM employee_roles WHERE role_name="{extraFilters[0]}";'

		elif getTag == 2:
			queryToExecute = "SELECT * FROM basic_amount;"

		elif getTag == 3:
			queryToExecute = f'SELECT * FROM employee_details WHERE employee_name="{extraFilters[0]}";'

		elif getTag == 4:
			queryToExecute = f'SELECT * FROM payment_records WHERE employee_name="{extraFilters[0]}" AND month_value={extraFilters[1]} AND year_value={extraFilters[2]};'

		else:
			queryToExecute = f'SELECT employee_role FROM employee_details WHERE employee_name="{extraFilters[0]}";'



		# get a connection
		dbConnection = self.getDatabaseConnection()

		# get cursor
		cursorObject = dbConnection.cursor()

		# execute
		cursorObject.execute(queryToExecute)

		# get the object
		extractedRecord = cursorObject.fetchone()

		# close
		dbConnection.close()

		# extract the data if its there
		processedResult = extractedRecord[0] if not extractedRecord is None else None

		return processedResult



	def getEmployeeRoleAndStatus(self, employeeName:str, currentYear:int, currentMonth:int):
		# get the role
		employeeRole = self.fetchSingleDataToken(getTag=5, extraFilters=[employeeName])

		# get payment status
		wasPaid = True if self.fetchSingleDataToken(getTag=4, extraFilters=[employeeName, currentMonth, currentYear]) else False

		return employeeRole, wasPaid



	def getPresentBasicAmount(self):
		# get the basic amount
		presentAmount = self.fetchSingleDataToken(getTag=2)

		if not presentAmount is None:
			pass

		else:
			# write default basic amount
			self.writeNewBasicAmount(0)

			# write basic amount
			presentAmount = 0


		return presentAmount



	def writeNewBasicAmount(self, newBasicAmount):
		# first delete all records
		wipeQuery = "DELETE FROM basic_amount;"

		# execute
		self.writeQueryExecutor(wipeQuery)

		# write new amount
		writeQuery = f'INSERT INTO basic_amount VALUES ({newBasicAmount});'

		# update
		self.writeQueryExecutor(writeQuery)

		return



	def getDaysWorkedAndTotalForEmployee(self, employeeName, yearValue, monthValue):
		# query
		getQuery = f'SELECT * FROM payment_records WHERE employee_name="{employeeName}" AND month_value={monthValue} AND year_value={yearValue};'


		dbConnection = self.getDatabaseConnection()

		# get cursor
		cursorObject = dbConnection.cursor()

		# execute
		cursorObject.execute(getQuery)

		# get the object
		extractedRecord = cursorObject.fetchone()

		# close
		dbConnection.close()

		# get the days
		daysWorked = extractedRecord[4]

		# pay
		basicPay = extractedRecord[3]

		return daysWorked, (daysWorked * basicPay)




	def generateReportPreview(self, presentPaymentRecords):
		# report header
		reportHeader = "    NAME           DAYS WORKED          PAYMENT\n--------------------------------------------------"

		# report blocks
		reportBlocks = [reportHeader]

		if len(presentPaymentRecords) == 0:
			reportBlocks += ["", "", "", "		    NO RECORDS"]

		else:
			# format the data blocks
			for eachRecord in presentPaymentRecords:
				# get the name
				employeeName = eachRecord[0]

				# get the days
				daysWorked = eachRecord[4]

				# get the basic pay
				basicPay = eachRecord[3]

				# get amount
				accumulatedValue = daysWorked * basicPay

				# generate a record string
				recordString = f"{employeeName}           {daysWorked}            {accumulatedValue}/="

				# store it
				reportBlocks.append(recordString)

		# merge
		mergedDisplayString = "\n".join(reportBlocks)


		return mergedDisplayString



	def fetchRecordsThatMatchCriteria(self, currentMonth, currentYear):
		# query
		fetchQuery = f"SELECT * FROM payment_records WHERE month_value={currentMonth} AND year_value={currentYear};"

		# all
		availableRecords = self.batchFetchExecutor(queryToExecute=fetchQuery)

		return availableRecords


	def getReportRecords(self, currentMonth, currentYear):
		# records
		gottenRecords = self.fetchRecordsThatMatchCriteria(currentMonth=currentMonth, currentYear=currentYear)

		# formatted records
		prepareRecordsData = [

			{
				'name': eachRecord[0],
				'days': eachRecord[4],
				'payment': eachRecord[4] * eachRecord[3]

			} for eachRecord in gottenRecords
		]


		return prepareRecordsData


	def getRecentReportData(self, currentMonth, currentYear):
		# records
		gottenRecords = self.fetchRecordsThatMatchCriteria(currentMonth=currentMonth, currentYear=currentYear)


		# prepare them
		prepareRecordsData = self.generateReportPreview(presentPaymentRecords=gottenRecords)

		return prepareRecordsData




	def getCountOfAllEmployees(self):
		# all
		allEmployeesCount = len(self.batchFetchExecutor(queryToExecute="SELECT * FROM employee_details;"))

		return allEmployeesCount


	def getCountOfAlreadyPaidEmployees(self, currentMonth, currentYear):
		# query
		fetchQuery = f"SELECT * FROM payment_records WHERE month_value={currentMonth} AND year_value={currentYear};"

		# paid
		thosePaidCount = len(self.batchFetchExecutor(queryToExecute=fetchQuery))

		return thosePaidCount	



	def revokePaymentDetail(self, employeeName, currentMonth, currentYear):
		# delete the payment
		revokeQuery = f'DELETE FROM payment_records WHERE employee_name="{employeeName}" AND month_value={currentMonth} AND year_value={currentYear};'

		# execute the query
		self.writeQueryExecutor(revokeQuery)

		return


	def writeNewPaymentDetail(self, employeeName, currentMonth, currentYear, currentBasicPay, daysWorked):
		# create a query to store the data
		paymentQuery = f'INSERT INTO payment_records VALUES ("{employeeName}", {currentMonth}, {currentYear}, {currentBasicPay}, {daysWorked});'

		# make the record
		self.writeQueryExecutor(paymentQuery)

		return



	def getPresentEmployees(self):
		# get the updated records
		fetchedRecords = self.batchFetchExecutor("SELECT * FROM employee_details;")

		# get all present roles
		updatedRecords = [
						eachRoleRecord[0] for eachRoleRecord in fetchedRecords
						] if fetchedRecords else []

		return updatedRecords




	def recordNewEmployee(self, employeeName:str, employeRole:str):
		# clean name
		cleanedName = employeeName.upper()

		# check if it exists
		isDuplicate = True if self.fetchSingleDataToken(getTag=3, extraFilters=[cleanedName]) else False

		if isDuplicate is False:
			# save and proceed
			employeeSaveQuery = f'INSERT INTO employee_details VALUES ("{cleanedName}", "{employeRole}");'

			# execute
			self.writeQueryExecutor(queryToExecute=employeeSaveQuery)

		else:
			pass

		return isDuplicate

	def deleteSelectedEmployee(self, employeeName):
		# query
		deleteQuery = f'DELETE FROM employee_details WHERE employee_name="{employeeName}";'

		# debug - f tags may not be filled mistakenly
		# print(deleteQuery)

		# execute
		self.writeQueryExecutor(deleteQuery)

		return



	def getPresentRoles(self):
		# get the updated records
		fetchedRecords = self.batchFetchExecutor("SELECT * FROM employee_roles;")

		# get all present roles
		updatedRecords = [
						eachRoleRecord[0] for eachRoleRecord in fetchedRecords
						] if fetchedRecords else []

		return updatedRecords




	def deleteSelectedRole(self, roleName):
		# query
		deleteQuery = f'DELETE FROM employee_roles WHERE role_name="{roleName}";'

		# debug - f tags may not be filled mistakenly
		# print(deleteQuery)

		# execute
		self.writeQueryExecutor(deleteQuery)

		return



	def recordNewRole(self, roleName:str):
		# clean name
		cleanedName = roleName.upper()

		# check if it exists
		isDuplicate = True if self.fetchSingleDataToken(getTag=1, extraFilters=[cleanedName]) else False

		if isDuplicate is False:
			# save and proceed
			roleSaveQuery = f'INSERT INTO employee_roles  VALUES ("{cleanedName}");'

			# execute
			self.writeQueryExecutor(queryToExecute=roleSaveQuery)

		else:
			pass

		return isDuplicate 





	def initializeReporterDatabase(self):
		"""
		Create the database and its default tables
		"""
		rolesQuery = "CREATE TABLE IF NOT EXISTS employee_roles(role_name TEXT PRIMARY KEY);"

		basicAmountQuery = "CREATE TABLE IF NOT EXISTS basic_amount(daily_pay INT PRIMARY KEY);"

		employeeDetailsQuery = "CREATE TABLE IF NOT EXISTS employee_details(employee_name TEXT PRIMARY KEY, employee_role TEXT);"

		paymentRecordsQuery = "CREATE TABLE IF NOT EXISTS payment_records(employee_name TEXT PRIMARY KEY, month_value INT, year_value INT, basic_pay INT, days_worked INT);"

		with sqlite3.connect(self.databasePath) as initialConnectionHandle:
			# get a cursor
			cursorObject = initialConnectionHandle.cursor()

			# create the tables
			cursorObject.execute(rolesQuery)

			cursorObject.execute(basicAmountQuery)

			cursorObject.execute(employeeDetailsQuery)

			cursorObject.execute(paymentRecordsQuery)

			# save all changes
			initialConnectionHandle.commit()

		return


	def preActionRoutines(self):
		# folder
		if os.path.exists(self.storagePath):
			pass

		else:
			# create it
			os.mkdir(self.storagePath)


		# database
		if os.path.exists(self.databasePath):
			pass

		else:
			# create the database
			self.initializeReporterDatabase()

		return



# StorageUtilities().preActionRoutines()