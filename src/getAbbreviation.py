#!/usr/bin/env python
# coding: utf8
# import sys
import time
import copy
import re
# sys.path.insert(0, "../")

from loggingmodule import getlogger
import configparser
import os
import json,math
import operator
from collections import Counter
import skill_to_cat_role
####################### Confi file reading
config_file_loc = "../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../../config/config.cfg"
config_obj = configparser.ConfigParser()

try:
    config_obj.read(config_file_loc)
    debugLevel = int(config_obj.get("GetAbbreviation","debuglevel"))
    logfilenameconfig = config_obj.get("GetAbbreviation","logfilename")
    filename=config_obj.get("GetAbbreviation","filename")
    filename_common=config_obj.get("GetAbbreviation","filename_common")

except Exception as e:
    raise Exception("Config file error: "+str(e))



logfilename="../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../../logs/"
logfilename=logfilename+ logfilenameconfig

####################### Loggin Functionality
loggerobj = getlogger.GetLogger("abbreviation",logfilename,debugLevel)
logger = loggerobj.getlogger1()

class Abbreviation():
    def __init__(self):
        try:
            with open(os.path.join("data","abbreviation",filename)) as f:
                self.abbreviation = json.load(f)
        except Exception as e:
            logger.error("Abbreviation: __init__ Error: Failed to read abbreviation file: "+str(e))
            raise Exception("Failed to read abbreviation file: "+str(e))
        try:
            with open(os.path.join("data","abbreviation",filename_common)) as f:
                self.abbreviation_common = json.load(f)
        except Exception as e:
            logger.error("Abbreviation: __init__ Error: Failed to read abbreviation file: "+str(e))
            raise Exception("Failed to read abbreviation file: "+str(e))
        try:
            self.category_skill_obj = skill_to_cat_role.Skill_to_Cat_Role()
        except Exception as e:
            logger.error("Abbreviation: __init__ Error: Failed to create object: "+str(e))
            raise Exception("Abbreviation: __init__ Error: Failed to create object: "+str(e))
    def getAbbreviation(self,words,word):
        words = words.lower().strip()
        word = word.lower().strip()
        if type(words)!=str and type(word)!=str:
            logger.error("Abbreviation: getCategory Error: Expecting type should be str")
            raise Exception("Abbreviation: getCategory Error: Expecting type should be str")
        if len(words.strip())==0 and len(word.strip())!=None:
            return [word]
        category  = self.category_skill_obj.find_mapped_role_and_cat(words)
        if len(category)>0:
            category = category[0]
        else:
            return [word]

        try:
            abbr = self.abbreviation[category][word]
        except:
            try:
                abbr = self.abbreviation_common[word]
            except:
                abbr = [word]
        if words==word or words.strip()=="":
            abbr=[]
            for k, v in self.abbreviation.items():
                try:
                    abbr.extend(v[word])
                except:
                    abbr.append(word)
        abbr = list(set(abbr))
        return abbr


if __name__=="__main__":
    obj = Abbreviation()
    print(obj.getAbbreviation("chief operating officer","sem"))
    print(obj.getAbbreviation("sales head marketing head e&y","e and y"))

