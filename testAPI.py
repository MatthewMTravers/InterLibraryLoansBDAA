import requests
import xml.etree.ElementTree as ET

# Worldcat API  - https://developer.api.oclc.org/wcv1#/
# MARC21 format - https://www.loc.gov/marc/bibliographic/

APIKEY = "VwdNr2kjw0YPqIPDeY1tJU3cHMpQWQN5amDAwCijQlwE3W7Np9ETk3knq0cSag63GxlaBBBtjvFmPcEI"

def getByISBN(isbn):
	url = f"https://worldcat.org/webservices/catalog/content/isbn/{isbn}?wskey={APIKEY}"
	response = requests.get(url)
	return response.content.decode()

def getByISSN(issn):
	url = f"https://worldcat.org/webservices/catalog/content/issn/{issn}?wskey={APIKEY}"
	response = requests.get(url)
	return response.content.decode()


isbn = "9042908998"
issn = "1079-0713"

content = getByISBN(isbn)
parsed = ET.fromstring(content)

toStrip = ",./© "

for child in parsed:
	tag = child.get("tag")
	ind1 = child.get("ind1")
	ind2 = child.get("ind2")

	# tag = 245: title statement
	if tag == "245":
		titleA = ""
		titleB = ""
		for grandchild in child:
			code = grandchild.get("code")
			
			if code == "a": 
				titleA = grandchild.text
			elif code == "b": 
				titleB = grandchild.text

		title = (titleA + " " + titleB).strip(toStrip)
		print(f"Title: {title}")

	# tag = 260: Publication, Distribution, etc. (Imprint) (R)
	# tag = 264: Production, Publication, Distribution, Manufacture, and Copyright Notice (R) ; ind2 = 1: Publication
	elif (tag == "260") or (tag == "264" and ind2 == "1"):
		publisher = ""
		publicationYear = ""
		for grandchild in child:
			code = grandchild.get("code")
			
			if code == "b":
				publisher = grandchild.text.strip(toStrip)
			elif code == "c":
				publicationYear = grandchild.text.strip(toStrip)
	
		print(f"Publisher: {publisher} ({publicationYear})")
