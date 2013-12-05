import csv
import xml.etree.cElementTree as ET
#csvFile = '/home/drishti/ERP/account.csv'  # Define here your CSV File Path
xmlFile = '/home/drishti/ERP/NLCO1.xml'          # Define here your xml File path
#csvData = csv.reader(open(csvFile))
account_type_dict = {  'Revenue View' : 'account_type_income_view1',
                       'Expense View' : 'account_type_expense_view1',
                       'Asset View' : 'account_type_asset_view1',
                       'Liability View' : 'account_type_liability_view1',
                       'Tax' :  'conf_account_type_tax',
                       'Equity' : 'conf_account_type_equity',
                       'Check' : 'conf_account_type_chk',
                       'Root/View' : 'data_account_type_view',
                       'Receivable' : 'data_account_type_receivable',
                       'Payable'  :  'data_account_type_payable',
                       'Bank' : 'data_account_type_bank',
                       'Cash' : 'data_account_type_cash',
                       'Asset' : 'data_account_type_asset',
                       'Liability' : 'data_account_type_liability',
                       'Revenue' : 'data_account_type_income',
                       'Expense' : 'data_account_type_expense',
                        'Receivable View' : 'data_account_type_receivable_view1',
                        'Payable View'  :  'data_account_type_payable_view1',
                       # '' : 'data_account_type_revenue_view',
                         '' : 'data_account_type_revenue',
                     }
xmlData = open(xmlFile, 'w')
import xlrd
workbook = xlrd.open_workbook('/home/drishti/ERP/nlco_coa.xls')
worksheets = workbook.sheet_names()
for worksheet_name in worksheets:
	worksheet = workbook.sheet_by_name(worksheet_name)
        num_rows = worksheet.nrows - 1
        num_cells = 3 #worksheet.ncols - 1
        curr_row = 0
	while curr_row < num_rows:
		        curr_row += 1
		        row = worksheet.row(curr_row)
		
			# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
			#cell_type = worksheet.cell_type(curr_row, curr_cell)
			cell_value = worksheet.cell_value(curr_row, 0)
                        code = str(worksheet.cell_value(curr_row, 0))
        		account_name= worksheet.cell_value(curr_row, 1)
        		parent_account = str(worksheet.cell_value(curr_row, 2))
                        if worksheet.cell_value(curr_row, 3)== 'Regular':
           			type1= 'other'
        		else:
           			type1 = worksheet.cell_value(curr_row, 3).lower()
			user_type = account_type_dict[worksheet.cell_value(curr_row, 4)] #"Asset"
                       
                        id1 = "afras_account_" +code.replace(",", "")
			parent_id = "afras_account_" +parent_account.replace(",", "")
			#user_type = "afras_account_type_" + account_user_type.lower().replace(" ","_")
	
			doc = ET.Element("record")
			doc.set("id", id1)
			doc.set("model", "account.account")
			field1 = ET.SubElement(doc, "field")
			field1.set("name", "name")
			field1.text = account_name
			field2 = ET.SubElement(doc, "field")
			field2.set("name", "code")
			field2.text = code
			field3 = ET.SubElement(doc, "field")
			field3.set("name", "type")
			field3.text = type1
			if parent_account:
			    field4 = ET.SubElement(doc, "field")
			    field4.set("name", "parent_id")
			    field4.set("ref", parent_id)
			field5 = ET.SubElement(doc, "field")
			field5.set("name", "user_type")
			field5.set("ref", user_type)
			tree = ET.ElementTree(doc)
			print "code",code
			print "tree",tree
		   
			tree.write(xmlData)
			xmlData.write("\n")
				       



