import os,json,ast,re


def read_file( filename):
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
                raise Exception("PhraseHandling read_file error: failed to read file :" \
                                + str(filename) + " error:" + str(e))
    fileData = [i.replace(r"\n", "").strip().lower() for i in fileData]
    return fileData
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
data=[]
newd=[]
for file in fileList2:
    data.extend(read_file(file))

data = [i.replace(r"\n", "").strip().lower() for i in data]
for d in data:
    d = re.sub(' +', ' ', d, flags=re.IGNORECASE | re.MULTILINE)
    newd.append(d)

print(len(newd))
print(len(list(set(newd))))
with open("AllPhrases","w") as f:
    json.dump(newd,f)