#!/usr/bin/env python
# coding: utf8

import sys


from flask import Flask
# from flask import request
import json
from flask_cors import CORS,cross_origin
import configparser
from loggingmodule import getlogger
from flask import json
from flask.json import jsonify
from flask.globals import request
import semantic
####################### Confi file reading
config_file_loc = "../config/config.cfg"

config_obj = configparser.ConfigParser()

try:    
    config_obj.read(config_file_loc)
    debugLevel = int(config_obj.get("REST","debuglevel"))
    logfilename = config_obj.get("REST","logfilename")
    ip = str(config_obj.get("REST", "ip"))
    port = int(config_obj.get("REST", "port"))
except Exception as e:
    raise Exception("Config file reading error: "+str(e))

logfilename="../logs/"+logfilename
logfilename_temp = "../logs/"+"SEMANTIC_REQ_RES.log"

####################### Loggin Functionality
loggerobj = getlogger.GetLogger("Semantic_Rest",logfilename,debugLevel)
logger = loggerobj.getlogger1()

loggerobj_req_res = getlogger.GetLogger("Semantic_Rest_REQ_RES",logfilename_temp,debugLevel)
loggerobj_req_res = loggerobj_req_res.getlogger1()
###################### Flask Initialization
app = Flask(__name__)
CORS(app)

##################### Initializing all the objects

try:
    semanticobj=semantic.Semantic()
    print ("Successfully initialized Semantic")
except Exception as e:
    semanticobj=None
    raise Exception("Unsuccessfully initialized Semantic Reason: "+str(e))

response = {
        "company": [],
        "edu_level": [],
        "edu_stream": [],
        "experience": [],
        "ind": [],
        "loc": [],
        "o": [],
        "recommendations": [],
        "role": [],
        "skill": []
    }
logger.info("Sematic Search REST API Started")

@app.route('/getSemantic', methods=['POST'])
@cross_origin()
def getSemantic():
    logger.info("getSemantic called")
    if request.method!='POST':
        logger.error("getSemantic: Only accept POST request")
        return json.dumps({"Status":"ERROR","DATA":response,"Reason":"Only accept POST request"})
    if not request.headers['Content-Type'] == 'application/json':
        logger.error("getSemantic: Only  accept Content-Type:application/json")
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": "Only  accept Content-Type:application/json"})
    if not request.is_json :
        logger.error('getSemantic: Content_Type should be applicatin/json,Expecting json data in the form {"data":"VALUE","numTerms":VALUE,"tokens_only":BOOLVALUE}')
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": 'Expecting json data in the form {"data":"VALUE","numTerms":VALUE,"tokens_only":BOOLVALUE}'})
    data=request.json

    if 'data' not in data :
        logger.error("getSemantic: Expecting key as data,numTerms,tokens_only")
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": 'Expecting key as data,numTerms,tokens_only'})
    logger.info("getSemantic: got json as = " + str(data))
    try:
        word=data['data']
        numTerms = 2
    except Exception as e:
        logger.error("getSemantic: Failed to parse the key and value from the data")
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": 'Failed to parse: "data" should be str, "numTerms" should be int, "tokens_only" should be bool'})

    logger.info("getSemantic: data = " + str(word))
    try:
        if semanticobj!=None:
            semanticwords = semanticobj.semanticJobSearch(word,numTerms)
        else:
            semanticwords=[]
        logger.info("getSemantic: related terms are = " + str(semanticwords))
    except Exception as e:
        logger.error("getSemantic: 'Internal server error'")
        return jsonify({"Status": "ERROR", "DATA": response, "Reason": "Internal server error"})
    loggerobj_req_res.info(str(word)+" = "+str(semanticwords))
    return jsonify({"Status": "SUCCESS", "DATA":semanticwords, "Reason": ""})


@app.route('/getSemanticResumeSearch', methods=['POST'])
@cross_origin()
def getSemanticResumeSearch():
    logger.info("getSemantic called")
    if request.method!='POST':
        logger.error("getSemantic: Only accept POST request")
        return json.dumps({"Status":"ERROR","DATA":response,"Reason":"Only accept POST request"})
    if not request.headers['Content-Type'] == 'application/json':
        logger.error("getSemantic: Only  accept Content-Type:application/json")
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": "Only  accept Content-Type:application/json"})
    if not request.is_json :
        logger.error('getSemantic: Content_Type should be applicatin/json,Expecting json data in the form {"data":"VALUE","numTerms":VALUE,"tokens_only":BOOLVALUE}')
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": 'Expecting json data in the form {"data":"VALUE","numTerms":VALUE,"tokens_only":BOOLVALUE}'})
    data=request.json

    if 'data' not in data :
        logger.error("getSemantic: Expecting key as data,numTerms,tokens_only")
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": 'Expecting key as data,numTerms,tokens_only'})
    logger.info("getSemantic: got json as = " + str(data))
    try:
        word=data['data']
        numTerms=2
    except Exception as e:
        logger.error("getSemantic: Failed to parse the key and value from the data")
        return json.dumps({"Status": "ERROR", "DATA": response, "Reason": 'Failed to parse: "data" should be str, "numTerms" should be int, "tokens_only" should be bool'})

    logger.info("getSemantic: data = " + str(word))
    try:
        if semanticobj!=None:
            semanticwords = semanticobj.semanticResumeSearch(word,numTerms)
        else:
            semanticwords=[]
        logger.info("getSemantic: related terms are = " + str(semanticwords))
    except Exception as e:
        logger.error("getSemantic: 'Internal server error'")
        return jsonify({"Status": "ERROR", "DATA": response, "Reason": "Internal server error"})
    loggerobj_req_res.info(str(word)+" = "+str(semanticwords))
    return jsonify({"Status": "SUCCESS", "DATA":semanticwords, "Reason": ""})
# def main():
#     app.run(ip, port=port, debug=False, threaded=True)
if __name__=='__main__':
    app.run(ip,port=port,debug=False,threaded=True)

