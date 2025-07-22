import requests
import json
import logging
from cylogger import cylogger
#limit max 3 url requests/sec;
 
#def getSearchCounts(es_response, totalcount, idlist):    
   
#    es_data = es_response.json()
#    totalcount = es_data['esearchresult']['count']
    #count is the number of found ids from the queryterm   
#    print(f'totalcount:{totalcount}')
    
#    idlist = es_data['esearchresult']['idlist']
    #print(f"idlist:{','.join(idlist)}")

#    return [totalcount, idlist]

#    [total_id.append(id) for id in idlist]

    #用 for 迴圈，可以確定有完成es.get的時候。用while，擔心會有無限迴路出現。
#    quotient = (int(totalcount) - len(idlist))//retmax
#    remainder = (int(totalcount) - len(idlist))%retmax
#    loops = quotient if remainder == 0 else quotient + 1
 
#    print(f"more loops:{loops}")

#    if (loops == 0):
#        pass
#    else:
#        for loop in range(1, loops + 1):
#            print(f"loop:{loop}")
#            time.sleep(1.0)
#            retstart += retmax
#            esdata = esearch(retstart=f'{retstart}', retmax = f'{retmax}')
#            idlist = esdata['esearchresult']['idlist']
#            [total_id.append(id) for id in idlist]

#    if (len(total_id) != int(totalcount)):
#        print(f"WARNING: total_id:{len(total_id)} != totalcount:{totalcount}")
#    else:
        #不用擔心id是否重複，只是重複下載文件而已 
#        for pmid in total_id:
            #pmid = '34987367'
            #pmid = '38764299' 
            #pmid = '37189446'
#            time.sleep(1.0)
#            fetchoneid(pmid, subject)
       

def esearch(search_query, retstart, retmax): 
    cylogger.debug('------start esearch----------')   
    cylogger.debug(f'search_query:{search_query}')
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    eutil = 'esearch.fcgi?'
    urlstr = base_url + eutil
    #search query in db=pubmed, get idlist; 
    dbstr = 'db=pubmed'
    retmode = 'json'
     
    #retstart = '0' #retrieval start index; set default=0
    #retmax = '20' #max retrievel, default=20, don't ask more than 10,000
    rettotal = 0 #number of ids been retrieved
    total_id = [] #id list

    #usehistory = '&usehistory=y' #no space inbetween =; 
 
    #search_query = 'caffein+scalp' #input search key words
    #subject = 'chlorella'
   
    #andboolean = '+AND+' #input
    #pubdate = '2000:2025[pdat]' #in a range of 2000 to 2025
    #pubdate = '2014[pdat]'
    cylogger.debug(f'retstart={retstart}, retmax={retmax}')
    ret_range_str = '&retstart=' + retstart + '&retmax=' + retmax
  
    retmodestr = '&retmode=' + retmode
    querystr = '&term=' + search_query
   
    filter = 'ffrft[filter]' # 'ffrft[filter]' : free fulltext[filter]
  
    esearch_url = urlstr + dbstr + ret_range_str + retmodestr + querystr
   
    cylogger.debug(f'esearch_url: {esearch_url}')
    
    count = 0
    idlist = []
  
    try:
       
        #time.sleep(1.0) # make get(url) frequency less than 3/s
      
        response = requests.get(esearch_url)
        cylogger.debug(f'request get {querystr}')
        response.raise_for_status()
      
        #important info in esearch response are: counts & idlist;
    
        #esearch retrieval returns json format data
        #pubmed_es_data = response.json()
        es_data = response.json()
       
        count = es_data['esearchresult']['count']
        #count is the number of found ids from the queryterm   
        #cylogger.debug(f'es count:{count}')
    
        idlist = es_data['esearchresult']['idlist']
        #cylogger.debug(f'es idlist:{idlist}')
        #print(f"idlist:{','.join(idlist)}")
        
    except requests.exceptions.HTTPError as errh:
        cylogger.warning(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        cylogger.warning(f"Error connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        cylogger.warning(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        cylogger.warning(f"something went wrong: {err}")

    return [count, idlist]

#def fetchoneid(pmid, subject):
#    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
#    eutil = 'efetch.fcgi?'
    #fetch pmid to 'db=pubmed' to get info:
    #ArticleTitle, AbstractText, ArticleIdList
    # in ArticleIdList, get pmcid & doi(besides pmid)
    # if pmcid: article has 'free' full text in db=pmc
    # doi number: article has full text in other sources:journals, may not be free
 
#    fetch_url = base_url + eutil    
#    fetch_db = 'db=pubmed'   
    #pmid = '34987367'
    #pmid = '38764299' 
#    fetch_pmid = '&id=' + pmid
#    efetch_url = fetch_url + fetch_db + fetch_pmid

#    response = requests.get(efetch_url) 
#    response.raise_for_status()
    #print(f"{response.text}")
    # for unkown xml files:
    # first try parsing it with defusedxml
    # if ok. use xmltodict to convert it to python dictionary objct, save as json file 

#    try:  
#        root = DET.fromstring(response.content)
    
#    except DET.ParseError as err:
#        print(f"DET parse err: {err}")
#    except Exception as err:
#        print(f"exception: {err}")
    
#    else:    
#        efdic = xmltodict.parse(response.content) 
#        xmltodic_directory = f'./data/{subject}/xmltodic'
#        xmltodic_fname = f"{pmid}.json"
        
#        if not os.path.exists(xmltodic_directory):
#            os.makedirs(xmltodic_directory)

#        xmltodic_fp = os.path.join(xmltodic_directory, xmltodic_fname) 
#        try:
#            with open(xmltodic_fp, 'w') as f:
#                json.dump(efdic, f, indent=4)
#        except IOError as e:
#            print(f"An error occurred while saving the file:{e}")

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
        #article_xpath_base = './PubmedArticle/MedlineCitation/Article'
        #article_elem_list = root.findall(article_xpath_base)
        #above return all "Article" elem in a list under:PubmedArticle/MedlineCitation/"
        #in this data only one element:Article will be returned
            
#        articleDic = initArticleDic()

#        title_elem_list = root.findall('.//ArticleTitle')
        #print(f"title_elem_list length = {len(title_elem_list)}")
        
#        abstract_elem_list = root.findall('.//AbstractText')
        #print(f"abstract_elem_list length = {len(abstract_elem_list)}")
        
        #find the child_elem:ArticleTitle of article_elem
#        title_text = ''
#        for title_elem in title_elem_list:
#            title_text += ''.join(title_elem.itertext())
#        articleDic['title'] = title_text
"""
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

        articleId_list = root.findall('./PubmedArticle/PubmedData/ArticleIdList/ArticleId')
        #id_elem_list will have 1-many(list 12 IdTypes) ArticleIds returned by the findall call
        #pubmed:pmid always included
        #pmcid depends on fulltext availability in pmc
        #doi:publishers reference, usually included
        #pii:biom...

        if (len(articleId_list)) == 0 :
            print("something wrong, no ArticleId element returned")
       
        else:
    # new articleIdList:[{'type':'pubmed', 'id':'1233'}]
    #        for articleId in articleId_list:
                for key, value in articleId.items():
                # print(f"key:{key}, value:{value} of articleId attribute")
                    #type = value;
                    #id=articleId.text;
                    #articleId:{"type":{type}, "id":{id}}
                    articleDic[value] = articleId.text
              
        #if pmc id!= 'none': get fullText pdf from pmcid:      
        pmcid = articleDic.get('pmc')
        if (pmcid == 'none'):
            pass 
        else:  
            #print(f"pmcid:{pmcid}")
            ua = UserAgent()
            header = {'User-Agent':str(ua.chrome)}
            url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/'    
           
            time.sleep(0.5)
            article_pdf = requests.get(url, headers=header)

            fulltext_directory = f'./data/{subject}/fulltext'
            fulltext_fname = f"{pmcid}.pdf"
            articleDic['fullText'] = fulltext_fname
               
            if not os.path.exists(fulltext_directory):
                os.makedirs(fulltext_directory)

            fulltext_fp = os.path.join(fulltext_directory, fulltext_fname)

            try:
                with open(fulltext_fp, 'wb') as f:
                    f.write(article_pdf.content)   
            except IOError as e:
                print(f"an error occurred while saving the file:{e}")

        article_directory = f'./data/{subject}/article'
        article_fname = f"PM{pmid}.json" #use pmid; not pmcid

        if not os.path.exists(article_directory):
            os.makedirs(article_directory)

        brief_fp = os.path.join(article_directory, article_fname)

        try:
            with open(brief_fp, 'w') as f:
                json.dump(articleDic, f, indent=4)  
        except IOError as e:
            print(f"an error occurred while saving the file:{e}")

    finally:
        print(f"success fetch pmid:{pmid}")
   
def initArticleDic():
    articleDic = {} 
    # core articleDic = {
    #   'pubmed':pmid; 'pmc':pmcid, 'doi':doi, 
    #  'articleIdList':articleIdList,
    #  'authorList':authorList,
    #   'title':ttext, 'abstract':atext,'fullText':pmcid
    # } 
       
    #populate articleDic default value='none' for all keys
    articleDicKeys=['pubmed', 'pmc', 'doi', 'title', 'abstract', 'fullText']
    for key in articleDicKeys:
        articleDic[key] = 'none'
    return articleDic
"""
# pubmed.py