# adSeparator.py reads advertasement dataset from each year (default 2006-2010).
import json

class AdvStructure():
    def return_next_level(self,attr_level, level):
        level += 1
        #print("In recursive function")
        for attribute in attr_level:
            if type(attr_level.get(attribute)) == dict:
                print('L' + str(level) + " " + str(attribute))      
                self.return_next_level(attr_level.get(attribute), level)
            else:
                #print("Out of recursive") 
                print('L' + str(level) + " " + str(attribute) + ": " + str(attr_level.get(attribute)))
        return

    def print_structure(self,adv):
        for attribute in adv: 
            level = 0
            if type(adv.get(attribute)) == dict:
                #Has children attributes      
                print('L' + str(adv) + " " + str(attribute))
                self.return_next_level(adv.get(attribute),0)
            else:
                #No children attributes
                print('L' + str(level) + " " + str(attribute) + ": " + str(adv.get(attribute)))


class OccupationMerge():
    def __init__(self):
        self.nr_by_occupation = {}
        self.text_by_occupation = {}
    
    def add_advertisement(self,label,text):
        if label in self.nr_by_occupation:
            #Add text and nr to stored label 
            stored_nr = self.nr_by_occupation.get(label)
            stored_text = self.text_by_occupation.get(label)
            self.text_by_occupation[label] = stored_text + "{" + text + "}" 
            self.nr_by_occupation[label] = stored_nr+1     
        else:
            #Initiating new occupation label
            self.nr_by_occupation[label] = 1
            self.text_by_occupation[label] = "{" + text + "}"
    
    def write_to_file(self): 
            f1 = open("text-by-occupation.txt","w")
            f2 = open("number-by-occupation.txt","w")
            for occ in self.text_by_occupation:
                f1.write(str(occ)+ ":" + str(self.text_by_occupation.get(occ))+ "\n")
                f2.write(str(occ)+ " " + str(self.nr_by_occupation.get(occ)) + "\n")

def seperate_by_occupation(occ_sep,adv):
    valid = True  
    for attr in adv:
        if attr == "occupation":
                occ_dic = adv.get(attr)
                text = adv["description"]["text"]
                if occ_dic.get("label") == None or (text == None):
                    valid = False
                else:
                    occ_sep.add_advertisement(occ_dic.get("label"), text)
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
    occ_sep = OccupationMerge()
    valid_nr = 0 
    for year in range(2006,2007):
        f = open(str(year)+'.json',)
        adv_set = json.load(f)
        adv_total = len(adv_set)
        #adv_str.print_structure(adv_set[3]) #IS NOT CORRECT 
        valid_nr = iterate_adv_set(occ_sep, adv_set) 
        print("Advertisement set from year " + str(year)+ ":")
        print("Number of adds: " + str(adv_total))
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(adv_total-valid_nr))
        f.close()
    
    occ_sep.write_to_file()
    print("End")
main()
