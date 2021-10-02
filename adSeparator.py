# adSeparator.py reads advertasement dataset from each year (default 2006-2010).
import json

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
    
    def write_to_file(self):
        f1 = open("nr-by-occupation.txt","w") 
        f2 = open("text-by-occupation.txt","w")
        f3 = open("head-by-occupation.txt","w")
        for occ in self.text_by_occupation:
            f1.write(str(occ)+ " " + str(self.nr_by_occupation.get(occ)) + "\n")
            f2.write(str(occ)+ ":" + str(self.text_by_occupation.get(occ))+ "\n")
            f3.write(str(occ)+ " " + str(self.head_by_occupation.get(occ))+ "\n")
               

def seperate_by_occupation(occ_mer,adv):
    valid = True 
    occ_label = adv["occupation"]["label"]
    des_text = adv["description"]["text"]
    headline = adv["headline"]
    if occ_label == None or (des_text == None):
        valid = False 
    else:
        occ_mer.add_advertisement(occ_label, des_text, headline)
    return valid 
    
  
def iterate_adv_set(occ_sep,adv_set): 
    valid_nr = 0
    adv_nr = 1
    adv_limit = 20
    
    for adv in adv_set:
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
    valid_nr = 0 #Initiating 
    for year in range(2006,2007):
        f = open(str(year)+'.json',)
        adv_set = json.load(f)
        adv_total = len(adv_set)
        #adv_str.print_adv_structure(adv_set[5]) #IS NOT CORRECT 
        valid_nr = iterate_adv_set(occ_mer, adv_set) 
        print("Advertisement set from year " + str(year)+ ":")
        print("Number of adds: " + str(adv_total))
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(adv_total-valid_nr))
        f.close()
    
    occ_mer.write_to_file()
    print("End")
main()
