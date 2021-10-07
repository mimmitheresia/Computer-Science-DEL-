# Python program to read
# json file
import json 

class OccupationDict():
    def __init__(self):
        self.occupation_frequency = {}

    
    def add_label(self,label):
        if label in self.occupation_frequency:
            #Add nr to stored label 
            stored_nr = self.occupation_frequency.get(label)
            self.occupation_frequency[label] = stored_nr+1
        else:
            #Initiating new occupation label
            self.occupation_frequency[label] = 1

class TextFile:
    def __init__(self):
        self.f_nr = open("2006-2011-occupation-frequency.txt","w",encoding="utf8") #0-07 size: 22.8kB 
    
    def write_to_file(self, occ):
        print("Writing each occupation to 2006-2011-occupation-frequency.txt.")
        nr_of_occ = len(occ.occupation_frequency)
        print("Number of unique occupations in total data set:" + str(nr_of_occ))
        term_nr = 0
        for term in occ.occupation_frequency:
            if (term_nr % 100 == 0):
                print("Writing occ nr: " + str(term_nr))
            self.f_nr.write(str(term)+ ":" + str(occ.occupation_frequency.get(term)) + "\n")
            term_nr +=1 
        print("Number of total occupations: " + str(term_nr))     
          


def return_next_level(self,attr_level, level=0):
    level += 1
    for attribute in attr_level:
        if type(attr_level.get(attribute)) == dict:
            print(str("  "*level) + 'L' + str(level) + " " + str(attribute))   
            return_next_level(attr_level.get(attribute), level)
        else: 
            print(str("  "*level)+ 'L' + str(level) + " " + str(attribute) + ": " + str(attr_level.get(attribute)))
    return

def print_ad_object(ad):
    for attribute in ad: 
        level = 0
        if type(ad.get(attribute)) == dict: 
            print('L' + str(level) + " " + str(attribute))
            return_next_level(ad.get(attribute),0)
        else:
            print('L' + str(level) + " " + str(attribute) + ": " + str(ad.get(attribute)))

def sort_popular_occ(occ):
    #Sort popular occupations in descending order
    print("Top 50 popular occupations in total advertisement set (2006-2010)")
    print("#Occupation  #Nr of advertisements")
    popular_occupations = {}
    it = len(occ.nr_by_occupation)
    for i in range(1,101):
        current_value = 0
        current_occ = None 
        for occ in occ.nr_by_occupation:
            occ_nr = occ.nr_by_occupation.get(occ)
            if occ_nr > current_value:
                if occ not in popular_occupations: 
                    current_value = occ_nr
                    current_occ = occ
        highest_value = current_value
        highest_occ = current_occ
        popular_occupations[highest_occ] = True
        print(str(i) + ". " + str(highest_occ) + " " + str(highest_value))



def seperate_by_occupation(occ,object):
    valid = True 
    occ_label = object["occupation"]["label"]
    des_text = object["description"]["text"]
    headline = object["headline"]
    if occ_label == None or (des_text == None) or (headline == None):
        valid = False 
    else:

        occ.add_label(occ_label)
    return valid 
    
  
def iterate_adv_set(occ,ad_set): 
    valid_nr = 0
    ad_nr = 1
    ad_limit = len(ad_set)
    for object in ad_set:
        if (ad_nr % 40000 == 0):
            print("Iterating ad nr: " + str(ad_nr))
        ad_nr +=1
        valid = seperate_by_occupation(occ,object)
        if valid:
            valid_nr +=1 
        if ad_nr > ad_limit:
            break
    return valid_nr


def main(): 
    occ = OccupationDict()
    f_o = TextFile()
    valid_nr = 0 #Initiating 
    for year in range(2006,2011):
        f = open(str(year)+'.json')
        ad_set = json.load(f)
        ad_total = len(ad_set)
        #print_ad_object(ad_set[5])
        print("Advertisement dataset from year " + str(year)+ ":")
        print("Number of ads: " + str(ad_total))  
        valid_nr = iterate_adv_set(occ, ad_set) 
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(ad_total-valid_nr))
        f.close()
    #f_o.write_to_file(occ)
    sort_popular_occ(occ)
    print("End") 
main()
