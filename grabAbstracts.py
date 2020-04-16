from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import pandas

# Solicit user input
input_term = input("Enter your search terms: ")
base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
mydict = {'term': input_term}

# Construct esearch url to retrieve Pubmed IDs
url_esearch = base + "esearch.fcgi?db=pubmed&" + urlencode(mydict)

# Parse esearch XML
var_url_esearch = urlopen(url_esearch)
xmldoc_esearch = parse(var_url_esearch)
root_esearch = xmldoc_esearch.getroot()
xmlList_esearch = list(root_esearch.find('IdList'))

# For every Id in xmlList, retrieve .text field then put it in a list
idList = list(map(lambda x: x.text, xmlList_esearch))
idListJoined = ','.join(idList)

# Construl efetch url to retrieve article details
url_efetch_xml = base + "efetch.fcgi?db=pubmed&id=" + idListJoined + "&rettype=xml"

# Parse efetch XML
var_url_efetch_xml = urlopen(url_efetch_xml)
xmldoc_efetch = parse(var_url_efetch_xml)
root = xmldoc_efetch.getroot()

# Add relevant details to a dataframe for export
articleList = []
colnames = ['Title', 'First Author', 'Last Author', 'Journal', 'Pub Year', 'Abstract']

for article in root.findall('./PubmedArticle/MedlineCitation'):
    title = article.find('.//ArticleTitle').text
    firstauth = article.find('.//Author[1].LastName').text
    lastauth = article.find('.//Author[last()].LastName').text
    journal = article.find('.//Journal/ISOAbbreviation').text
    pubyear = article.find('.//PubDate/Year').text
    abstract = article.find('.//AbstractText').text
    article_joined = [title, firstauth, lastauth, journal, pubyear, abstract]
    articleList.append(article_joined)

df = pandas.DataFrame(articleList, columns = colnames)
df.to_csv('query.csv', index=False)

