# adSeparator.py reads advertasement dataset from each year (default 2006-2010).
# Python program to read
# json file
import json 
import re

class FileObjects:
    def __init__(self):
        self.f_nr = open("nr-by-occupation-10.txt","w",encoding="utf8") #0-07 size: 22.8kB
        self.f_tx = open("text-by-occupation-10.txt","w",encoding="utf8") #06-07 size: 39.1MB
        self.f_hd = open("head-by-occupation-10.txt","w",encoding="utf8") #06-07 size: 976kB
    
    def write_to_file(self, occ_mer):
        
        nr_of_occ = len(occ_mer.text_by_occupation)
        print("Number of occupations:" + str(nr_of_occ))
        occ_nr = 0
        for occ in occ_mer.text_by_occupation:
            if (occ_nr % 100 == 0):
                print("Writing occ nr: " + str(occ_nr))
            self.f_nr.write(str(occ)+ ":" + str(occ_mer.nr_by_occupation.get(occ)) + "\n")
            self.f_hd.write(str(occ)+ ":" + str(occ_mer.head_by_occupation.get(occ))+ "\n")
            self.f_tx.write(str(occ)+ ":" + str(occ_mer.text_by_occupation.get(occ))+ "\n")    
            occ_nr +=1 
        print("Number of total occupations: " + str(occ_nr))     
          
class AdvStructure():
    def return_next_level(self,attr_level, level=0):
        level += 1
        for attribute in attr_level:
            if type(attr_level.get(attribute)) == dict:
                print(str("  "*level) + 'L' + str(level) + " " + str(attribute))   
                self.return_next_level(attr_level.get(attribute), level)
            else: 
                print(str("  "*level)+ 'L' + str(level) + " " + str(attribute) + ": " + str(attr_level.get(attribute)))
        return

    def print_adv_structure(self,adv):
        for attribute in adv: 
            level = 0
            if type(adv.get(attribute)) == dict: 
                print('L' + str(level) + " " + str(attribute))
                self.return_next_level(adv.get(attribute),0)
            else:
                print('L' + str(level) + " " + str(attribute) + ": " + str(adv.get(attribute)))


class OccupationMerge():
    def __init__(self):
        self.nr_by_occupation = {}
        self.text_by_occupation = {}
        self.head_by_occupation = {}
        self.merge_dicts = [self.nr_by_occupation, self.text_by_occupation,self.head_by_occupation]
    
    def add_advertisement(self,label,text,head):
        if label in self.nr_by_occupation:
            #Add nr, text and headline to stored label 
            stored_nr = self.nr_by_occupation.get(label)
            stored_text = self.text_by_occupation.get(label)
            stored_head = self.head_by_occupation.get(label)
            self.nr_by_occupation[label] = stored_nr+1
            self.text_by_occupation[label] = stored_text + "{" + text + "}" 
            self.head_by_occupation[label] = stored_head + "{" + head + "}"    
        else:
            #Initiating new occupation label
            self.nr_by_occupation[label] = 1
            self.text_by_occupation[label] = "{" + text + "}"
            self.head_by_occupation[label] = "{" + head + "}"
               

def seperate_by_occupation(occ_mer,adv):
    valid = True 
    occ_label = adv["occupation"]["label"]
    des_text = adv["description"]["text"]
    headline = adv["headline"]
    if occ_label == None or (des_text == None) or (headline == None):
        valid = False 
    else:

        occ_mer.add_advertisement(occ_label, des_text, headline)
    return valid 
    
  
def iterate_adv_set(occ_sep,adv_total,adv_set): 
    valid_nr = 0
    adv_nr = 1
    adv_limit = len(adv_set)
    for adv in adv_set:
        if (adv_nr % 40000 == 0):
            print("Iterating ad nr: " + str(adv_nr))
        adv_nr +=1
        valid = seperate_by_occupation(occ_sep,adv)
        if valid:
            valid_nr +=1 
        if adv_nr > adv_limit:
            break
    return valid_nr


def main():
    adv_str = AdvStructure() 
    occ_mer = OccupationMerge()
    f_o = FileObjects()
    valid_nr = 0 #Initiating 
    for year in range(2010,2011):
        f = open(str(year)+'.json')
        adv_set = json.load(f)
        adv_total = len(adv_set)
        #adv_str.print_adv_structure(adv_set[5])
        print("Advertisement dataset from year " + str(year)+ ":")
        print("Number of ads: " + str(adv_total))  
        valid_nr = iterate_adv_set(occ_mer, adv_total, adv_set) 
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(adv_total-valid_nr))
        f.close()
    f_o.write_to_file(occ_mer)
    print("End") 
main()
