from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import pandas

base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
colnames = ['Title', 'First Author', 'Last Author', 'Journal', 'Pub Year', 'Abstract']


# helper functions
def extract_text(elem):
    if elem is None:
        return ''
    else:
        return ''.join(elem.itertext())

def divide_chunks(l, n):
    # l: the list to split up
    # n: size of the resulting chunks
    for i in range(0, len(l), n):
        yield l[i:i + n]

def build_list(root):
    for article in root.findall('./PubmedArticle/MedlineCitation'):
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

# Solicit user input
input_term = input("Enter your search terms: ")
input_filename = input("Enter desired file name: ")
mydict = {'term': input_term}
filename = input_filename + '.xlsx'

# Construct esearch url to retrieve Pubmed IDs
url_esearch = base + "esearch.fcgi?db=pubmed&retmax=100000&" + urlencode(mydict)

# Parse esearch XML
var_url_esearch = urlopen(url_esearch)
xmldoc_esearch = parse(var_url_esearch)
root_esearch = xmldoc_esearch.getroot()
xmlList_esearch = list(root_esearch.find('IdList'))

# For every Id in xmlList, retrieve .text field then put it in a list
idList = list(map(lambda x: x.text, xmlList_esearch))

print('fetching ' + str(len(idList)) + ' results... please be patient.')

idListChunks = divide_chunks(idList, 400)
idListJoinedChunks = list(map(lambda x: ','.join(x), idListChunks))

# Add relevant details to a dataframe for export
articleList = []

for chunk in idListJoinedChunks:
    print('.')
    # Construct efetch url to retrieve article details
    url_efetch = base + "efetch.fcgi?db=pubmed&id=" + chunk + "&rettype=xml"
    # Parse efetch XML
    var_url_efetch = urlopen(url_efetch)
    xmldoc_efetch = parse(var_url_efetch)
    root = xmldoc_efetch.getroot()
    # Construct list containing article and details
    build_list(root)

df = pandas.DataFrame(articleList, columns = colnames)

print('\ndone!')

# Create a Pandas Excel writer using xlsxwriter as the engine
writer = pandas.ExcelWriter(filename, engine='xlsxwriter')
writer.save()
df.to_excel(filename, index=False, encoding='utf-8')
