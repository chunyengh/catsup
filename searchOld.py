from flask import Flask
from flask import request
from flask import jsonify, abort
from cylogger import cylogger
from go_pubmed_search import esearch
from go_pubmed_fetch import fetchoneid
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello_world():
    cylogger.info("hello_world")
    return jsonify('<p>Hello, My catseye Flask World!</p>')
   
@app.route('/search', methods=['POST'])
def receive_search_term_in_json():
    cylogger.info("enter /search -----------")
    cylogger.info(f"request:{request.data}")
    #logger.info(f'request.content_length = {request.content_length}')

    # request body from front end fetch func:
    # when body='' | body not included, we get: 
    # request.content_length=0 and
    # request.data = '' empty
   
    #if request.content_length and request.content_length > 1024 * 1024:
    #    logger.debug('request body is None or too large')
        # return needs to include str, code; str message doesn't go to front end browser
        #if return str only => front end no response(even inside exception block)
        #if return code only => front end shows 500 server error
    #    return 'content is None or too big', 413

    # data = request.get_json(silent=True)
    # if data is None:
    #    logger.debug("AHHHHHHHHHHH")
   
    # None by flask means request is "invalid" json data
    # if silent is True; program needs to take care of None
    # else (i.e default=False), None goes to Exception
    #loopIndex;
    #init:retstart=0(loopIndex=0);
    # if loops > 0;  
    #retstart=loopIndex*retmax;
    retstart = 0
    retmax = 20
    testresult = {
        "loops":"0",
        "loopIndex":"0",
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
    cylogger.info(f"testresult:{testresult}")
    #return jsonify({"ok":"data receive success"})
    return jsonify(testresult), 200

    try:
        request_query = request.get_json()
        cylogger.info(f"request_query: {request_query}")
        loop_index = request_query['loopIndex']
        search_query = request_query['sq']
        cylogger.info(f'loop_index:{loop_index}')
        cylogger.info(f'search_query:{search_query}')
        cylogger.info("search_query successful")
        #continue data request
        #do pubmed e-search: get counts(match search_query) and pmidlist of the counts
        #we set max retrieval count=20 for each e-search
        #if match > retrieval; return 20 idlist 
        retstart = int(loop_index) * retmax
        [counts, idlist] = esearch(search_query, retstart=f'{retstart}', retmax=f'{retmax}')
      
        cylogger.info(f'counts={counts}')
        cylogger.info(f'idlist={str(idlist)}')
       
#    [total_id.append(id) for id in idlist]

    #用 for 迴圈，可以確定有完成es.get的時候。用while，擔心會有無限迴路出現。
        quotient = (int(counts) - len(idlist))//retmax
        remainder = (int(counts) - len(idlist))%retmax
        loops = quotient if remainder == 0 else quotient + 1
        cylogger.info(f"loops:{loops}")

        #fetch articles@idlist from pubmed
        
        #try subject = date
        date = datetime.now()
        subject = date.strftime("%Y%m%d")
        total_article_dic={} #{id#, ind_article_dic=article_dic}
      
        #for id in idlist:
        
        article_dic = fetchoneid(idlist[0], subject={subject})
        total_article_dic[f'{idlist[0]}'] = article_dic
     
        cylogger.info(f"total_article_dic:{total_article_dic}")
       
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
            "loops":f"{loops}",
            "loopIndex": loop_index, 
            "result":f"{total_article_dic}"
        }
        #cylogger.info(f"es_result:{es_result}")
        es_result_str = jsonify(es_result)
      
        #return jsonify({"ok":"data receive success"})
        cylogger.info(f"es_result_str:{es_result_str}")
        #return jsonify({"result":f"{es_result}"}), 200
        return es_result, 200
    except Exception as e:
        cylogger.debug(f"search exception parsing error {e}")
        return jsonify({"exception":f"{e}"}), 400

#if __name__ == '__main__':
#    app.run(debug=True)