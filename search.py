from flask import Flask
from flask import request
from flask import jsonify, abort
from cylogger import cylogger
from go_pubmed_search import esearch
from go_pubmed_fetch import fetchoneid
from datetime import datetime
import os
import json
from fake_useragent import UserAgent
import time
import requests
import xmltodict
from xml.etree import ElementTree as ET
from defusedxml import ElementTree as DET

app = Flask(__name__)

@app.route('/')
def hello_world():
    cylogger.info("hello_world")
    return jsonify('<p>Hello, My catseye Flask World!</p>')
   
@app.route('/search', methods=['POST'])
def receive_search_term_in_json():
    #cylogger.info("enter /search -----------")  
    retstart = 0
    retmax = 2
    
    #""" 
    testresult = {
        #"startArticleIndex":"0",
        "searchquery":"sq",
        #"loops":"0",
        #"loopIndex":"0",
        "counts":"5",
        "articleList":[   
            {
                "articleIdList":[
                    {"type":"pubmed",
                     "id":"23733102",
                    },
                    {"type":"doi",
                     "id":"10.1016/j.fct.2013.05.035",
                    },
                    {"type":"pii",
                     "id":"S0278-6915(13)00341-4",
                    },
                ],   
                "journalIssueTitle":"Food and chemical toxi",
                "journalIssueVolume":"59",
                "journalIssuePubDateYear":"2013",
                "title":"paper title",
                "abstract":"paper abstract",
                "authorList":[
                    {"LastName":"Szabo",
                     "Initials":"NJ",
                    },
                    {"LastName":"Matulka",
                     "Initials":"RA",
                    },
                    {"LastName":"Chan",
                     "Initials":"T",
                    }
                ],
            },
            {
                "articleIdList":[
                    {"type":"pubmed",
                     "id":"66666666",
                    },
                    {"type":"doi",
                     "id":"10.1016/j.fct.2013.05.035",
                    },
                    {"type":"pii",
                     "id":"S0278-6915(13)00341-4",
                    },
                ],   
                "journalIssueTitle":"Physics and chemistry",
                "journalIssueVolume":"59",
                "journalIssuePubDateYear":"2000",
                "title":"paper title",
                "abstract":"paper abstract",
                "authorList":[
                    {"LastName":"Chen",
                     "Initials":"NJ",
                    },
                    {"LastName":"Zhou",
                     "Initials":"RA",
                    },
                    {"LastName":"Lin",
                     "Initials":"T",
                    }
                ],
            }
        ]
    }
    #cylogger.info(f"testresult:{testresult}")
    #return jsonify({"ok":"data receive success"})
    return jsonify(testresult), 200
    
    try:
        request_query = request.get_json()
        cylogger.info(f"request_query: {request_query}")

        startArticleIndex = request_query['startArticleIndex'] 
        search_query = request_query['sq']
    
        #do pubmed e-search: get counts(match search_query) and pmidlist of the counts
        #we set max retrieval count=20 for each e-search
        #if match > retrieval; return 20 idlist 
    
        retstart = startArticleIndex
         
        [counts, idlist] = esearch(search_query, retstart=f'{retstart}', retmax=f'{retmax}')
      
        #cylogger.info(f'counts={counts}')
        #cylogger.info(f'idlist={str(idlist)}')
       
        #fetch articles@idlist from pubmed
        
        #try subject = date
        #date = datetime.now()
        #subject = date.strftime("%Y%m%d")
        article_list= [] #[articleIndex]
      
        for id in idlist:
            article_dic = fetchoneid(id)
            cylogger.info(f'article_dic = {article_dic}')
            article_list.append(article_dic)
     
        #cylogger.info(f"total_article_list:{total_article_list}")
       
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

       
        es_result = {
            "searchquery": search_query,
            "counts": counts, 
            "articleList":article_list
        }  
        return jsonify(es_result), 200
    except Exception as e:   
        return jsonify({"exception":f"{e}"}), 400


@app.route('/download', methods=['POST'])
def download():
    cylogger.info("enter /download -----------")
    #cylogger.info(f"request:{request.data}")
    try:
        #return jsonify({"ok":"to download"})
        request_query = request.get_json()
        cylogger.info(f"download request_query: {request_query}")
        subject = request_query['sq']
        articleIndexTestInfoObjList = request_query['data']
     
        for articleIndexTestInfoObj in articleIndexTestInfoObjList:
            articleIndex = articleIndexTestInfoObj['articleIndex']
            testInfoObj = articleIndexTestInfoObj['selectedTestInfoObj']
            
            date = datetime.now()
            dax = date.strftime("%Y%m%d")
       
            data_directory = f'./data/{subject}/all'
            data_fname = f"{dax}_{articleIndex}.json"
        
            if not os.path.exists(data_directory):
                os.makedirs(data_directory)

            data_fp = os.path.join(data_directory, data_fname) 
            try:
                with open(data_fp, 'w') as f:
                    json.dump(articleIndexTestInfoObjList, f, indent=4)
                #return jsonify({"ok":"data download success"})
            except IOError as e:
                cylogger.warning(f"An error occurred while saving the file:{e}")
        
            articleIdObjList = testInfoObj['articleIdObjArray']
            for articleIdObj in articleIdObjList:
                #if (articleIdObj['type'] != 'pmc'):
                #    pass
                #else:
                    #pmcid = articleIdObj['id']
                    ua = UserAgent()
                    header = {'User-Agent':str(ua.chrome)}
                    #url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/'  
                    url =f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC5334499'
                    time.sleep(0.5)
                    #article_pdf = requests.get(url, headers=header, stream=True)
                    article_oa = requests.get(url, headers=header)
                    cylogger.info(f'---------i am here-----------')
                    #article_oa_dic = xmltodict.parse(article_oa.content)
                    try:  
                        root = DET.fromstring(article_oa.content)
    
                    except DET.ParseError as err:
                        cylogger.debug(f"DET parse err: {err}")
                    except Exception as err:
                        cylogger.debug(f"exception: {err}")
    
                    else:        
                        link_list = root.findall('.//link')
                        #link_list:[[{key:format, value:pdf}, {key:href, value:'ftp://ftp...'}]]
                        for link in link_list:
                            for key, value in link.items():
                                if (key === 'format')
                            cylogger.info(f'link:{link}')
                        cylogger.info(f'record_list:{link_list}')
                        #cylogger.info(f'article_oa:{article_oa_dic}')
                        fulltext_directory = f'./data/{subject}/fulltext'
                        #fulltext_fname = f"{dax}_{articleIndex}.pdf"
                        fulltext_fname = f"{dax}_{articleIndex}.json"
                        #if not os.path.exists(fulltext_directory):
                        #    os.makedirs(fulltext_directory)

                        #fulltext_fp = os.path.join(fulltext_directory, fulltext_fname)
                        """
                        try:
                            with open(fulltext_fp, 'w') as f:
                            #f.write(article_pdf.content)  
                                json.dump(article_oa_dic, f, indent=4)
                        except IOError as e:
                            cylogger.warning(f"An error occurred while saving the file:{e}")
                        """
        return jsonify({"ok":"data download success"})    
                
    except Exception as e:
        return jsonify({"exception":f"{e}"}), 400


#if __name__ == '__main__':
#    app.run(debug=True)