import csv
import xml.etree.cElementTree as ET
csvFile = '/home/drishti/2_COA_NLCO_V1_7.csv'  # Define here your CSV File Path
xmlFile = '/home/drishti/NLCO.xml'          # Define here your xml File path
csvData = csv.reader(open(csvFile))
xmlData = open(xmlFile, 'w')
for row in csvData:
        
	account_user_type = row[3] #"Asset"
        code = row[0]
        if row[5] == 'Regular':
           type1= 'other'
        else:
           type1 = row[5].lower()
	account_name= row[1]
	parent_account = row[2]
	id1 = "afras_account_" +account_name.lower().replace(" ", "_").replace(".", "_")
	parent_id = "afras_account_" +parent_account.lower().replace(" ", "_").replace(".", "_")
	user_type = "afras_account_type_" + account_user_type.lower().replace(" ","_")
	
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
   
	tree.write(xmlData)
	xmlData.write("\n")
