import os,json




def reinitialize():
    try:
        #########remove and company names
        with open(os.path.join("data","company", "company_add"), encoding="utf8") as f:
            company_add = list(f.readlines())

        with open(os.path.join("data", "company","company_remove"), encoding="utf8") as f:
            company_remove = list(f.readlines())

        with open(os.path.join("data", "company","company_names")) as f:
            company_names = json.load(f)
        company_add = [i.replace(r"\n", "").strip().lower() for i in company_add]
        company_remove = [i.replace(r"\n", "").strip().lower() for i in company_remove]

        company_names.extend(company_add)
        company_names = list(set(company_names) - set(company_remove))
        with open(os.path.join("data", "company","company_names"), "w") as f:
            json.dump(company_names, f)



    except Exception as e:
        raise Exception("Failed to remove and add company names: " + str(e))

    try:
        #########remove and company names
        with open(os.path.join("data","role", "role_add"), encoding="utf8") as f:
            role_add = list(f.readlines())

        with open(os.path.join("data","role", "role_remove"), encoding="utf8") as f:
            role_remove = list(f.readlines())

        with open(os.path.join("data","role", "role_data")) as f:
            role_data = json.load(f)

        role_add = [i.replace(r"\n", "").strip().lower() for i in role_add]
        role_remove = [i.replace(r"\n", "").strip().lower() for i in role_remove]

        role_data.extend(role_add)
        role_data = list(set(role_data) - set(role_remove))

        with open(os.path.join("data", "role","role_data"), "w") as f:
            json.dump(role_data, f)
    except Exception as e:
        raise Exception("Failed to remove and add role names: " + str(e))

    try:
        #########remove and company names
        with open(os.path.join("data","skills", "skill_add"), encoding="utf8") as f:
            skill_add = list(f.readlines())

        with open(os.path.join("data","skills", "skill_remove"), encoding="utf8") as f:
            skill_remove = list(f.readlines())

        with open(os.path.join("data","skills", "skills_data_mayalsoknow")) as f:
            skill_data = json.load(f)

        skill_add = [i.replace(r"\n", "").strip().lower() for i in skill_add]
        skill_remove = [i.replace(r"\n", "").strip().lower() for i in skill_remove]

        skill_data.extend(skill_add)
        skill_data = list(set(skill_data) - set(skill_remove))

        with open(os.path.join("data", "skills","skills_data_mayalsoknow"), "w") as f:
            json.dump(skill_data, f)
    except Exception as e:
        raise Exception("Failed to remove and add skills data: " + str(e))

