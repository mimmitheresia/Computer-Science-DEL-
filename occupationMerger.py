import json

class OccupationMerge():
    def __init__(self):
        self.nr_by_occupation = {}
        self.text_by_occupation = {}
        self.head_by_occupation = {}


    def add_advertisement(self,label,text,head):
        if label in self.nr_by_occupation:
            #Add nr, text and headline to stored label 
            stored_nr = self.nr_by_occupation.get(label)
            stored_text = self.text_by_occupation.get(label)
            stored_head = self.head_by_occupation.get(label)
            self.nr_by_occupation[label] = stored_nr+1
            self.text_by_occupation[label] = stored_text + "{" + text + "}\n" 
            self.head_by_occupation[label] = stored_head + "{" + head + "}\n"    
        else:
            #Initiating new occupation label
            self.nr_by_occupation[label] = 1
            self.text_by_occupation[label] = "{" + text + "}\n"
            self.head_by_occupation[label] = "{" + head + "}\n"

def seperate_by_occupation(occ,adv,classified_occupations):
    valid = True 
    occ_label = adv["occupation"]["label"]
    if occ_label in classified_occupations:
        des_text = adv["description"]["text"]
        headline = adv["headline"]
        if occ_label == None or (des_text == None) or (headline == None):
            valid = False 
        else:
            occ.add_advertisement(occ_label, des_text.strip(), headline.strip())
    else:
        valid = False
    return valid 

def iterate_adv_set(occ_sep,adv_set,classified_occupations): 
    valid_nr = 0
    adv_nr = 1
    adv_limit = len(adv_set)
    for adv in adv_set:
        if (adv_nr % 40000 == 0):
            print("Iterating ad nr: " + str(adv_nr))
        adv_nr +=1
        valid = seperate_by_occupation(occ_sep,adv,classified_occupations)
        if valid:
            valid_nr +=1 
        if adv_nr > adv_limit:
            break
    return valid_nr

def read_all_ads(occ, classified_occupations):
    for year in range(2007,2008):
        print("Advertisement dataset from year " + str(year)+ ":")  
        f = open(str(year)+'.json')
        adv_set = json.load(f)
        adv_total = len(adv_set)   
        valid_nr = iterate_adv_set(occ, adv_set, classified_occupations) 
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(adv_total-valid_nr))
        f.close()
    for o in occ.text_by_occupation:
        print(o)
        print(occ.text_by_occupation.get(o))

def read_gender_occupations(occ, gender):
    if gender == "Men":
        f = open("men-ad-occupations.txt", "r", encoding = "utf-8")
    if gender == "Women":
        f = open("women-ad-occupations.txt", "r", encoding = "utf-8")
    
    classified_occupations = {}
    for ad in f:
        classified_occupations[ad.strip("\n")] = True
    read_all_ads(occ, classified_occupations)

def main():
    occ = OccupationMerge()
    gender = "Men"
    read_gender_occupations(occ, gender) #no men-file 


main()

