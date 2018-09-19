#!/usr/bin/env python
# coding: utf8
# import sys
#
# sys.path.insert(0, "../")
from loggingmodule import getlogger
import configparser
import math
import os,time
import json
####################### Confi file reading


config_obj = configparser.ConfigParser()
config_file_loc = "../../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../config/config.cfg"
config_obj.read(config_file_loc)
try:
    debugLevel = int(config_obj.get("MonsterWeightage","debuglevel"))
    logfilenameobj = config_obj.get("MonsterWeightage","logfilename")
    roundVal=int(config_obj.get("MonsterWeightage","roundVal"))
    default_idf=int(config_obj.get("MonsterWeightage","default_idf"))
    splitparameter=str(config_obj.get("MonsterWeightage","splitparameter"))
    optimize=int(config_obj.get("MonsterWeightage","optimize"))
    filepath=(config_obj.get("MonsterWeightage","filepath"))
    semantic_stopwords=(config_obj.get("MonsterWeightage","semantic_stopwords"))
    synonymsfilepath = (config_obj.get("MayAlsoKnow", "synonymsfilepath"))

except Exception as e:
    raise Exception("Config file error "+str(config_file_loc))


####################### Loggin Functionality
logfilename="../../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../logs/"
logfilename=logfilename+logfilenameobj

try:
    logger = getlogger.GetLogger("MonsterWeightage",logfilename,debugLevel)
    logger = logger.getlogger1()
except Exception as e:
    raise Exception(e)
logger.info("MonsterWeightage called")

class WordWeightage():
    def __init__(self):
        logger.info("WordWeightage class called")
        try:
            starttime= time.time()
            self.filepath=os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","common", filepath)


            self.datadict={}
            self.static_weightage={}

            try:
                with open(self.filepath) as fileobj:
                    data = json.load(fileobj)
            except Exception as e:
                print("WordWeightage __init__ error: Failed to read the file: "+str(e))
                logger.error("WordWeightage: Failed to read the file: "+str(e))
                raise Exception("WordWeightage: Failed to read the file: "+str(e))


            try:
                with open(os.path.join("data","spell","word_spell_Final")) as fileobj:
                    self.wordspell = json.load(fileobj)
            except Exception as e:
                print("WordWeightage __init__ error: Failed to read the word_spells file: "+str(e))
                logger.error("WordWeightage: Failed to read the word_spells file: "+str(e))
                raise Exception("WordWeightage: Failed to read the word_spells file: "+str(e))

            try:
                with open(os.path.join("data","stop_words",semantic_stopwords)) as fileobj:
                    stopwords = list(fileobj.readlines())
            except Exception as e:
                print("WordWeightage __init__ error: Failed to read the semantic_stopwords file: "+str(e))
                logger.error("WordWeightage: Failed to read the semantic_stopwords file: "+str(e))
                raise Exception("WordWeightage: Failed to read the semantic_stopwords file: "+str(e))

            stopwords = [i.replace("\n", "") for i in stopwords]

            try:
                with open(
                        os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "synonyms",synonymsfilepath)) as fileobj:
                    self.dict_synonyms = json.load(fileobj)
            except Exception as e:
                print("WordWeightage __init__ error: Failed to read the file: " + str(e))
                logger.error("WordWeightage: Failed to read the file: " + str(e))
                raise Exception("WordWeightage: Failed to read the file: " + str(e))

            for st in stopwords:
                self.static_weightage[st]=2


            try:
                self.len_data=0
                for k,v in data.items():
                    self.datadict[k]=v['self_weight']
                    self.len_data=self.len_data+v['self_weight']
            except Exception as e:
                print("WordWeightage __init__ error: Failed to process: "+str(e))
                logger.error("WordWeightage: Failed to process: "+str(e))
                raise Exception("WordWeightage: Failed to process: "+str(e))
            print("word weightage initialization time : " ,time.time()-starttime)

        except Exception as e:
            print("WordWeightage __init__ error: " + str(e))
            logger.error("WordWeightage: Exception: "+str(e))
            raise Exception("WordWeightage: Exception: "+str(e))

    def tokenize(self, text):
        try:
            return text.split(splitparameter)
        except Exception as e:
            logger.error("Tokenize tokenize: Failed to tokenize: "+str(e))
            raise Exception(e)

    def n_containing(self,word):
        try:
            if word in self.datadict:
                val=self.datadict[word]
            else:
                val=0
        except Exception as e:
            print("WordWeightage n_containing error: " + str(e))
            logger.error("WordWeightage n_containing: failed: "+str(e))
            raise Exception(e)
        return val

    def idf(self,word):
        try:

            d = self.len_data / (1 + self.n_containing(word))
        except Exception as e:
            print("WordWeightage idf error: " + str(e))
            logger.error("WordWeightage idf: failed: " + str(e))
            raise Exception(e)
        if d == 0:
            return default_idf
        return math.log(d)

    def tfidf(self,word):
        try:
            word=self.dict_synonyms[word]
        except:
            pass
        try:
            word = self.wordspell[word]
        except:
            word = word
        word = word.replace(" ",'')
        try:
            val = self.static_weightage[word]
        except:
            try:
                val= 1 * self.idf(word)
            except Exception as e:
                print("WordWeightage tfidf error: " + str(e))
                logger.error("WordWeightage idf: failed: " + str(e))
                raise Exception(e)
        return  val

    def wordweight(self,sent):
        logger.info("WordWeightage: " + str(sent))
        if type(sent)==None:
            logger.error("WordWeightage wordweight: Expecting text got None")
            return {}
        if sent=='' and len(sent)==0:
            logger.error("WordWeightage wordweight: Expecting text got Empty")
            return {}

        dictdata = {}
        try:
            scores = {word: self.tfidf(word) for word in self.tokenize(sent)}
            sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for word, score in sorted_words:
                if word not in dictdata:
                    dictdata[word] = round(score, roundVal)
                else:
                    if dictdata[word] < round(score, roundVal):
                        dictdata[word] = round(score, roundVal)

        except Exception as e:
            print("WordWeightage wordweight error: " + str(e))
            logger.error("WordWeightage wordweight: Failed: " + str(e))
            raise Exception("word_weightageV2 wordweight error: " + str(e))
        logger.info("WordWeightage: Successfully: "+str(dictdata))

        return dictdata



if __name__=='__main__':
    sent="nlp,natural language processing,hr,human resource"
    obj=WordWeightage()
    print (obj.wordweight(sent))
