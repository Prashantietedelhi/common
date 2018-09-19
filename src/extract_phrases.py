# import semantic
import string
from nltk.corpus import stopwords
stopw = list(set(stopwords.words('english')))
stopw.extend(list(set(string.punctuation)))
from phrasehandlingv3 import PhraseHandling
phraseobj=PhraseHandling()
import json
data=json.load(open("MongoRelatedData"))
# sem_obj = semantic.Semantic()
words=[]
for ii,dd in enumerate(data):
    # print(ii, len(data))
    # print(d)
    # if d=="associate consultant":
    #     print(1)
    allwords = []
    for d in dd:
            print(d)
        # try:
            pgr = phraseobj.phrases(d)
            pgr = list(set(pgr)-set(stopw))
            # semanticwords = sem_obj.semanticJobSearch(d, 0)
            #
            # for k, v in semanticwords.items():
            #     for l in v:
            #         if type(l)==dict:
            #             if "name" in l:
            if len(pgr)>0:
                allwords.extend(pgr)
        # except:
        #     pass

    allwords = list(set(allwords))
    if len(allwords)>0:
        words.append(allwords)
    # print(allwords)
with open("MongoRelatedData_words2","w") as f:
    json.dump(words,f)


