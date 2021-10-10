import json
#import spacy_udpipe

class POS:
    def __init__(self):
        #spacy_udpipe.download("sv") # download Swedish model
        #self.nlp = spacy_udpipe.load("sv")
        pass

class MANUAL_POS:
    def __init__(self,text,lem,pos,dep):
        self.text = text
        self.lemma_ = lem
        self.pos_ = pos
        self.dep_ = dep

class OccupationMerge:
    def __init__(self):
        self.nr_by_occupation = {}
        self.description_by_occupation = {}
        self.head_by_occupation = {}

class GenderClass:
    def __init__(self,gender):
        self.gender = gender
        self.total_nr = 0
        self.lemmas = {}
    
class NaiveBayes:
    def __init__(self):
        self.class_list = []
        self.N = 0
        
    def createClass(self,gC):
        self.class_list.append(gC)
        self.P_c = 1/len(self.class_list)
        print("Adding " + str(gC.gender) + " Class with size of: " + str(len(gC.lemmas) + " lemmas."))
        self.N += gC.total_nr

    def classify(self,term):
        print("Total number of lemmas for both classes: " + str(self.N))
        term_freq = 0
        
        class1 = self.class_list[0] #Men class
        class2 = self.class_list[1] #Women class 
        for CL in self.class_list:
            try:
                term_freq += CL.lemmas[term]
            except:
                continue
        print("Total number of the term for both classes:" + str(term_freq))
        P_t = term_freq/self.N   
        
        if P_t == 0:
            print("The term can't be found in any class.")
            return None, None 
        
        else:  
            if term not in class1.lemmas:
                P_c1_t =  0
                c1_term_freq = 0
            else:
                c1_term_freq = class1.lemmas[term]  
                P_t_c1 = c1_term_freq/class1.total_nr
                P_c1_t = (P_t_c1*self.P_c) / P_t
                print("Term frequency in men: " + str(c1_term_freq))
        
            if term not in class2.lemmas:
                P_c2_t =  0
                c2_term_freq = 0
            else:
                c2_term_freq = class2.lemmas[term]  
                P_t_c2 = c2_term_freq/class2.total_nr
                P_c2_t = (P_t_c2*self.P_c) / P_t
                print("Term frequency in " + str(class2.gender) +" :" + str(c2_term_freq))
        return P_c1_t, P_c2_t

        

def extract_word_classes(token,gC,limit):
    #token.text, token.lemma_, token.pos_, token.dep_
    if (token.pos_ == "NOUN") or (token.pos_ == "ADJ") or (token.pos_ == "ADV") or ((token.pos_ == "VERB")):
        gC.total_nr +=1
        if token.lemma_ not in gC.lemmas:
            gC.lemmas[token.lemma_] = 1
          
        else: 
            gC.lemmas[token.lemma_] += 1  
        

def POS_all_ads(pos, occ,gC,limit):
    for term in occ.description_by_occupation: 
        des_list = occ.description_by_occupation.get(term)
        head_list = occ.head_by_occupation.get(term)
        for des in des_list:
            des_doc = pos.nlp(des)
            for token in des_doc:
                if limit != None:
                    if gC.total_nr > limit:
                        return
                    else:
                        extract_word_classes = (token,gC,limit) 
        

    def add_ad_data(self,label,text,head):
        if label in self.nr_by_occupation:
            #Add nr, text and headline to stored label  
            stored_nr = self.nr_by_occupation.get(label)
            self.nr_by_occupation[label] = stored_nr+1
            self.description_by_occupation[label].append(text)
            self.head_by_occupation[label].append(head)  
            #print("stored label: " + str(label))
            #print("stored text: " + str(self.description_by_occupation[label]))    
        else:
            #Initiating new occupation label
            self.nr_by_occupation[label] = 1
            self.description_by_occupation[label] = []
            self.description_by_occupation[label].append(text)
            self.head_by_occupation[label] = []
            self.head_by_occupation[label].append(head)
            #print("new label:" + str(label))
            #print("new description: " + str(self.description_by_occupation[label]))

def find_gender_occupation(occ,adv,classified_occupations):
    valid = True 
    occ_label = adv["occupation"]["label"]
    if occ_label in classified_occupations:
        des_text = adv["description"]["text"]
        headline = adv["headline"]
        if occ_label == None or (des_text == None) or (headline == None):
            valid = False 
        else:
            des_text = des_text.strip('\n\r')
            des_text = des_text.strip(' \r ')
            occ.add_ad_data(occ_label, des_text, headline.strip('\n').strip('\r'))
    else:
        valid = False
    return valid 

def iterate_ad_set(occ_sep,ad_set,classified_occupations): 
    valid_nr = 0
    adv_nr = 1
    adv_limit = len(ad_set)
    for adv in ad_set:
        if (adv_nr % 40000 == 0):
            print("Iterating ad nr: " + str(adv_nr))
        adv_nr +=1
        valid = find_gender_occupation(occ_sep,adv,classified_occupations)
        if valid:
            valid_nr +=1 
        if adv_nr > adv_limit:
            break
    return valid_nr

def collect_all_ads(occ, classified_occupations):
    for year in range(2007,2008):
        print("Advertisement dataset from year " + str(year)+ ":")  
        f = open(str(year)+'.json')
        ad_set = json.load(f)
        adv_total = len(ad_set)   
        valid_nr = iterate_ad_set(occ, ad_set, classified_occupations) 
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(adv_total-valid_nr))
        f.close()
    for o in occ.description_by_occupation:
        print(o)
        print(occ.description_by_occupation.get(o))

def read_classified_occupations(gender):
    if gender == "Men":
        f = open("men-ad-occupations.txt", "r", encoding = "utf-8")
    if gender == "Women":
        f = open("women-ad-occupations.txt", "r", encoding = "utf-8")
    
    classified_occupations = {}
    for ad in f:
        classified_occupations[ad.strip("\n")] = True
    return classified_occupations

def MANUAL_read_POS(gC,gender):
    if gender == "Women":
        f = open("womentaggedtext.txt", "r", encoding = "utf-8")
    if gender == "Men":
        f = open("mentaggedtext.txt", "r", encoding = "utf-8")
    for row in f: 
        term = row.split(" ")
        token = MANUAL_POS(term[0],term[1],term[2],term[3].strip('\n'))
        extract_word_classes(token,gC)

   
def main():
    g_list = ["Men", "Women"]
    nB = NaiveBayes()
    #pos = POS()
    limit = None 
    for gender in g_list:
        occ = OccupationMerge()
        gC = GenderClass(gender)
        #classified_occupations = read_classified_occupations(occ, gender) #no men-file 
        #collect_all_ads(occ, classified_occupations)
        #POS_all_ads(pos,occ,gC,limit)
        MANUAL_read_POS(gC,gender)
        nB.createClass(gC)
        limit = gC.total_nr
        iteration +=1 

    while True:
        print("Type input text:") 
        inp = input()
        terms  = inp.split()
        for term in terms:
            pos_list = pos.nlp(term)
            term = pos_list[0].lemma
            #term = "söker"
            try: 
                P_1, P_2 = nB.classify(term.lower())
            except: 
                print("ERROR.")
            if (P_1 and P_2) == None: 
                print("The term '" +str(term) + "' cannot be classified.")
            elif P_1 > P_2: 
                print(str(term) + " = MEN  ")
            else:
                print(str(term) + " = WOMEN  ")
            print("P(Men I " + str(term) + ") = " + str(P_1) + "   -   P(Women I " + str(term) + ") = " + str(P_2))
    


    
    



main()

