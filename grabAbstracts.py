from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import parse

# Solicit user input
input_term = input("Enter your search terms: ")
base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
mydict = {'term': input_term}
url_esearch = base + "esearch.fcgi?db=pubmed&" + urlencode(mydict)
var_url_esearch = urlopen(url_esearch)
xmldoc = parse(var_url_esearch)
root = xmldoc.getroot()

xmlList = list(root.find('IdList'))
# For every element in xmlList, retrieve field .text. Then, put it in a list
idList = list(map(lambda x: x.text, xmlList))
csvList = ','.join(idList)

# Construct url for grabbing Abstracts
url_efetch = base + "efetch.fcgi?db=pubmed&" + "id=" + csvList + "&retmode=abstract&rettype=text"
print()
print("Copy paste the following url into your browser:")
print()
print(url_efetch)
print()
