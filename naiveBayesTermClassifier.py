import json
import spacy_udpipe
import re

class POS:
    def __init__(self):
        spacy_udpipe.download("sv") # download Swedish model
        self.nlp = spacy_udpipe.load("sv")
        #pass

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

class GenderClass:
    def __init__(self,gender): #print(token.text, token.lemma_, token.pos_, token.dep_)
        self.gender = gender
        self.total_nr = 0
        self.lemma_freq = {} #lemma_freq {lemma, {word_class1:freq, word_class2:freq}}
        self.word_class = {} #lemma_wordclass
        self.lemma_word = {} #lemma_word
        self.word_lemma = {} #word_lemma 
    
class NaiveBayes:
    def __init__(self):
        self.class_list = []
        self.N = 0
        
    def createClass(self,gC):
        self.class_list.append(gC)
        self.P_c = 1/len(self.class_list)
        #print("Adding " + str(gC.gender) + " Class with size of: " + str(gC.total_nr)+ " lemma_freq.")
        self.N += gC.total_nr

    def classify(self,term):
        term_freq = 0
        
        class1 = self.class_list[0] #Men class
        class2 = self.class_list[1] #Women class 
        for CL in self.class_list:
            try:
                term_freq += CL.lemma_freq[term]
            except:
                continue
        #print(" ")
        #print("Total number of the term for both classes:" + str(term_freq))
        P_t = term_freq/self.N   
        
        if P_t == 0:
            print("The term can't be found in any class.")
            return None, None 
        
        else:  
            if term not in class1.lemma_freq:
                P_c1_t =  0
                c1_term_freq = 0
            else:
                c1_term_freq = class1.lemma_freq[term]  
                P_t_c1 = c1_term_freq/class1.total_nr
                P_c1_t = (P_t_c1*self.P_c) / P_t
                #print("Term frequency in men: " + str(c1_term_freq))
        
            if term not in class2.lemma_freq:
                P_c2_t =  0
                c2_term_freq = 0
            else:
                c2_term_freq = class2.lemma_freq[term]  
                P_t_c2 = c2_term_freq/class2.total_nr
                P_c2_t = (P_t_c2*self.P_c) / P_t
                #print("Term frequency in " + str(class2.gender) +" :" + str(c2_term_freq))
        return P_c1_t, P_c2_t

        

def extract_word_classes(token,gC,limit,f):
    #print(token.text, token.lemma_, token.pos_, token.dep_)
    if (token.pos_ == "NOUN") or (token.pos_ == "ADJ") or (token.pos_ == "ADV") or ((token.pos_ == "VERB")):
        gC.total_nr +=1
        if token.lemma_ not in gC.lemma_freq:
            gC.lemma_freq[token.lemma_] = 1
            gC.word_class[token.lemma_] = token.pos_
            if f != None:
                f.write(str(token.text) + " " + str(token.lemma_) + " " + str(token.pos_) + " " + str(token.dep_)+"\n")
          
        else: 
            gC.lemma_freq[token.lemma_] += 1  
            gC.word_class[token.lemma_] = token.pos_
            if f != None:
                f.write(str(token.text) + " " + str(token.lemma_) + " " + str(token.pos_) + " " + str(token.dep_)+"\n")    

def POS_all_ads(pos, occ,gC,limit,f):
    for term in occ.description_by_occupation: 
        des_list = occ.description_by_occupation.get(term)
        head_list = occ.head_by_occupation.get(term)
        for des in des_list:
            des_doc = pos.nlp(des)
            for token in des_doc:
                if limit == None:
                    extract_word_classes(token,gC,limit,f)
                if limit != None:
                    if gC.total_nr > limit:
                        return
                    else:
                        extract_word_classes(token,gC,limit,f) 

       

def find_gender_occupation(occ,adv,classified_occupations):
    valid = True 
    occ_label = adv["occupation"]["label"]
    if occ_label in classified_occupations:
        des_text = adv["description"]["text"]
        headline = adv["headline"]
        if occ_label == None or (des_text == None) or (headline == None):
            valid = False 
        else:
            des_text = des_text.strip("\n\r")
            des_text = des_text.strip("\r\n")
            des_text = des_text.strip("\r")
            des_text = des_text.strip('\r\n\r\n\r\n')
            #print(des_text)
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

def collect_all_ads(occ, classified_occupations,gender):
    for year in range(2006,2007):
        print("Reading Advertisement dataset for " + str(gender) + " from year " + str(year)+ ":")  
        f = open(str(year)+'.json')
        ad_set = json.load(f)
        adv_total = len(ad_set)   
        valid_nr = iterate_ad_set(occ, ad_set, classified_occupations) 
        print("Valid adds: " + str(valid_nr))
        print("Invalid adds: " + str(adv_total-valid_nr))
        f.close()
    

def read_classified_occupations(gender):
    if gender == "Men":
        f = open("men-ad-occupations.txt", "r", encoding = "utf-8")
    if gender == "Women":
        f = open("women-ad-occupations.txt", "r", encoding = "utf-8")
    
    classified_occupations = {}
    for ad in f:
        classified_occupations[ad.strip("\n")] = True
    return classified_occupations

def read_POS_terms(gC,gender,limit,year):
    if gender == "Women":
        f = open("POS-" + str(year) + "-Women", "r", encoding = "utf-8")
    if gender == "Men":
        f = open("POS-" + str(year) + "-Men", "r", encoding = "utf-8")
    for row in f: 
        term = row.split(" ")
        token = MANUAL_POS(term[0],term[1],term[2],term[3].strip('\n'))
        if limit == None:
            extract_word_classes(token,gC,limit,None)
        if limit != None:
            if gC.total_nr >= limit:
                return
            else:
                extract_word_classes(token,gC,limit,None)

def sort_popular_terms(gC):
    #Sort popular occupations in descending order
    print(" ")
    print("Top 50 popular terms for " + str(gC.gender) + " in advertisement set.")
    print("#Term  #Frequency")
    popular_terms = {}
    it = len(gC.lemma_freq)
    for i in range(1,51):
        current_value = 0
        current_term = None 
        for term in gC.lemma_freq:
            term_freq = gC.lemma_freq.get(term)
            if term_freq > current_value:
                if term not in popular_terms: 
                    current_value = term_freq
                    current_term = term
        highest_value = current_value
        highest_term = current_term
        popular_terms[highest_term] = True
        print(str(i) + ". " + str(highest_term) + " " + str(highest_value) + " Word class: " + str(gC.word_class.get(highest_term)))

def extract_extreme_carpe_terms(gender_class_list):
    extreme_carpe_terms_c1 = {}
    extreme_carpe_terms_c2 = {}
    class1 = gender_class_list[0]
    class2 = gender_class_list[1]
    g1 = class1.gender
    g2 = class2.gender
    for term in class1.lemma_freq:
        if term not in class2.lemma_freq:
            extreme_carpe_terms_c1[term] = True

    for term in class2.lemma_freq:
        if term not in class1.lemma_freq:
            extreme_carpe_terms_c2[term] = True

    print(str(g1) + " extreme carpe terms: ")
    i = 0 
    for term in extreme_carpe_terms_c1:
        i += 1 
        #print(str(i) + ". " + str(term) + " " + str(class1.lemma_freq.get(term)) +" " + str(class1.word_class.get(term)))
    print(" ")
    i = 0
    for term in class1.lemma_freq:
        if term not in extreme_carpe_terms_c1 and class1.lemma_freq.get(term) > 10:
            i+=1
            print(str(i) + ". " + str(term) + " " + str(class1.lemma_freq.get(term)) +" " + str(class1.word_class.get(term)))
    # print(str(g2) + " extreme carpe terms: ")
    # i = 0 
    # for term in extreme_carpe_terms_c2:
    #     i += 1 
    #     print(str(i) + ". " + str(term) + " " + str(class2.lemma_freq.get(term)))

def classify_extreme(nB,gender_class_list):
    class1 = gender_class_list[0]
    class2 = gender_class_list[1]
    g1 = class1.gender
    g2 = class2.gender
    result_list = {}
    for lemma in class1.lemma_freq:

        P_1, P_2 = nB.classify(lemma)
        if (P_1 > 0.88) and (P_1 < 0.95): 
             result_list[lemma] = ["M", P_1,P_2] 
        
        if (P_2 > 0.88) and (P_2 < 0.95):
            result_list[lemma] = ["W", P_1,P_2]

    print(" ")
    print("RESULT:")
    print("term [Gender,P(M|term), P(W|term)]")
    special_char = '"-[@_!$%^&*().<>?/\|}{~:]#'
    for term in result_list:
        if (class1.word_class[term] == "ADJ") and not any(c in special_char for c in term):
            print(str(term)+ " " + str(class1.word_class[term]) + " " +str(result_list.get(term)))
    
def classify_input(pos,nB):
    while True:
        print(" ")
        print("Type input text:") 
        inp = input()
        terms  = inp.split()
        print(" ")
        result_list = {}
        pos_list = pos.nlp(terms)
            
        for term in pos_list:
            P_1, P_2 = nB.classify(term.lemma_)
            print(term)
            print(term.text, term.lemma_, term.pos_, term.dep_, term.tag_)
            
    
            if (P_1 and P_2) == None: 
                #print("The term '" +str(term) + "' cannot be classified.")
                result_list[term] = None
            elif P_1 > P_2: 
                #print(str(term) + " = MEN  ")
                result_list[term] = ["M", P_1,P_2] 
            else:
                #print(str(term) + " = WOMEN  ")
                result_list[term] = ["W", P_1,P_2]
            #print("P(Men I " + str(term) + ") = " + str(P_1) + "   -   P(Women I " + str(term) + ") = " + str(P_2))
        print("Input text: " +str(inp))

        print(" ")
        print("RESULT:")
        print("term [Gender,P(M|term), P(W|term)]")
        for term in result_list:
            print(str(term)+  " " +str(result_list.get(term)))

def main():
    g_list = ["Men", "Women"]
    gender_class_list = []
    nB = NaiveBayes()
    pos = POS()
    limit = None 
    for gender in g_list:
        gC = GenderClass(gender)
        gender_class_list.append(gC)
        for year in range(2006, 2011):
            #f = open("POS-2006-"+str(gender), "w", encoding ="utf-8")
            #occ = OccupationMerge()
            #gC = GenderClass(gender)
            #classified_occupations = read_classified_occupations(gender) #no men-file 
            #collect_all_ads(occ, classified_occupations,gender)
            #POS_all_ads(pos,occ,gC,limit,f)
            read_POS_terms(gC,gender,limit, year)
        nB.createClass(gC)
        limit = gC.total_nr
        sort_popular_terms(gC)
            #f.close()
    extract_extreme_carpe_terms(gender_class_list)
    #classify_extreme(nB, gender_class_list)
    classify_input(pos,nB)

    #for gender in g_list:
        #f = open("POS-2006-"+str(gender), "w", encoding ="utf-8")
        #occ = OccupationMerge()
        #gC = GenderClass(gender)
        #classified_occupations = read_classified_occupations(gender) #no men-file 
        #collect_all_ads(occ, classified_occupations,gender)
        #POS_all_ads(pos,occ,gC,limit,f)
        #nB.createClass(gC)
        #limit = gC.total_nr
        #sort_popular_terms(gC)
        #f.close()
        
main()
