import re,time
from nltk import ngrams
from nltk import word_tokenize
import sys
sys.path.insert(0, "../")
import configparser
import json,os
from nltk.corpus import stopwords
from loggingmodule import getlogger
from gensim.models import Phrases

from nltk.stem.wordnet import WordNetLemmatizer
import parse
import string,ast
from keras.preprocessing.text import text_to_word_sequence

####################### Confi file reading
config_obj = configparser.ConfigParser()
config_file_loc = "../../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../config/config.cfg"
config_obj.read(config_file_loc)
try:
    debugLevel = int(config_obj.get("MonsterPhraseHandling","debuglevel"))
    logfilenameobj = config_obj.get("MonsterPhraseHandling","logfilename")
except Exception as e:
    raise Exception("Config file error "+str(config_file_loc))


####################### Loggin Functionality
logfilename="../../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../logs/"
logfilename=logfilename+logfilenameobj

try:
    logger = getlogger.GetLogger("MonsterPhraseHandling",logfilename,debugLevel)
    logger = logger.getlogger1()
except Exception as e:
    raise Exception(e)


logger.info("Phrase Handling Module Called")
class PhraseHandling():
    def __init__(self):
            try:
                starttime = time.time()
                self.stopwords=list(set(stopwords.words('english')))
                self.stopwords.extend(list(set(string.punctuation)))
                self.lmtzr = WordNetLemmatizer()
                if not os.path.isfile(os.path.join("data", "PhraseData","PhrasesDictData")):
                    self.dictdata = {}
                    fileList=[os.path.join("data","education","edu_level_data"),
                              os.path.join("data", "education", "edu_streams_data"),
                            ]
                    data=[]

                    for file in fileList:
                        data.extend(self.read_file(file))
                    data = list(set(data))

                    # phrasedata = self.read_file(os.path.join("data","PhraseData","PhrasesData"))

                    phrase_remove = self.read_file(os.path.join("data","PhraseData","phrase_remove"))

                    # data.extend(phrasedata)

                    data = [i.replace(r"\n", "").strip().lower() for i in data]

                    for d in data:
                        d = re.sub(' +',' ',d,flags=re.IGNORECASE|re.MULTILINE).strip()
                        if d not in phrase_remove:
                            d = re.sub(' +', ' ', d, flags=re.IGNORECASE | re.MULTILINE)
                            if d.strip() not in phrase_remove:
                                n = len(d.split())
                                for i in range(1, n + 1):
                                    sixgrams = ngrams(d.split(), i)
                                    for grams in sixgrams:
                                        grams = " ".join(grams)
                                        if grams not in self.stopwords:
                                            self.dictdata[grams.strip().replace(" ","")] = 1

                    data=[]

                    fileList2 = [
                                os.path.join("data", "locations", "locations_all"),
                                os.path.join("data","PhraseData","itskills_phrase_training_data"),
                                 os.path.join("data", "PhraseData", "Phrase_retrain_data"),
                                 os.path.join("data", "skills", "skills_data_mayalsoknow"),
                                 # os.path.join("data", "skills", "linkdinskills"),
                                 os.path.join("data", "PhraseData", "linkedin_skills"),
                                 os.path.join("data", "PhraseData", "All_sure_chunks_mongodb"),
                                 os.path.join("data", "company", "company_names"),
                                 os.path.join("data", "role", "role_data"),
                                 os.path.join("data", "PhraseData", "phrase_train_data_bigram"),
                                 os.path.join("data", "PhraseData", "phrase_train_data_trigram"),
                                 os.path.join("data", "PhraseData", "phrase_train_data_fourgram"),
                                 os.path.join("data", "PhraseData", "phrase_train_data_fivegram"),
                                 os.path.join("data", "PhraseData", "phrase_train_data_sixgram"),
                                 os.path.join("data", "PhraseData", "PhrasesData"),
                                 os.path.join("data", "industry", "indsutry_list")

                                 ]

                    for file in fileList2:
                        data.extend(self.read_file(file))


                    # data = [i.replace(r"\n", "").strip().lower() for i in data]
                    data = list(set(data))
                    for d in data:
                        if d not in phrase_remove:
                            d = re.sub(' +', ' ', d, flags=re.IGNORECASE | re.MULTILINE)
                            if d not in phrase_remove:
                                if d not in self.stopwords:
                                    self.dictdata[d.strip().replace(" ","")] = 1
                    with open(os.path.join("data", "PhraseData","PhrasesDictData"),"w") as f:
                        json.dump(self.dictdata,f)
                else:
                    self.dictdata = json.load(open(os.path.join("data", "PhraseData","PhrasesDictData")))
                print("phrasehandling initialization time : " ,time.time()-starttime)

            except Exception as e:
                print("PhraseHandling __init__ error : ", str(e))
                logger.error("PhraseHandling __init__ error : ", str(e))

                raise Exception("Error Creating object PhraseHandling: " + str(e))


    def read_file(self,filename):
        fileData = []
        try:
            with open(filename, encoding="utf8") as fileObj:
                fileData = list(set(json.load(fileObj)))
        except:
            try:
                with open(filename, encoding="utf8") as fileObj:
                    fileData = ast.literal_eval(fileObj.read())
            except:
                    try:
                        with open(filename, encoding="utf8") as fileObj:
                            fileData = list(fileObj.readlines())
                    except Exception as e:
                        print("PhraseHandling read_file error: failed to read file :" \
                              + str(filename) + " error:" + str(e))
                        logger.error("PhraseHandling read_file error: failed to read file :"\
                                     + str(filename) + " error:" + str(
                                e))
                        raise Exception("PhraseHandling read_file error: failed to read file :" \
                                        + str(filename) + " error:" + str(e))
        fileData = [i.replace(r"\n", "").strip().lower() for i in fileData]
        return fileData

    def phrases(self, chunks):
        try:

            self.mappedterms={}
            n = 11
            allgrams = []
            allskills = []
            for i in range(1, n + 1):
                sixgrams = ngrams(chunks.split(), i)
                for grams in sixgrams:
                    grams = " ".join(grams)
                    try:
                        origgram=grams
                        self.dictdata[grams.replace(" ","")]
                        self.mappedterms[grams]=origgram
                        allgrams.append(grams)
                    except:
                        pass

            allgrams.sort(key=lambda x: len(word_tokenize(x)), reverse=True)

            chunks = re.sub(' +', ' ', chunks, flags=re.IGNORECASE | re.MULTILINE)
            for grams in allgrams:
                if len(chunks) > 0 and chunks != '':

                    if len(re.findall(r'\b%s\b' % grams, chunks)) > 0:
                        chunks = re.sub(r"\b%s\b" % grams, "", chunks)

                        grams = re.sub(' +', ' ', grams, flags=re.IGNORECASE | re.MULTILINE)
                        allskills.append(self.mappedterms[grams])
                        chunks = chunks.strip()

                else:
                    break
            if len(chunks) > 0 and chunks != '':
                chunks_not_found=word_tokenize(chunks)
                for word in chunks_not_found:
                    word = re.sub(' +', ' ', word, flags=re.IGNORECASE | re.MULTILINE)
                    allskills.append(word)
            allskills=list(set(allskills))
            return allskills
        except Exception as e:
            print("PhraseHandling phrases error : ",str(e))
            logger.error("phreasehandling: phrases function ERROR: "+str(e))
            raise Exception("phreasehandling: phrases function ERROR: "+str(e))

if __name__=='__main__':
    sent = "natural language processing"
    obj=PhraseHandling()

    print (obj.phrases(sent))