import requests
import json
from xml.etree import ElementTree as ET
from defusedxml import ElementTree as DET
# defusedxml strengthens xml against maliciously constructed data,
# doesn't replace xml all; if any func is needed, still get it from xml(import)
# python document suggests using defusedxml other than xml for more secure in parsing

from fake_useragent import UserAgent
import time
import xmltodict

import os
from cylogger import cylogger

def fetchoneid(pmid, subject):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    eutil = 'efetch.fcgi?'
    #fetch pmid to 'db=pubmed' to get info:
    #ArticleTitle, AbstractText, ArticleIdList
    # in ArticleIdList, get pmcid & doi(besides pmid)
    # if pmcid: article has 'free' full text in db=pmc
    # doi number: article has full text in other sources:journals, may not be free
 
    fetch_url = base_url + eutil    
    fetch_db = 'db=pubmed'   
    #pmid = '34987367'
    #pmid = '38764299' 
    fetch_pmid = '&id=' + pmid
    efetch_url = fetch_url + fetch_db + fetch_pmid

    response = requests.get(efetch_url) 
    response.raise_for_status()
    #print(f"{response.text}")
    # for unkown xml files:
    # first try parsing it with defusedxml
    # if ok. use xmltodict to convert it to python dictionary objct, save as json file 

    try:  
        root = DET.fromstring(response.content)
    
    except DET.ParseError as err:
        cylogger.debug(f"DET parse err: {err}")
    except Exception as err:
        cylogger.debug(f"exception: {err}")
    
    else:        
        efdic = xmltodict.parse(response.content) 
        #xmltodic_directory = f'./data/{subject}/xmltodic'
        #xmltodic_fname = f"{pmid}.json"
        
        #if not os.path.exists(xmltodic_directory):
        #    os.makedirs(xmltodic_directory)

        #xmltodic_fp = os.path.join(xmltodic_directory, xmltodic_fname) 
        #try:
        #    with open(xmltodic_fp, 'w') as f:
        #        json.dump(efdic, f, indent=4)
        #except IOError as e:
        #    print(f"An error occurred while saving the file:{e}")

        #get always:ArticleTitle & ArticleAbstract
        #<PubmedArticleSet><PubmedArticle><MedlineCitation>
        #<Article><ArticleTitle>titletext</ArticleTitle>
        #<Article><Abstract><AbstractText>abstracttext</AbstractText> 
        # some case:<AbstractText> 1stpart...<i>n</n> 2ndpart...</AbstractText> 
        # or <AbstractText Label='a'>1st</AbstractText> 
        # <AbstractText Label='b'>2nd</AbstractText>...
        # if use AbstractText.text => only get 1stpart; stopped by <i> and not continue to 2nd Label
        # to get 1st&2nd, ignore inner tag <i> or to continue with other Labels;
        # use Abstract.itertext(): str = ''.join(AbstractText.itertext()) => 1st + 2nd
        #from root get pmcid to fetch full text articles
        #ArticleIdList shows up not only in article, but also in reference
        #if we use root.iter('ArticleIdList'), will go through all ArticleIdLists(self & references articles)
        #if use element.findall(tag), get children only; takes many steps to go from root to 'ArticleIdList'
        #the one we are interested in getting is in the path:
        #<PubmedArticleSet><PubmedArticle><PubmedData><ArticleIdList>
        # <ArticleId IdType:'pubmed'>'34987367' </ArticleId>  
        # <ArticleId IdType:'pmc'>'PMC8722672' </ArticleId>
        # <ArticleId IdType:'doi'>"10.3389/fnhum.2021.744054"</ArticleId>
        # Idtype is ArticleId's attrib_key = attrib_dict_key, 
        # 'pubmed' is ArticleId's attrib_value = attrib_dict_value,
        # '34987367' is ArticleId.text
          #<PubmedArticleSet><PubmedArticle><MedlineCitation>
        #<Article><Journal><Title>journalTitleText</Title>
        #<Article><Journal><JournalIssue><Volume>volumeText</Volume>
        #<Article><Journal><JournalIssue><PubDate><Year>yearText</Year>
        #<Article><AuthorList><Author>[
        # {"LastName":"ln", "ForeName":"fn", "Initials":"in"}
        #]
        #xpath usage: root.findall(xpath); not root.find(xpath)
        #root:= PubmedArticleSet 
        # if use like: root.findall('.//article)
        #    will return all article elem in a list under PubmedArticleSet   
        #if use like: article_xpath_base = './PubmedArticle/MedlineCitation/Article'
        #             article_elem_list = root.findall(article_xpath_base)
        #   then the return will be all "Article" elem in a list 
        #   under:PubmedArticle/MedlineCitation/"
        #in this data only one element:Article will be returned
            
              
        #articleDic = initArticleDic()
        articleDic = {}
        title_elem_list = root.findall('.//ArticleTitle')
        #print(f"title_elem_list length = {len(title_elem_list)}")
        
        abstract_elem_list = root.findall('.//AbstractText')
        #print(f"abstract_elem_list length = {len(abstract_elem_list)}")
        
        #find the child_elem:ArticleTitle of article_elem
        title_text = ''
        for title_elem in title_elem_list:
            title_text += ''.join(title_elem.itertext())
        articleDic['title'] = title_text
        
        abstract_text = ''
        for abstract_elem in abstract_elem_list:
            if (abstract_elem.items() == 0):
                abstract_text += ''.join(abstract_elem.itertext())
            else:
                elem_attr_value_list = []
                for key, value in abstract_elem.items():#has two attris:label & nlmcategory
                    if value in elem_attr_value_list:
                        pass
                    else:
                        elem_attr_value_list.append(value)
                
                elem_attr_text = ' '.join(elem_attr_value_list)
                attr_prespace = '' if abstract_text == '' else ' '
                abstract_text += attr_prespace + elem_attr_text + ' ' + ''.join(abstract_elem.itertext())
                #print(f"aat:{article_abstract_text}")

        articleDic['abstract'] = abstract_text

        journal_issue_title_list = root.findall('./PubmedArticle/MedlineCitation/Article/Journal/Title')
        for journal_issue_title in journal_issue_title_list:
           # cylogger.info(f'tag:{journal_issue_title.tag}, text:{journal_issue_title.text}')
            articleDic['journalIssueTitle'] = journal_issue_title.text
        
        journal_issue_volume_list = root.findall('./PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/Volume')
        for journal_issue_volume in journal_issue_volume_list:
            # cylogger.info(f'tag:{journal_issue_volume.tag}, text:{journal_issue_volume.text}')
            articleDic['journalIssueVolume'] = journal_issue_volume.text
        
        # working example:
        # journal_issue_pubdate_list = root.findall('./PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate')
        # for journal_issue_pubdate in journal_issue_pubdate_list:
        #    for child in journal_issue_pubdate:
        #        cylogger.info(f'child tag:{child.tag}, child text:{child.text}')

        journal_issue_pubdateyear_list = root.findall('./PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
        for journal_issue_pubdateyear in journal_issue_pubdateyear_list:
            #cylogger.info(f'tag:{journal_issue_pubdateyear.tag}, text:{journal_issue_pubdateyear.text}')
            articleDic['journalIssuePubDateYear'] = journal_issue_pubdateyear.text

        author_list = root.findall('./PubmedArticle/MedlineCitation/Article/AuthorList/Author')
        #authorDicList=[{LastName:ln, Initials:in}]
        authorDicList = []
        for author in author_list:
            authorDic = {}
            for childauthor in author:
                #cylogger.info(f'childauthor:{childauthor}')
                #cylogger.info(f'childauthor tag:{childauthor.tag}, childauthor text:{childauthor.text}')
                if (childauthor.tag == 'LastName'):
                    #cylogger.info(f'lastname:{childauthor.text}')
                    authorDic['LastName'] = childauthor.text
                elif (childauthor.tag == 'Initials'):
                    #cylogger.info(f'initials:{childauthor.text}')
                    authorDic['Initials'] = childauthor.text
         
            authorDicList.append(authorDic)    
        articleDic['authorList'] = authorDicList
        
        articleId_list = root.findall('./PubmedArticle/PubmedData/ArticleIdList/ArticleId')
        #id_elem_list will have 1-many(list 12 IdTypes) ArticleIds returned by the findall call
        #pubmed:pmid always included
        #pmcid depends on fulltext availability in pmc
        #doi:publishers reference, usually included
        #pii:biom...
       
        articleIdDicList = []
        #[{'type':'pubmed', 'id':'123'},{'type':'pmc', 'id':'345'},{'type';'doi', 'id':'js/01'}]
        for articleId in articleId_list:
            articleIdDic = {}
            for key, value in articleId.items():
            # print(f"key:{key}, value:{value} of articleId attribute, etc.attribute:"IdType")
                articleIdDic['type']= value
                articleIdDic['id']= articleId.text
                #cylogger.info(f'articleIdDic:{articleIdDic}')
            articleIdDicList.append(articleIdDic)
            #cylogger.info(f'articleIdDicList:{articleIdDicList}')
        articleDic['articleIdList'] = articleIdDicList

        return articleDic 
         
        #if pmc id!= 'none': get fullText pdf from pmcid:      
        #pmcid = articleDic.get('pmc')
        #if (pmcid == 'none'):
        #    pass 
        #else:  
            #print(f"pmcid:{pmcid}")
        #    ua = UserAgent()
        #    header = {'User-Agent':str(ua.chrome)}
        #    url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/'    
           
        #    time.sleep(0.5)
        #    article_pdf = requests.get(url, headers=header)

        #    fulltext_directory = f'./data/{subject}/fulltext'
        #    fulltext_fname = f"{pmcid}.pdf"
        #    articleDic['fullText'] = fulltext_fname
               
        #    if not os.path.exists(fulltext_directory):
        #        os.makedirs(fulltext_directory)

        #    fulltext_fp = os.path.join(fulltext_directory, fulltext_fname)

        #    try:
        #        with open(fulltext_fp, 'wb') as f:
        #            f.write(article_pdf.content)   
        #    except IOError as e:
        #        print(f"an error occurred while saving the file:{e}")

        #article_directory = f'./data/{subject}/article'
        #article_fname = f"PM{pmid}.json" #use pmid; not pmcid

        #if not os.path.exists(article_directory):
        #    os.makedirs(article_directory)

        #brief_fp = os.path.join(article_directory, article_fname)

        #try:
           # with open(brief_fp, 'w') as f:
           #     json.dump(articleDic, f, indent=4)  
        #except IOError as e:
           # print(f"an error occurred while saving the file:{e}")

    #finally:
        #print(f"success fetch pmid:{pmid}")
    
#def initArticleDic():
#    articleDic = {} 
    # core articleDic = {
    #   'pubmed':pmid; 'pmc':pmcid, 'doi':doi, 
    #   'title':ttext, 'abstract':atext,'fullText':pmcid
    # } 
       
    #populate articleDic default value='none' for all keys
#    articleDicKeys=['pubmed', 'pmc', 'doi', 'title', 'abstract', 'fullText']
#    for key in articleDicKeys:
 #       articleDic[key] = 'none'
#    return articleDic
    
# pubmed.py