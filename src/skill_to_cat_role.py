import os
import time
import ast
import json
import re
import math
from collections import Counter
import operator

from loggingmodule import getlogger
import configparser
####################### Confi file reading
# os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
# config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","config","config.cfg")
# if not os.path.isfile(config_file_loc):
#     config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","..","config","config.cfg")
# config_obj = configparser.ConfigParser()

config_file_loc = "../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../../config/config.cfg"
config_obj = configparser.ConfigParser()
try:
    config_obj.read(config_file_loc)
    debugLevel = int(config_obj.get("COMMON","debuglevel"))
    logfilenameconfig = config_obj.get("COMMON","logfilename")
    skill_to_cat_role_file_name=config_obj.get("SkillToCatRole","skill_to_cat_role_matrix")
    synonym_file_path=(config_obj.get("SkillToCatRole","synonymsfilepath"))
except Exception as e:
    raise Exception("Config file error: "+str(e))


logfilename="../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../../logs/"
logfilepath=logfilename+ logfilenameconfig

# logfilepath=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","logs")
# if not os.path.isdir(logfilepath):
#     logfilepath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","..","logs")
# logfilepath=logfilepath+ logfilenameconfig


class Skill_to_Cat_Role:
    def __init__(self):
        start_time = time.time()
        synonym_file = os.path.join("data","category_predication",synonym_file_path)
        if os.path.isfile(synonym_file) and os.stat(synonym_file).st_size > 0:
            self.syn_list_dict = ast.literal_eval(open(synonym_file).read())
        else:
            self.syn_list_dict = {}
        skill_to_cat_role_file = os.path.join("data","category_predication",skill_to_cat_role_file_name)
        if os.path.isfile(skill_to_cat_role_file) and os.stat(skill_to_cat_role_file).st_size > 0:
            with open(skill_to_cat_role_file) as fileObj:
                self.skill_to_cat_role = json.load(fileObj)
        else:
            self.skill_to_cat_role = {}
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","role",
                               "role_suffix")) as fileobj:
            self.role_suffix = fileobj.read().split("\n")
        self.role_suffix = [r.strip().lower() for r in self.role_suffix]
        print("Skill_to_Cat_Role initialisation time : %s seconds." % (time.time() - start_time))

    def find_synonym_root(self, term):
        try:
            for k,v in self.syn_list_dict.items():
                if term in v:
                    return k
            return term
        except Exception as e:
            raise(Exception(str(e)))

    def formatquery(self,query):
        try:
            if query == None:
                return ''
            if len(query) == 0:
                return ''
            listofstop = [',', '-', '_', '/', '`', '~', '!', '@', '$', '%', '^', '&', '*', '(', ')', '=', '{', '}', '[',
                          ']', ';', ':', '"', '\'', '<', '>', '?', '/', ' ']
            for l in listofstop:
                query = query.replace(l, '').strip()
            return query
        except Exception as e:
            raise Exception(str(e))

    def find_mapped_role_and_cat(self,keyskills_txt):
        input_skills = [self.find_synonym_root(s.strip().lower()).lower().strip() for s in keyskills_txt.split(",") if len(s.strip()) > 0]
        # input_skills = [self.formatquery(ds) for ds in input_skills]
        query_list = []
        for s in input_skills:
            for rs in self.role_suffix:
                s = re.sub(r'\b%s\b' % rs, "", s)
            s = s.strip()
            s = self.formatquery(s)
            if len(s):
                query_list.append(s)
        input_skills = list(set(query_list))
        if len(input_skills)==0:
            return ('','')
        suggestor_role_list = []
        suggestor_cat_list = []
        found_skills = []
        total_weight = float(1)
        for k in input_skills:
            try:
                suggestor_cat_list.extend(self.skill_to_cat_role[k]["category"].keys())
                suggestor_role_list.extend(self.skill_to_cat_role[k]["role"].keys())
                found_skills.append(k)
                total_weight += self.skill_to_cat_role[k]["self_weight"]
            except:
                pass
        if len(found_skills)==0:
            return ('','')
        common_cats = Counter(suggestor_cat_list)
        common_roles = Counter(suggestor_role_list)
        suggested_roles = {k: 0 for k, v in common_roles.items()}
        for k in found_skills:
            self_weight = float(self.skill_to_cat_role[k]["self_weight"])
            idf_self = math.log((total_weight / self_weight))
            for r in suggested_roles.keys():
                try:
                    if self.skill_to_cat_role[k]["role"][r]>0.05*self_weight:
                        suggested_roles[r] += (float(self.skill_to_cat_role[k]["role"][r]) / self_weight) * idf_self
                except:
                    pass
        suggested_cats = {k: 0 for k, v in common_cats.items()}
        for k in found_skills:
            self_weight = float(self.skill_to_cat_role[k]["self_weight"])
            idf_self = math.log((total_weight / self_weight))
            for c in suggested_cats.keys():
                try:
                    if self.skill_to_cat_role[k]["category"][c] > 0.05 * self_weight:
                        suggested_cats[c] += (float(self.skill_to_cat_role[k]["category"][c]) / self_weight) * idf_self
                except:
                    pass
        return (max(suggested_cats, key=suggested_cats.get),sorted(suggested_roles.items(), key=operator.itemgetter(1), reverse=True)[:3])

if __name__ == "__main__":
    obj = Skill_to_Cat_Role()
    print(obj.find_mapped_role_and_cat("data science,machine learning")[0])
