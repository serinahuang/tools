from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import pandas

base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# helper functions
def extract_text(elem):
    return ''.join(elem.itertext())

# Solicit user input
input_term = input("Enter your search terms: ")
mydict = {'term': input_term}

# Construct esearch url to retrieve Pubmed IDs
url_esearch = base + "esearch.fcgi?db=pubmed&retmax=100000&" + urlencode(mydict)

# Parse esearch XML
var_url_esearch = urlopen(url_esearch)
xmldoc_esearch = parse(var_url_esearch)
root_esearch = xmldoc_esearch.getroot()
xmlList_esearch = list(root_esearch.find('IdList'))

# For every Id in xmlList, retrieve .text field then put it in a list
idList = list(map(lambda x: x.text, xmlList_esearch))
idListJoined = ','.join(idList)

# Construl efetch url to retrieve article details
url_efetch = base + "efetch.fcgi?db=pubmed&id=" + idListJoined + "&rettype=xml"

# Parse efetch XML
var_url_efetch = urlopen(url_efetch)
xmldoc_efetch = parse(var_url_efetch)
root = xmldoc_efetch.getroot()

# Add relevant details to a dataframe for export
articleList = []
colnames = ['Title', 'First Author', 'Last Author', 'Journal', 'Pub Year', 'Abstract']

for article in root.findall('./PubmedArticle/MedlineCitation'):
    #import pdb; pdb.set_trace()
    title = extract_text(article.find('.//ArticleTitle'))
    firstauth = extract_text(article.find('.//Author[1].LastName'))
    try:
        lastauth = extract_text(article.find('.//Author[last()].LastName'))
    except AttributeError:
        lastauth = extract_text(article.find('.//Author[last()-1].LastName'))
    journal = extract_text(article.find('.//Journal/ISOAbbreviation'))
    pubyear = extract_text(article.find('.//PubDate/Year'))
    abstract = extract_text(article.find('.//AbstractText'))
    article_joined = [title, firstauth, lastauth, journal, pubyear, abstract]
    articleList.append(article_joined)

df = pandas.DataFrame(articleList, columns = colnames)

# Create a Pandas Excel writer using xlsxwriter as the engine
writer = pandas.ExcelWriter('query.xlsx', engine='xlsxwriter')
#df.to_excel(writer)
writer.save()
df.to_excel('query.xlsx', index=False, encoding='utf-8')
