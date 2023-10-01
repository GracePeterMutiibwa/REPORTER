from docxtpl import DocxTemplate

import jinja2

import os

class ReportMint:
	# path to template
	pathToTemplate = "../assets/report-template.docx"

	# folder path
	desktopFolderPath = os.path.join(os.getenv("USERPROFILE"), "Desktop", "SmartSkillsReporter")

	def __init__(self):
		if os.path.exists(self.desktopFolderPath):
			pass

		else:
			# create the folder
			os.mkdir(self.desktopFolderPath)



	def openSaveFolder(self):
		# open location
		os.startfile(self.desktopFolderPath)

		return


	def generateSavePath(self, timeStamp):
		# get the report save path
		reportSavePath = os.path.join(os.getenv("USERPROFILE"), "Desktop", "SmartSkillsReporter", f"Report For {timeStamp}.docx")

		return reportSavePath


	def exportReportDetails(self, reportData:dict, reportStamp:str, monthName, yearValue):
		# create a docx template instance
		docxTemplateObject = DocxTemplate(self.pathToTemplate)

		# create a context
		createdContext = {
			'month': monthName,
			'current_year': yearValue,
			'report_data': reportData
		}

		# print(createdContext)

		# reed in the data
		docxTemplateObject.render(createdContext)


		# save the document to the desktop
		docxTemplateObject.save(self.generateSavePath(timeStamp=reportStamp))

		# open the folder
		self.openSaveFolder()

		return



# reportData = {
# 	"month": "September".upper(),
# 	"current_year": "2024",
# 	"report_data": [
# 		{
# 			"name": "Mutiibwa Grace",
# 			"days": 12,
# 			"payment": "120000"

# 		},
# 		{
# 			"name": "Mutiibwa Grace",
# 			"days": 12,
# 			"payment": "120000"

# 		}
		
# 	]
# }

# reportStamp = "Sept-2024"

# ReportMint().exportReportDetails(reportData, reportStamp)

# print("done")