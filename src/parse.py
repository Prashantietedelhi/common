import re, os,json
import string
import configparser
from nltk.stem.wordnet import WordNetLemmatizer


config_obj = configparser.ConfigParser()
config_file_loc = "../../config/config.cfg"

if not os.path.isfile(config_file_loc):
    config_file_loc = "../config/config.cfg"
config_obj.read(config_file_loc)
try:
    debugLevel = int(config_obj.get("Parse", "debuglevel"))
    logfilenameobj = config_obj.get("Parse", "logfilename")
    synonymsfilepath = (config_obj.get("MayAlsoKnow", "synonymsfilepath"))

except Exception as e:
    raise Exception("Config file error " + str(config_file_loc))


class Parse():
    def __init__(self):
        self.printable = set(string.printable)
        self.lmtzr = WordNetLemmatizer()
        try:
            with open(
                    os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "synonyms",synonymsfilepath)) as fileobj:
                self.dict_synonyms = json.load(fileobj)
        except Exception as e:
            print("Parse __init__ error: Failed to read the file: " + str(e))
            raise Exception("Parse: Failed to read the file: " + str(e))

    def parse(self, source):
        '''
        '''
        self.source = source
        replaceWord = {"+": " plus ", "#": " sharp ", ".": " dot ", "'s": 's',"&":" and "}

        for k, v in replaceWord.items():
            self.source = self.source.replace(k, v).strip()

        ########remove unicodes and non printable characters
        self.source = re.sub(r'[^\x00-\x7F]', ' ', self.source)
        ######## removing all non printable characters
        self.source = ''.join(filter(lambda x: x in self.printable, self.source))
        ####### remove white space from the beginning of the line
        # self.source = re.sub(r'^( +)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ####### remove lines containing number followed by dot(.) that appearing in the text
        # self.source = re.sub(r'(^\s*\d+.\r*\n)|^( +)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ###### removing one or more whitespaces from the begining and end of each line
        # self.source = re.sub(r'(^( +)|( +)$)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ###### removing all jpeg embedded in document
        # self.source = re.sub(r'((\!\[\]\(data:image\/).*\r*\n)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ###### remove any blank images embedded in document
        # self.source = re.sub(r'((\!\[\]\(data:\)))', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ###### remove starting digits and '#' symbols
        # self.source = re.sub(r'(^\s*[^a-zA-Z]+\s*)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ###### remove one or more whitespaces from the beginning and end of each line
        # self.source = re.sub(r'(^( +)|( +)$)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ###### remove multiple new lines
        # self.source = re.sub(r'(\n+)', r'\n', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ############ remove whitespace with single space
        # self.source = re.sub(' +', ' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        ######## remove line containg numbers followed by dot(.)
        self.source = re.sub(r'(^\s*)(\d+.)(\r*\n)', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'&#x22;', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'x22;', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'&#x22;', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'&#x27;', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'x27;', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'\\\\', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(r'//', r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)

        junk_list = ['xa4', 'xa4', 'xa7', 'xe6', 'xa9', 'xa6', 'xa8', 'u201a', 'u02dc', 'xbf', 'xba', 'u02dc', 'u2014',
                     'u2026', 'u2020', 'xbc', 'xef', 'u2022', 'u2122', 'xe5', 'xbd', 'x9d', 'xe7', 'xe2', 'xb8', 'xe8',
                     'u017d', 'xb4', 'xae', 'x90', 'xbb', 'xa5', 'u0192', 'xa0', 'u2018', 'xe9', 'u201c', 'xb5',
                     'u2013', 'xb6', 'u203a', 'u20ac', 'xb7', 'u0153', 'xb0', 'u201e', 'xc3', 'xaf', 'xa1', 'xe4',
                     'xad', 'xa2', 'xc2', 'xb9', 'u2026 - ']
        for j in junk_list:
            self.source = re.sub(j, r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)
        self.source = re.sub(j, r' ', self.source, flags=re.IGNORECASE | re.MULTILINE)

        listofstop = [',', '-', '_', '/', '`', '~', '!', '@', '$', '%', '^', '&', '*', '(', ')', '=', '{', '}', '[',
                      ']', ';', ':', '"', '\'', '<', '>', '?', '/']
        for k in listofstop:
            self.source = self.source.replace(k, ' ').strip()
        self.source = re.sub(' +', ' ', self.source, flags=re.IGNORECASE | re.MULTILINE).strip()

        # newsource = []
        # for i in self.source.split():
        #     if len(i) > 3:
        #         newsource.append(self.lmtzr.lemmatize(i.strip()))
        #     else:
        #         newsource.append(i)
        #
        # self.source = " ".join(newsource)

        # try:
        #     self.source = self.dict_synonyms[self.source]
        # except:
        #     pass

        return self.source


    def replaceSynonyms(self, word):
        try:
            return self.dict_synonyms[word]
        except:
            return word

    def clean_string(self, input_string):
        try:
            input_string = input_string.lower()
            reg = re.compile("[\(\)\"\!\~\|\$\%\^\*\,\[\]<>]+")
            exp = re.findall(
                r'((\d+\.)?(\d+\s*?(-|–|to|\+)?\s*?(\d+)?(\.)?(\d+)?\s*?(yrs|yr|years|year))(\s+)?((of) (\s+)?(experiences|experience|exp))?(experiences|experience|exp)?)',
                input_string)
            exp = [e[0] for e in exp]
            new_exp = []
            for e in exp:
                input_string = input_string.replace(e, '')
                tmp = re.findall(r"((\d+\.)?(\d+))", e)
                for t in tmp:
                    new_exp.append(t[0])
            new_exp = list(set(new_exp))
            new_exp = [float(ne) for ne in new_exp]
            new_exp.sort()
            new_exp = [str(ne) for ne in new_exp]
            if len(exp):
                input_string = re.sub(r"\b%s\b" % "experiences", "", input_string)
                input_string = re.sub(r"\b%s\b" % "experience", "", input_string)
                input_string = re.sub(r"\b%s\b" % "exp", "", input_string)
            sure_chunks = re.findall(r'"([^"]*)"', input_string)
            sure_chunks = [w.strip() for w in sure_chunks if len(w.strip())]
            for sc in sure_chunks:
                try:
                    input_string = re.sub(r"%s" % ('"' + sc + '"'), "", input_string)
                except:
                    input_string = input_string.replace(sc,"")
            words = input_string
            words = reg.sub(" 1234 ", words)
            allwords = words.split("1234")
            allwords = [re.sub(' +', ' ', w, flags=re.IGNORECASE | re.MULTILINE).strip() for w in allwords if
                        len(w.strip())]
            allwords = list(set(allwords) - set(sure_chunks))
            return allwords, sure_chunks, new_exp, exp
        except Exception as e:
            print("Semantic clean_string error : ", str(e))
            raise Exception(str(e))


if __name__=='__main__':
    filepath = r"nlp"
    obj = Parse()
    print(obj.parse("2-d design"))
    # import time
    # st=time.time()
    # print(obj.parse("c++"))
    # print(time.time()-st)
    # st = time.time()
    # print(obj.parse("big-data"))
    # print(time.time() - st)


