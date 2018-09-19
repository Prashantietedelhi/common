#!/usr/bin/env python
# coding: utf8
# import sys
import time
import copy
import re
from nltk.stem.wordnet import WordNetLemmatizer

# sys.path.insert(0, "../")

from loggingmodule import getlogger
import configparser
import os
import json,math
import operator
from collections import Counter
# from multiprocessing.pool import ThreadPool
####################### Confi file reading
config_file_loc = "../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../../config/config.cfg"
config_obj = configparser.ConfigParser()

try:
    config_obj.read(config_file_loc)
    debugLevel = int(config_obj.get("MayAlsoKnow","debuglevel"))
    logfilenameconfig = config_obj.get("MayAlsoKnow","logfilename")
    filename=config_obj.get("MayAlsoKnow","filename")
    synonymsfilepath=(config_obj.get("MayAlsoKnow","synonymsfilepath"))
    singularized_words = (config_obj.get("MayAlsoKnow", "singularized_words"))
    skills_data = (config_obj.get("MayAlsoKnow", "skills_data"))
    role_data = (config_obj.get("MayAlsoKnow", "role_data"))
    linkdinskills_Crawled = (config_obj.get("MayAlsoKnow", "linkdinskills_Crawled"))
    linkdinskills_CrawledAll = (config_obj.get("MayAlsoKnow", "linkdinskills_CrawledAll"))
    stopwords_mayalsoknowDATA = (config_obj.get("MayAlsoKnow", "stopwords_mayalsoknow"))
    role_suffix_mayalsoknow = (config_obj.get("MayAlsoKnow", "role_suffix_mayalsoknow"))
    role_prefix_mayalsoknow = (config_obj.get("MayAlsoKnow", "role_prefix_mayalsoknow"))
    static_mayalsoknowData = (config_obj.get("MayAlsoKnow", "static_mayalsoknowData"))
    designations = (config_obj.get("MayAlsoKnow", "designations"))
    # threshold = float(config_obj.get("MayAlsoKnow", "threshold"))
    # numTermsCount = int(config_obj.get("MayAlsoKnow", "numTermsCount"))
    # percentageTerms = float(config_obj.get("MayAlsoKnow", "percentageTerms"))
except Exception as e:
    raise Exception("Config file error: "+str(e))



logfilename="../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../../logs/"
logfilename=logfilename+ logfilenameconfig

####################### Loggin Functionality
loggerobj = getlogger.GetLogger("mayalsoknow",logfilename,debugLevel)
logger = loggerobj.getlogger1()
logger.info("MayAlsoKnow Called")
class MayAlsoKnow():
    def __init__(self):
        try:
            starttime = time.time()
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","common",filename)) as fileobj:
                self.dict_map_All = json.load(fileobj)
                self.dict_map_Skills = self.dict_map_All
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","synonyms",synonymsfilepath)) as fileobj:
                self.dict_synonyms = json.load(fileobj)

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","skills",
                                   skills_data)) as fileobj:
                skillslist = json.load(fileobj)
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","role",
                                   role_data)) as fileobj:
                rolelist = json.load(fileobj)

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","role",
                                   role_suffix_mayalsoknow)) as fileobj:
                self.role_suffix=fileobj.read().split("\n")

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","role",
                                   role_prefix_mayalsoknow)) as fileobj:
                self.role_prefix=fileobj.read().split("\n")
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","mayalsoknow",
                                   static_mayalsoknowData)) as fileobj:
                self.static_mayalsoknow = json.load(fileobj)

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","designation",
                                   designations)) as fileobj:
                self.designations = json.load(fileobj)

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","stop_words",
                                   stopwords_mayalsoknowDATA)) as fileobj:
                self.stopwords_mayalsoknow = list(fileobj.readlines())
            self.stopwords_mayalsoknow=[i.replace(r"\n","").strip().lower() for i in self.stopwords_mayalsoknow]


            stopwords_mayalsoknow={}
            for sk in self.stopwords_mayalsoknow[:]:
                try:
                    stopwords_mayalsoknow[self.dict_synonyms[sk].replace(' ','')] = sk
                except:
                    stopwords_mayalsoknow[sk.replace(' ','')] = sk

            self.stopwords_mayalsoknow=stopwords_mayalsoknow


            self.replaceBackChar = [(" dot ", "."), ("dot ", "."), ("dot", "."), (" sharp", "#"), ("sharp", "#"),
                                    (" plus", "+"), ("plus ", "+"), ("plus", "+")]
            self.skillslist = {}
            self.allroleskill={}

            for sk in skillslist:
                self.skillslist[sk.lower().strip()] = sk.lower().strip()
                self.allroleskill[sk.lower().strip()] = sk.lower().strip()
            for sk in rolelist:
                self.allroleskill[sk.lower().strip()] = sk.lower().strip()

            self.role_suffix = [r.strip().lower() for r in self.role_suffix]
            self.role_suffix.sort(key=lambda x: len(x.split()), reverse=True)
            self.role_prefix = [r.strip().lower() for r in self.role_prefix]
            self.designations.sort(key=lambda x: len(x.split()), reverse=True)
            self.role_prefix.extend(self.designations)
            self.role_prefix = list(set(self.role_prefix))
            self.role_prefix.sort(key=lambda x: len(x.split()), reverse=True)

            self.lmtzr = WordNetLemmatizer()
            self.NotSemantic={}
            print("mayalsoknow initialization time : " ,time.time()-starttime)
        except Exception as e:
            print("MayAlsoKnow __init__ error : ",str(e))
            logger.error("MayAlsoKnow __init__ error : ",str(e))
            raise Exception(str(e))


    def replace_prefix_suffix(self,tmp,numThreshold):
        tmp = re.sub(r"\b%s\b" % "sr dot", "senior", tmp)
        tmp = re.sub(r"\b%s\b" % "jr dot", "junior", tmp)
        tmp = re.sub(r"\b%s\b" % "Asst dot", "assistant", tmp)
        tmp = re.sub(r"\b%s\b" % "Ass dot", "assistant", tmp)
        final_tmp = tmp
        try:
            if "software engineer" not in tmp and "hardware engineer" not in tmp and "software developer" not in tmp and "software" not in tmp and "hardware" not in tmp:
                q_removedprefix = tmp
                if len(set(tmp.split())-set(self.role_prefix))!=0:
                    for rp in self.role_prefix:
                        try:
                            q_removedprefix = re.sub(r"\b%s\b" % rp, "", q_removedprefix).strip()
                        except:
                            q_removedprefix = q_removedprefix.replace(rp,"").strip()
                    q_removedprefix = re.sub(" +", " ", q_removedprefix, flags=re.IGNORECASE | re.MULTILINE).strip()
                    final_tmp = q_removedprefix
                    q_removedprefix = q_removedprefix.replace(' ', '')

                    if self.dict_map_All[q_removedprefix]['self_weight'] < numThreshold or q_removedprefix!=tmp:
                        raise Exception

        except:
            if tmp.split()[
                -1] in self.role_suffix and "software engineer" not in tmp and "hardware engineer" not in tmp and "software developer" not in tmp and "software" not in tmp and "hardware" not in tmp and  final_tmp.split()[
                -1] in self.role_suffix:
                final_tmp = " ".join(final_tmp.split()[:-1])

        return final_tmp
    def find_similar_skill(self, query,numTerms,tokens_only,numThreshold,percentage_terms,threshold):
        try:
            temquery=query
            result = {}
            new_query = []
            mapped_original_terms={}
            for q in query:
                q = q.lower().strip()
                q = re.sub(' +',' ',q,flags=re.IGNORECASE|re.MULTILINE)

                if len(q):
                    try:
                        q = self.dict_synonyms[q]
                    except:
                        pass
                    tmp = q
                    q = q.replace(' ','')
                    try:

                        if self.dict_map_All[q]['self_weight']<numThreshold:
                            raise Exception
                    except:
                        final_tmp = self.replace_prefix_suffix(tmp,numThreshold)
                        q=final_tmp.replace(' ','')

                    try:
                        self.stopwords_mayalsoknow[q]
                    except:
                        new_query.append(q)
                        mapped_original_terms[q]=tmp
            query = list(set(new_query))
            if len(query) == 0:
                result[",".join(temquery)] = []
                return result
            elif len(query)>1:
                found_skills = []
                suggestor_list = []
                total_weight = float(1)
                for q in query:
                    try:
                        if self.dict_map_All[q]["self_weight"]>numThreshold:
                            suggestor_list.extend(self.dict_map_All[q].keys())
                            total_weight += self.dict_map_All[q]["self_weight"]
                            found_skills.append(q)
                    except:
                        pass
                if len(found_skills) == 0:
                    result[",".join(temquery)] = []
                    return result
                common = Counter(suggestor_list)
                del common["self_weight"]
                max_common = common[max(common, key=common.get)]
                related_skills = [k for k, v in common.items() if v == max_common]
                suggestor_mat = {}
                for q in found_skills:
                    self_weight = float(self.dict_map_All[q]["self_weight"])
                    idf_self = math.log((total_weight / self_weight))
                    for s in related_skills:
                        try:
                            if float(self.dict_map_All[q][s]) > float(self_weight * percentage_terms) and float(
                                    self.dict_map_All[q][s]) > float(self.dict_map_All[s.replace(' ','')]["self_weight"] * threshold):
                                val = format(round((float(self.dict_map_All[q][s]) / self_weight) * idf_self * (
                                float(self.dict_map_All[q][s]) / self.dict_map_All[s.replace(' ','')]["self_weight"]),5),'f')
                                try:
                                    suggestor_mat[s] += val
                                except:
                                    suggestor_mat[s] = val
                        except:
                            pass

            else:
                try:
                    self_weight = float(self.dict_map_All[query[0]]["self_weight"])
                    suggestor_mat = {}
                    if self_weight > numThreshold:
                        for k,v in self.dict_map_All[query[0]].items():
                            if k!="self_weight":
                                try:
                                    if float(v)>float(self_weight*percentage_terms) and float(v)>float(self.dict_map_All[k.replace(' ','')]["self_weight"]*threshold):# or self_weight>4000:
                                            suggestor_mat[k] = format(round((v/self_weight)*(v/self.dict_map_All[k.replace(' ','')]["self_weight"]),5),'f')
                                except:
                                    pass
                    if len(suggestor_mat.keys()) == 0:
                        q=self.replace_prefix_suffix(mapped_original_terms[query[0]],numThreshold)
                        q = q.replace(' ', '')
                        for k,v in self.dict_map_All[q].items():
                            if k!="self_weight":
                                try:
                                    if float(v)>float(self_weight*percentage_terms) and float(v)>float(self.dict_map_All[k.replace(' ','')]["self_weight"]*threshold):# or self_weight>4000 :
                                        suggestor_mat[k] = format(round((v/self_weight)*(v/self.dict_map_All[k.replace(' ','')]["self_weight"]),5),'f')
                                except:
                                    pass
                except:
                    suggestor_mat={}
            sorted_x = sorted(suggestor_mat.items(), key=operator.itemgetter(1), reverse=True)
            # result[",".join(temquery)] = sorted_x[:numTerms]
            sorted_x = sorted_x[:numTerms]
            new_sorted_x = []
            for sx in sorted_x:
                if sx[1]:
                    nsx = sx[0]
                    nsx = re.sub(' +',' ',nsx,flags=re.IGNORECASE|re.MULTILINE)
                    for rbc in self.replaceBackChar:
                        k = rbc[0]
                        v = rbc[1]
                        try:
                            nsx = re.sub(r"\b%s\b" % k, v, nsx)
                        except:
                            nsx = nsx.replace(k,v)
                        nsx = nsx.strip()
                    new_sorted_x.append((nsx,sx[1]))
            # result[",".join(temquery)] = sorted_x[:numTerms]
            result[",".join(temquery)] = new_sorted_x
            return result
        except Exception as e:
            print("MayAlsoKnow find_similar_skill error : ",str(e))
            logger.error("MayAlsoKnow find_similar_skill error : ",str(e))
            raise (Exception(str(e)))
    def getDesignation(self, res):
        newres = copy.deepcopy(res)
        for k, v in res.items():
            for i in self.designations:
                if len(newres[k]) != len(res[k]):
                    break
                if k in self.designations:
                    newres[k] = []
                if re.findall(r"\b%s\b" % i, k):
                    try:
                        static_designation = self.static_mayalsoknow[i]
                        for sti, stv in static_designation.items():
                            try:
                                temp_word = re.sub(r"\b%s\b" % i, sti, k)
                            except:
                                temp_word = k.replace(i,sti)
                            try:
                                dict(newres[k])[temp_word]

                            except:
                                newres[k].append((temp_word, 100))
                    except:
                        pass
        return newres

    def semanticSkillsJobSearch(self,listsent,numTerms=5,tokens_only=False, numTermsCount=1000,percentageTerms=0.15,threshold=0.1):
        try:
            res = {}
            for i in listsent:
                k = ",".join(i)
                tmp_v = self.find_similar_skill(i, numTerms, tokens_only, numTermsCount,percentageTerms,threshold)
                res.update(tmp_v)

            return res
        except Exception as e:
            print("MayAlsoKnow semanticSkills error : ",str(e))
            logger.error("MayAlsoKnow semanticSkills error : ",str(e))
            raise Exception("mayalsoknow semanticSkills error "+str(e))

    def semanticSkillsResumeSearch(self, listsent, numTerms=5, tokens_only=False, numTermsCount=1000, percentageTerms=0.20,
                                threshold=0.15):
        try:
            res = {}
            for i in listsent:
                k = ",".join(i)
                tmp_v = self.find_similar_skill(i, numTerms, tokens_only, numTermsCount,percentageTerms,threshold)
                res.update(tmp_v)
                if len(i) == 1:
                    res = self.getDesignation(res)

            return res
        except Exception as e:
            print("MayAlsoKnow semanticSkills error : ", str(e))
            logger.error("MayAlsoKnow semanticSkills error : ", str(e))
            raise Exception("mayalsoknow semanticSkills error " + str(e))
if __name__=="__main__":
    obj = MayAlsoKnow()
    st=[["instructor"]]

    print (obj.semanticSkillsJobSearch(st, 5, False))
    sta=time.time()

    print (obj.semanticSkillsResumeSearch(st, 5, False))
    print (time.time()-sta)