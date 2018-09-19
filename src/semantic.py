# Semantic Search
# Authors: <Singh, Prashant <Prashant.Singh@Monsterindia.com>>
#          <Sharma, Shashikant <Shashikant.Sharma@Monsterindia.com>>
'''
The Semantic Search Library deals with following functionalities:
1. Data cleaning
2. Phrase Handling
3. NER Detection
4. MayAlsoKnow (Semantic Terms)
5. WordWeightage

e.x:
    from semantic import Semantic
    semanticSearch = Semantic()
    semanticSearch.semanticResumeSearch("java,hadoop natural language processing")
    semanticSearch.semanticJobSearch("java,hadoop natural language processing")

'''

# Maintainer, contributors, etc.
__maintainer__ = "Prashant, Shashikant Sharma"
__maintainer_email__ = [
                        "Prashant.Singh@Monsterindia.com",
                        "Shashikant.Sharma@Monsterindia.com"
]

import os,re,json,copy,time
from nltk.corpus import stopwords
from nltk import word_tokenize
from configparser import ConfigParser

###########################################################
# TOP-LEVEL MODULES
###########################################################

# Import top-level functionality into top-level namespace
from phrasehandlingv3 import PhraseHandling
from mayalsoknowV2 import MayAlsoKnow
from NER_detector import NER_Detector
from word_weightageV3 import WordWeightage
import parse,reinitializedata
from loggingmodule import getlogger
from getAbbreviation import Abbreviation

#Config file reading
config_obj = ConfigParser()
config_file_loc = "../../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../config/config.cfg"
config_obj.read(config_file_loc)
try:
    debugLevel = int(config_obj.get("MonsterSemanticSearch","debuglevel"))
    logfilenameobj = config_obj.get("MonsterSemanticSearch","logfilename")
except Exception as e:
    raise Exception("Config file error "+str(config_file_loc))


#Logging file initialization
####################### Loggin Functionality
logfilename="../../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../logs/"
logfilename=logfilename+logfilenameobj

try:
    logger = getlogger.GetLogger("MonsterSemanticSearch",logfilename,debugLevel)
    logger = logger.getlogger1()
except Exception as e:
    raise Exception(e)
logger.info("Semantic Search Starting")
class Semantic():
    '''Semantic search base class. It defines two functions called semanticResumeSearch and semanticJobSearch.

    >>>searchObj=Semantic()
    >>>searchObj.semanticResumeSearch("java,hadoop natural language processing")
    >>>searchObj.semanticJobSearch("java,hadoop natural language processing")

    Note: both semanticResumeSearch and semanticJobSearch accept optional argument: numTerms
    numTerms: total number of semantic terms need to be added,
    '''
    def __init__(self):
        '''
        Constructor deals with:
        1. reinitilazing the files inside data folders:
            a. reinitializing roles, skills, company_names
        2. loading all the necessary files:
            a. designations
            b. stopwords
            c. semantic_stopwords
            d. static_mayalsoknow
            e. role_suffix_mayalsoknow
        3. creating necessary objects
            a. phrase object
            b. word weightage object
            c. NER detector object
            d. semantic terms object (mayalsoknow)
        '''
        ####### reinitialize all data
        # starttime = time.time()
        reinitializedata.reinitialize()

        self.abbreviation_obj = Abbreviation()

        try:
            with open(os.path.join("data", "designation","designations")) as designationsFileObj:
                self.designations = json.load(designationsFileObj)
        except FileNotFoundError as file_not_found:
            print("Semantic __init__ read designations FileNotFoundError: ", str(file_not_found))
            logger.error("Semantic __init__ read designations FileNotFoundError: ", str(file_not_found))
            raise FileNotFoundError("Semantic __init__ read designations FileNotFoundError: ", str(file_not_found))
        except Exception as otherException:
            print("Semantic __init__ read designations error: ", str(otherException))
            logger.error("Semantic __init__ read designations error: ", str(otherException))
            raise Exception("Semantic __init__ read designations error: ", str(otherException))

        self.designations = [designation.replace('\n', '') for designation in self.designations]
        self.designations.sort(key=lambda x: len(x.split()), reverse=True)


        try:
            with open(os.path.join("data","stop_words","stopwords"),encoding="utf8") as fileobj:
                stopWordsData = fileobj.readlines()
        except FileNotFoundError as file_not_found:
            print("Semantic __init__ read stopwords FileNotFoundError: ", str(file_not_found))
            logger.error("Semantic __init__ read stopwords FileNotFoundError: ", str(file_not_found))
            raise FileNotFoundError("Semantic __init__ read stopwords FileNotFoundError: ", str(file_not_found))
        except Exception as otherException:
            print("Semantic __init__ read stopwords error: ", str(otherException))
            logger.error("Semantic __init__ read stopwords error: ", str(otherException))
            raise Exception("Semantic __init__ read stopwords error: ", str(otherException))

        self.stopwords = dict((i.replace('\n', ''), 1) for i in stopWordsData)

        try:
            with open(os.path.join("data","stop_words","semantic_stopwords"),encoding="utf8") as fileobj:
                semanticStopwordsData = fileobj.readlines()
        except FileNotFoundError as file_not_found:
            print("Semantic __init__ read semantic_stopwords FileNotFoundError: ", str(file_not_found))
            logger.error("Semantic __init__ read semantic_stopwords FileNotFoundError: ", str(file_not_found))
            raise FileNotFoundError("Semantic __init__ read semantic_stopwords FileNotFoundError: ", str(file_not_found))
        except Exception as otherException:
            print("Semantic __init__ read semantic_stopwords error: ", str(otherException))
            logger.error("Semantic __init__ read semantic_stopwords error: ", str(otherException))
            raise Exception("Semantic __init__ read semantic_stopwords error: ", str(otherException))
        self.semantic_stopwords = dict((i.replace('\n', ''), 1) for i in semanticStopwordsData)

        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data","mayalsoknow",
                                   "static_mayalsoknow")) as fileobj:
                self.static_mayalsoknow = json.load(fileobj)
        except FileNotFoundError as file_not_found:
            print("Semantic __init__ read static_mayalsoknow FileNotFoundError: ", str(file_not_found))
            logger.error("Semantic __init__ read static_mayalsoknow FileNotFoundError: ", str(file_not_found))
            raise FileNotFoundError("Semantic __init__ read static_mayalsoknow FileNotFoundError: ", str(file_not_found))
        except Exception as otherException:
            print("Semantic __init__ read static_mayalsoknow error: ", str(otherException))
            logger.error("Semantic __init__ read static_mayalsoknow error: ", str(otherException))
            raise Exception("Semantic __init__ read static_mayalsoknow error: ", str(otherException))

        try:
            with open(os.path.join("data","role","role_suffix_mayalsoknow"),encoding="utf8") as fileobj:
                roleSuffixMayalsoknow = fileobj.readlines()
        except FileNotFoundError as file_not_found:
            print("Semantic __init__ read role_suffix_mayalsoknow FileNotFoundError: ", str(file_not_found))
            logger.error("Semantic __init__ read role_suffix_mayalsoknow FileNotFoundError: ", str(file_not_found))
            raise FileNotFoundError("Semantic __init__ read role_suffix_mayalsoknow FileNotFoundError: ",
                                    str(file_not_found))
        except Exception as otherException:
            print("Semantic __init__ read role_suffix_mayalsoknow error: ", str(otherException))
            logger.error("Semantic __init__ read role_suffix_mayalsoknow error: ", str(otherException))
            raise Exception("Semantic __init__ read role_suffix_mayalsoknow error: ", str(otherException))

        self.semantic_stopwords2 = dict((i.lower().replace('\n', '').strip(), 1) for i in roleSuffixMayalsoknow)


        ###################### objects creation
        try:
            self.phraseobj=PhraseHandling()
            logger.info("PhraseHandling Started")

        except Exception as e:
            print("Semantic __init__ PhraseHandling Object creation error : ", str(e))
            logger.error("Semantic __init__ PhraseHandling Object creation error : ", str(e))
            raise Exception(e)

        try:
            self.mayalsoknowobj=MayAlsoKnow()
            logger.info("MayAlsoKnow Started")

        except Exception as e:
            print("Semantic __init__ MayAlsoKnow Object creation error : ", str(e))
            logger.error("Semantic __init__ MayAlsoKnow Object creation error : ", str(e))
            raise Exception(e)

        try:
            self.nerdetectorobj=NER_Detector()
            self.nerdetectorobj.categorize_txt(["121abcd345"])
            logger.info("NER Started")

        except Exception as e:
            print("Semantic __init__ NER_Detector Object creation error : ", str(e))
            logger.error("Semantic __init__ NER_Detector Object creation error : ", str(e))
            raise Exception(e)

        try:
            self.wordweightobj=WordWeightage()
            logger.info("WordWeghtage Started")

        except Exception as e:
            print("Semantic __init__ WordWeightage Object creation error : ", str(e))
            logger.error("Semantic __init__ WordWeightage Object creation error : ", str(e))
            raise Exception(e)

        try:
            self.parser=parse.Parse()
            logger.info("Parser Started")

        except Exception as e:
            print("Semantic __init__ Parse Object creation error : ", str(e))
            logger.error("Semantic __init__ Parse Object creation error : ", str(e))

            raise Exception(e)


        try:
            self.nltkStopWords = list(set(stopwords.words('english')))
        except Exception as nltkStopWordsException:
            print("Semantic __init__ nltk stop words initilization error: "+str(nltkStopWordsException))
            logger.error("Semantic __init__ nltk stop words initilization error: "+str(nltkStopWordsException))
            raise Exception(nltkStopWordsException)

        self.punct_marks = {",", "'", "/", "?", ".", ">", "<", ":", ";", '"', "{", "}", "[", "]", "\\", "|", "!", "@",
                            "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "`", "~", "@"}
        self.replaceBackChar = [(" dot ", "."), ("dot ", "."), ("dot", "."), (" sharp", "#"), ("sharp", "#"),
                                (" plus", "+"), ("plus ", "+"), ("plus", "+")]
        # print("semantic initialization time : ", time.time() - starttime)

        # return re.sub(r"\bor\b", "or", re.sub(r"\band\b", "and", re.sub(r"\bnot\b", "not", stri)))

    def getPhrases(self, chunksList):
        '''
        Extract phrases of terms
        :param chunksList: list of words
        :return: list of phrases detected
        '''
        # st = time.time()

        if type(chunksList)!=list:
            logger.error("Semantic getPhrases: Expecting allPhrases of type list")
            raise Exception("Semantic getPhrases: Expecting allPhrases of type list")
        try:
            allphrases = []
            for chunk in chunksList:
                allphrases.extend(self.phraseobj.phrases(chunk))
            # print("Phrase handling time: ",time.time()-st)
            return allphrases
        except Exception as GetPhrasesError:
            print("Semantic getPhrases failed to get phrases: " + str(GetPhrasesError))
            logger.error("Semantic getPhrases failed to get phrases: " + str(GetPhrasesError))
            raise Exception("Semantic getPhrases failed to get phrases: " + str(GetPhrasesError))

    def removeStopWords(self, allPhrases):
        '''
        Remove stop words from the allPhrases
        :param allPhrases: list of phrases detected
        :return: new phrases list contains removed stopwords
        '''
        if type(allPhrases)!=list:
            logger.error("Semantic removeStopWords: Expecting allPhrases of type list")
            raise Exception("Semantic removeStopWords: Expecting allPhrases of type list")
        try:
            # st = time.time()
            newPhrases = []
            for phrase in allPhrases:
                if phrase != "1234":
                    try:
                        self.stopwords[phrase.lower().strip()]
                    except:
                        listwords = word_tokenize(phrase)
                        if (len(set(listwords) & set(self.stopwords)) != len(set(listwords))) and (
                                    len(set(phrase) & set(self.punct_marks)) != len(set(phrase))):
                            newPhrases.append(phrase)
            # print("Stopword removal time: ",time.time()-st)

            return newPhrases
        except Exception as GetPhrasesError:
            print("Semantic removeStopWords failed to remove stopwords: " + str(GetPhrasesError))
            logger.error("Semantic removeStopWords failed to remove stopwords: " + str(GetPhrasesError))
            raise Exception("Semantic removeStopWords failed to remove stopwords: " + str(GetPhrasesError))
    def categorizeText(self, allPhrases):
        '''
        Call NER_detector module to extract all the categories of words
        :param allPhrases: list of phrases detected
        :return: category of phrases
        '''
        # st=time.time()
        if type(allPhrases)!=list:
            logger.error("Semantic categorizeText: Expecting allPhrases of type list")
            raise Exception("Semantic categorizeText: Expecting allPhrases of type list")
        try:
            category = self.nerdetectorobj.categorize_txt(allPhrases)
        except:
            print("Semantic semantic error : NER detector failed")
            logger.error("Semantic semantic error : NER detector failed")
        # print("NER time: " , time.time() - st)

        return category

    def getWordWeightage(self, allPhrases):
        '''
        Call word_weightage module to extact all word weight
        :param allPhrases: list of phrases detected
        :return: weight of each phrases
        '''
        # st = time.time()
        if type(allPhrases)!=list:
            logger.error("Semantic getWordWeightage: Expecting allPhrases of type list")
            raise Exception("Semantic getWordWeightage: Expecting allPhrases of type list")
        try:
            allWordWeight = self.wordweightobj.wordweight(",".join(allPhrases))
            # print("Word weightage time: ", time.time() - st)

            return allWordWeight
        except Exception as GetPhrasesError:
            print("Semantic getWordWeightage failed to get word weights: " + str(GetPhrasesError))
            logger.error("Semantic getWordWeightage failed to get word weights: " + str(GetPhrasesError))
            raise Exception("Semantic getWordWeightage failed to get word weights: " + str(GetPhrasesError))

    def getSemanticTermsQuery(self, allPhrases, category):
        '''
        Extract semantic terms for skills and role and combination of both
        :param allPhrases: list of all phrases
        :param category: category of the phrases
        :return: semantic terms, and recommendation result
        '''
        # st=time.time()
        queryTerms = []
        recommendQueryTerms = []
        if type(allPhrases)!=list:
            logger.error("Semantic getSemanticTerms: Expecting allPhrases of type list")
            raise Exception("Semantic getSemanticTerms: Expecting allPhrases of type list")
        for d in allPhrases:
            if len(allPhrases) > 1:
                if d not in self.semantic_stopwords:
                    if d in category["skill"] or d in category["role"]:
                        queryTerms.append([d])
                        recommendQueryTerms.append(d)
            else:
                if d in category["skill"] or d in category["role"]:
                    queryTerms.append([d])
                    recommendQueryTerms.append(d)

        if len(recommendQueryTerms) > 1:
            queryTerms.append(recommendQueryTerms)
        # print("Mayalsoknow time: ", time.time() - st)

        return queryTerms, recommendQueryTerms

    def preprocessing(self,chunks):
        '''
        preprocessing function is responsible for:
        1. cleaning data
        2. extracting phrase of terms
        3. NER categorization
        4. word weight of the terms
        5. extract semantic terms of a word (mayalsoknow)
        :param chunks: accept query string.
        :return: query terms, category, all detected phrases, word weightage, experience string, recommendataion query string and experignce
        '''

        ######## extract sure chunks inside quotes, other chunks, experience
        # st=time.time()
        unsure_chunks, sure_chunks, exp, exp_string = self.parser.clean_string(chunks)

        ######## clean sure chunks and unsure chunks
        if type(sure_chunks)!=list and type(unsure_chunks)!=list:
            logger.error("semantic preprocessing error: Expecting sure_chinks and unsure chunks of type list")
            raise Exception("semantic preprocessing error: Expecting sure_chinks and unsure chunks of type list")
        sure_chunks = [self.parser.parse(i) for i in sure_chunks]
        unsure_chunks = [self.parser.parse(i) for i in unsure_chunks]

        ######## extract phrases from unsure chunks and
        allPhrases = self.getPhrases(unsure_chunks)
        allPhrases.extend(sure_chunks)

        #add synonyms of allPhrases
        # allPhrases = [self.parser.replaceSynonyms(i) for i in allPhrases]
        # allPhrases.extend(allPhrases)
        allPhrases = list(set(allPhrases))
        allphrases_temp = []
        self.mapped_abbreviation = {}
        for phrases in allPhrases:
            abbr = self.abbreviation_obj.getAbbreviation(",".join(allPhrases), phrases)
            if len(abbr)>1:
                for ab in abbr:
                    if ab!=phrases:
                        allphrases_temp.append(ab)
            else:
                allphrases_temp.extend(abbr)

            for ab in abbr:
                if ab!=phrases:
                    self.mapped_abbreviation[ab] = phrases
                    break
            # allphrases_temp.append(phrases)
        allPhrases = list(set(allphrases_temp))
        ####### remove and stop words in the phrases detected or puctuation mark
        allPhrases = self.removeStopWords(allPhrases)

        ###### NER categorize
        category = self.categorizeText(allPhrases)

        ###### find word weight of the terms
        allwordweight = self.getWordWeightage(allPhrases)


        ######## extract terms for mayalsoknow of skill and role
        queryterms, recommendqueryterms = self.getSemanticTermsQuery(allPhrases, category)
        # print("preprocessing: ",time.time()-st)
        return queryterms,category,allPhrases,allwordweight,exp_string,recommendqueryterms,exp

    def updateResult(self,res):
        # st=time.time()
        if type(res)!=dict:
            logger.error("semantic updateResult error: expecting res of type dict")
            raise Exception("semantic updateResult error: expecting res of type dict")
        old_res=copy.deepcopy(res)

        for k,v in res.items():
            if k!='recommendations':
                if type(v) != list:
                    logger.error("semantic updateResult error: expecting values of type list")
                    raise Exception("semantic updateResult error: expecting values of type list")
                for value in v:
                    if type(value) != dict:
                        logger.error("semantic updateResult error: expecting values of type dict")
                        raise Exception("semantic updateResult error: expecting values of type dict")
                    if 'name' in value:
                        nsx=value['name']
                        try:
                            abbr = self.mapped_abbreviation[nsx]
                            newVal = {}
                            if value['name'] != abbr:
                                newVal['name'] = abbr
                                newVal['semanticTerms'] = []
                                newVal['weightage'] = value['weightage']

                                old_res[k].append(newVal)
                        except:
                            pass
                        for rbc in self.replaceBackChar:
                            replaceBack_Key = rbc[0]
                            replaceBack_Value = rbc[1]
                            try:
                                nsx = re.sub(r"\b%s\b" % replaceBack_Key, replaceBack_Value, nsx)
                            except:
                                nsx = nsx.replace(replaceBack_Key,replaceBack_Value)
                        newVal={}
                        if value['name']!=nsx:
                            newVal['name']=nsx
                            newVal['semanticTerms']=[]
                            newVal['weightage']=value['weightage']

                            old_res[k].append(newVal)
        # print("update result time: ", time.time() - st)

        return old_res
    def semanticResumeSearch(self,chunks,numTerms=5):
        try:
            queryterms, category, allphrases, allwordweight, exp_string, recommendqueryterms, exp = self.preprocessing(chunks)
            semanticterms = self.mayalsoknowobj.semanticSkillsResumeSearch(queryterms, numTerms=numTerms)
            termsrel = {}
            recommend_skills=[]
            for k,v in category.items():
                if k not in termsrel:
                    termsrel[k]=[]
                if  k=="role" or k=="skill":
                    if len(allphrases) > 1:
                            recommend_skills.append(k.lower().strip())
                            for v1 in v:
                                if v1 not in self.semantic_stopwords2:
                                    tempdict={}
                                    tempdict['name']=v1
                                    if v1 in semanticterms:
                                        tempdict['semanticTerms']=semanticterms[v1]
                                    else:
                                        tempdict['semanticTerms'] =[]
                                    if v1 in allwordweight:
                                        tempdict['weightage']=allwordweight[v1]
                                    else:
                                        tempdict['weightage']=0
                                    termsrel[k].append(tempdict)

                    else:
                        recommend_skills.append(k.lower().strip())
                        for v1 in v:
                            tempdict = {}
                            tempdict['name'] = v1
                            if v1 in semanticterms:
                                tempdict['semanticTerms'] = semanticterms[v1]
                            else:
                                tempdict['semanticTerms'] = []
                            if v1 in allwordweight:
                                tempdict['weightage'] = allwordweight[v1]
                            else:
                                tempdict['weightage'] = 0
                            termsrel[k].append(tempdict)
                else:
                    if len(allphrases) > 1:

                        for v1 in v:
                            if v1 not in self.semantic_stopwords2:
                                tempdict={}
                                tempdict['name']=v1
                                tempdict['semanticTerms'] =[]
                                if v1 in allwordweight:
                                    tempdict['weightage']=allwordweight[v1]
                                else:
                                    tempdict['weightage']=0
                                termsrel[k].append(tempdict)
                    else:
                        for v1 in v:
                            tempdict={}
                            tempdict['name']=v1
                            tempdict['semanticTerms'] =[]
                            if v1 in allwordweight:
                                tempdict['weightage']=allwordweight[v1]
                            else:
                                tempdict['weightage']=0
                            termsrel[k].append(tempdict)
            li_temp=[]
            for e in exp_string:
                li_temp.append({"name":e+" | "+",".join(exp)})
            termsrel["experience"] = li_temp
            if ",".join(recommendqueryterms) in semanticterms:
                termsrel["recommendations"]=[mm[0] for mm in semanticterms[",".join(recommendqueryterms)][:5]]
            else:
                termsrel["recommendations"] = []

            termsrel = self.updateResult(termsrel)
            return termsrel
        except Exception as e:
            print("Semantic semantic error : ",str(e))
            raise Exception(str(e))

    def semanticJobSearch(self,chunks,numTerms=3):
        try:
            # st=time.time()

            queryterms, category, allphrases, allwordweight, exp_string, recommendqueryterms, exp = self.preprocessing(
                chunks)
            semanticterms = self.mayalsoknowobj.semanticSkillsJobSearch(queryterms, numTerms=numTerms)
            # st=time.time()

            termsrel = {}
            recommend_skills=[]
            for k,v in category.items():
                if k not in termsrel:
                    termsrel[k]=[]
                if  k=="role":
                    if len(allphrases) > 1:
                            recommend_skills.append(k.lower().strip())
                            for v1 in v:
                                try:
                                    self.semantic_stopwords2[v1]
                                except:
                                    tempdict={}
                                    tempdict['name']=v1
                                    if v1 in semanticterms:
                                        tempdict['semanticTerms']=semanticterms[v1]
                                    else:
                                        tempdict['semanticTerms'] =[]
                                    if v1 in allwordweight:
                                        tempdict['weightage']=allwordweight[v1]
                                    else:
                                        tempdict['weightage']=0
                                    termsrel[k].append(tempdict)

                    else:
                        recommend_skills.append(k.lower().strip())
                        for v1 in v:
                            tempdict = {}
                            tempdict['name'] = v1
                            if v1 in semanticterms:
                                tempdict['semanticTerms'] = semanticterms[v1]
                            else:
                                tempdict['semanticTerms'] = []
                            if v1 in allwordweight:
                                tempdict['weightage'] = allwordweight[v1]
                            else:
                                tempdict['weightage'] = 0
                            termsrel[k].append(tempdict)
                else:
                    if len(allphrases) > 1:
                        for v1 in v:
                            # if v1 not in self.semantic_stopwords2:
                            try:
                                self.semantic_stopwords2[v1]
                            except:
                                tempdict={}
                                tempdict['name']=v1
                                tempdict['semanticTerms'] =[]
                                if v1 in allwordweight:
                                    tempdict['weightage']=allwordweight[v1]
                                else:
                                    tempdict['weightage']=0
                                termsrel[k].append(tempdict)
                    else:
                        for v1 in v:
                            tempdict={}
                            tempdict['name']=v1
                            tempdict['semanticTerms'] =[]
                            if v1 in allwordweight:
                                tempdict['weightage']=allwordweight[v1]
                            else:
                                tempdict['weightage']=0
                            termsrel[k].append(tempdict)

            li_temp=[]
            for e in exp_string:
                li_temp.append({"name":e+" | "+",".join(exp)})
            termsrel["experience"] = li_temp
            if ",".join(recommendqueryterms) in semanticterms:
                termsrel["recommendations"]=[mm[0] for mm in semanticterms[",".join(recommendqueryterms)][:5]]
            else:
                termsrel["recommendations"] = []

            termsrel = self.updateResult(termsrel)
            # print("job response time: ",time.time()-st)

            return termsrel
        except Exception as e:
            print("Semantic semantic error : ",str  (e))
            raise Exception(str(e))


if __name__=='__main__':
    obj=Semantic()
    # import time
    # starttime=time.time()
    # print (obj.semanticJobSearch("alzheimer's care"))
    print (obj.semanticJobSearch("project manager"))
    # print (obj.semantic("painter with atmost 3.9 year of experience in scenary /painting"))
    # print (time.time()-starttime)