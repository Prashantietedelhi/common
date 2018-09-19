import json
# data={}
# data["vp"]={}
# data["vp"]["vice principle"]=1
# data["vp"]["vice president"]=1
# data["vp"]["general manager"]=1
#
#
# data["vp"]["president"]=1
# data["vp"]["president"]=1
# data["vp"]["president"]=1
# data["vp"]["president"]=1
#

data = ["chief,head,vp,avp,director,svp,president,vice president",
"associate,assistant,junior,associates,Jr dot,jr",
"senior,lead,Supervisor,Sr dot,sr",
"Trainee,fresher,intern,entry level",
"Specialist,expert,Professional",
"Consultant,advisor,counsellor,adviser",
"vice principal,faculty,professor,dean,hod,lecturer",
        "instructor,teacher,tutor,guide,counsellor,lecturer"
        ]


newrel={}
allwords=[]
for d in data:
    alld=d.split(",")
    alld=[i.lower().strip() for i in alld if i.strip()!="" and len(i.strip())>0]
    for i in alld:
        ii=i#.replace(" ","")
        # newrel={}
        newrel[ii]={}
        for j in alld:
            if i!=j:
                newrel[ii][j]=1
                allwords.append(j)

allwords=list(set(allwords))
allwords.append("vp")
with open("data/mayalsoknow/static_mayalsoknow","w") as f:
    json.dump(newrel,f)


with open("data/designation/designations","w") as f:
    json.dump(allwords,f)