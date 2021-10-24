import json
import sys
import spacy_udpipe
import re
import xml.etree.ElementTree as ET
from termcolor import colored

# ========================== Classes ===================================

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
    def __init__(self,gender): 
        self.gender = gender
        self.total_nr = 0
        self.lemma_pos_freq = {} #lemma_pos_freq {lemma1: {word_class1:freq, word_class2:freq}}
        self.lemma_text_freq = {} #lemma_word {lemma1: {word1:freq, word2:freq}}
        self.text_lemma_freq = {} #word_lemma {word1: {lemma1:freq,lemma2:freq} }
        self.lemma_count = 0
        self.text_count = 0 
    
class NaiveBayes:
    def __init__(self):
        self.class_list = []
        self.N = 0
        
    def createClass(self,gC):
        self.class_list.append(gC)
        self.P_c = 1/len(self.class_list)
        #print("Adding " + str(gC.gender) + " Class with size of: " + str(gC.total_nr)+ " lemma_pos_freq.")
        self.N += gC.total_nr

    def classify_lemma(self,lemma, pos):
        term_freq = 0
        
        class1 = self.class_list[0] #Men class
        class2 = self.class_list[1] #Women class 
        N = class1.lemma_count + class2.lemma_count
        for g_class in self.class_list:
            try:
                pos_freq = g_class.lemma_pos_freq[lemma][pos]
                term_freq += pos_freq
            except:
                continue
        print(" ")
        print("Total number of the term for both classes:" + str(term_freq))
        P_t = term_freq/N   
        
        if P_t == 0:
            print("The term can't be found in any class.")
            return None, None 
        
        else:  
            #CHECK CLASS1
            if lemma not in class1.lemma_pos_freq:
                P_c1_t =  0
                c1_term_freq = 0
            else: #if lemma is in class
                if pos not in class1.lemma_pos_freq[lemma]:
                    P_c1_t =  0
                    c1_term_freq = 0
                else: 
                    c1_term_freq = class1.lemma_pos_freq[lemma][pos]  
                    P_t_c1 = c1_term_freq/class1.total_nr
                    P_c1_t = (P_t_c1*self.P_c) / P_t
                    print("Term frequency in men: " + str(c1_term_freq))
            
            #CHECK CLASS2
            if lemma not in class2.lemma_pos_freq:
                P_c2_t =  0
                c2_term_freq = 0
            else: #if lemma is in class
                if pos not in class2.lemma_pos_freq[lemma]:
                    P_c2_t =  0
                    c2_term_freq = 0
                else: 
                    c2_term_freq = class2.lemma_pos_freq[lemma][pos]  
                    P_t_c2 = c2_term_freq/class2.total_nr
                    P_c2_t = (P_t_c2*self.P_c) / P_t
                    print("Term frequency in women: " + str(c2_term_freq))
        return P_c1_t, P_c2_t

    def classify_text(self,text, lemma):
        term_freq = 0
        
        class1 = self.class_list[0] #Men class
        class2 = self.class_list[1] #Women class 
        N = class1.text_count + class2.text_count
        for g_class in self.class_list:
            try:
                lemma_freq = g_class.text_lemma_freq[text][lemma]
                term_freq += lemma_freq
            except:
                continue
        print(" ")
        print("Total number of the term for both classes:" + str(term_freq))
        P_t = term_freq/N   
        
        if P_t == 0:
            print("The term can't be found in any class.")
            return None, None 
        
        else:  
            #CHECK CLASS1
            if text not in class1.text_lemma_freq:
                P_c1_t =  0
                c1_term_freq = 0
            else: #if lemma is in class
                if lemma not in class1.text_lemma_freq[text]:
                    P_c1_t =  0
                    c1_term_freq = 0
                else: 
                    c1_term_freq = class1.text_lemma_freq[text][lemma]  
                    P_t_c1 = c1_term_freq/class1.total_nr
                    P_c1_t = (P_t_c1*self.P_c) / P_t
                    print("Term frequency in men: " + str(c1_term_freq))
            
            #CHECK CLASS2
            if text not in class2.text_lemma_freq:
                P_c2_t =  0
                c2_term_freq = 0
            else: #if lemma is in class
                if lemma not in class2.text_lemma_freq[text]:
                    P_c2_t =  0
                    c2_term_freq = 0
                else: 
                    c2_term_freq = class2.text_lemma_freq[text][lemma]  
                    P_t_c2 = c2_term_freq/class2.total_nr
                    P_c2_t = (P_t_c2*self.P_c) / P_t
                    print("Term frequency in women: " + str(c2_term_freq))
        return P_c1_t, P_c2_t

class POStags:
    def __init__(self):
        self.wordclass = {}

# ============================== End of classes =================================

"""
USED IN STEP 1&2
"""
def extract_word_classes(token,gC,f):
   
    special_char = '"-[@_!$%^&*().<>?/\|}{~:]#'
    if not any(c in special_char for c in token.text):
        if (token.pos_ == "NOUN") or (token.pos_ == "ADJ") or (token.pos_ == "ADV") or ((token.pos_ == "VERB")):
            if f != None: #Only write to file in STEP 1
                f.write(str(token.text) + " " + str(token.lemma_) + " " + str(token.pos_) + " " + str(token.dep_)+"\n") 
            gC.total_nr +=1
            
            #CHECK LEMMA
            if token.lemma_ not in gC.lemma_pos_freq: #if new lemma 
                gC.lemma_count +=1
                pos_freq = {}
                pos_freq[token.pos_] = 1 #initiate
                gC.lemma_pos_freq[token.lemma_] = pos_freq
                text_freq = {}
                text_freq[token.text] = 1 #initiate
                gC.lemma_text_freq[token.lemma_] = text_freq
            else: #if old lemma
                gC.lemma_count +=1
                if token.pos_ not in gC.lemma_pos_freq[token.lemma_]:
                    gC.lemma_pos_freq[token.lemma_][token.pos_] = 1 #pos_freq[token.pos_] = 1
                else:
                    gC.lemma_pos_freq[token.lemma_][token.pos_] += 1

                if token.text not in gC.lemma_text_freq[token.lemma_]:
                    gC.lemma_text_freq[token.lemma_][token.text] = 1 #text_freq[token.text] = 1
                else:
                    gC.lemma_text_freq[token.lemma_][token.text] += 1

            #CHECK WORD
            if token.text not in gC.text_lemma_freq:
                gC.text_count +=1
                lemma_freq = {}
                lemma_freq[token.lemma_] = 1
                gC.text_lemma_freq[token.text] = lemma_freq
            else: #if old word
                gC.text_count +=1
                if token.lemma_ not in gC.text_lemma_freq[token.text]:
                    gC.text_lemma_freq[token.text][token.lemma_] = 1
                else:
                    gC.text_lemma_freq[token.text][token.lemma_] += 1

                    
               
"""
USED IN STEP 1
"""
def POS_all_ads(pos, occ,gC,limit,f):
    for term in occ.description_by_occupation: 
        des_list = occ.description_by_occupation.get(term)
        head_list = occ.head_by_occupation.get(term)
        for des in des_list:
            des_doc = pos.nlp(des)
            for token in des_doc:
                if limit == None:
                    extract_word_classes(token,gC,f)
                if limit != None:
                    if gC.total_nr > limit:
                        return
                    else:
                        extract_word_classes(token,gC,f) 

       
"""
USED IN STEP 1
"""
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
            occ.add_ad_data(occ_label, des_text, headline.strip('\n').strip('\r'))
    else:
        valid = False
    return valid 

"""
USED IN STEP 1
"""
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

"""
USED IN STEP 1
"""
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
    
"""
USED IN STEP 1 
"""
def read_classified_occupations(gender):
    if gender == "Men":
        f = open("men-ad-occupations.txt", "r", encoding = "utf-8")
    if gender == "Women":
        f = open("women-ad-occupations.txt", "r", encoding = "utf-8")
    
    classified_occupations = {}
    for ad in f:
        classified_occupations[ad.strip("\n")] = True
    return classified_occupations

# ============================== "Extra"-functions to sort popular terms and get unique terms ======================

def sort_popular_terms(gC):
    #Sort popular occupations in descending order
    print(" ")
    print("Top 50 popular terms for " + str(gC.gender) + " in advertisement set.")
    print("#Term  #Frequency")
    popular_terms = {}
    it = len(gC.lemma_pos_freq)
    for i in range(1,51):
        current_value = 0
        current_term = None 
        for term in gC.lemma_pos_freq:
            term_freq = gC.lemma_pos_freq.get(term)
            if term_freq > current_value:
                if term not in popular_terms: 
                    current_value = term_freq
                    current_term = term
        highest_value = current_value
        highest_term = current_term
        popular_terms[highest_term] = True
        print(str(i) + ". " + str(highest_term) + " " + str(highest_value) + " Word class: " + str(gC.word_class.get(highest_term)))

def extract_unique_gender_lemmas(gender_class_list):
    important_word_classes = {}
    extreme_carpe_lemmas_c1 = {}
    extreme_carpe_lemmas_c2 = {}
    class1 = gender_class_list[0]
    class2 = gender_class_list[1]
    g1 = class1.gender
    g2 = class2.gender
    for lemmas in class1.lemma_pos_freq:
        if lemmas not in class2.lemma_pos_freq:
            extreme_carpe_lemmas_c1[lemmas] = True

    for lemmas in class2.lemma_pos_freq:
        if lemmas not in class1.lemma_pos_freq:
            extreme_carpe_lemmas_c2[lemmas] = True

    print(str(g1) + "Extreme carpe lemmas: ")
    i = 0 
    for m_lemma in extreme_carpe_lemmas_c1:
        i += 1 
        #print(str(i) + ". " + str(m_lemma) + " " + str(class1.lemma_pos_freq.get(m_lemma)))
        for word_class in class1.lemma_pos_freq.get(m_lemma):
            if word_class == "årskurs":
                print("men")
                print(str(m_lemma) + " " + str(class2.lemma_pos_freq.get(m_lemma)))
            important_word_classes[word_class] = True 
    print(" ")
    i = 0
    
    print(str(g2) + "Extreme carpe lemmas: ")
    i = 0 
    for w_lemma in extreme_carpe_lemmas_c2:
        #print("w_lemma: " + str(w_lemma))
        
        #if "ADJ" in class2.lemma_pos_freq.get(w_lemma):
          #  if class2.lemma_pos_freq.get(w_lemma).get("ADJ") > 50:
        i += 1 
        #print(str(i) + ". L - " + str(w_lemma) + " " + str(class2.lemma_pos_freq.get(w_lemma)))
        for word_class in class2.lemma_pos_freq.get(w_lemma):
            if word_class == "årskurs":
                print("women")
                print(str(w_lemma) + " " + str(class2.lemma_pos_freq.get(w_lemma)))
            important_word_classes[word_class] = True 
    print("---")
    print("Important word classes: " + str(important_word_classes))

def extract_unique_gender_terms(gender_class_list):
    extreme_carpe_terms_c1 = {}
    extreme_carpe_terms_c2 = {}
    class1 = gender_class_list[0]
    class2 = gender_class_list[1]
    g1 = class1.gender
    g2 = class2.gender
    for term in class1.text_lemma_freq:
        if term not in class2.text_lemma_freq:
            extreme_carpe_terms_c1[term] = True

    for term in class2.text_lemma_freq:
        if term not in class1.text_lemma_freq:
            extreme_carpe_terms_c2[term] = True

    print(str(g1) + " Extreme carpe terms: ")
    i = 0 
    for m_term in extreme_carpe_terms_c1:
        i += 1 
        #print(str(i) + ". " + str(m_term) + " " + str(class1.text_lemma_freq.get(m_term)))
    print(" ")
    i = 0
    
    print(str(g2) + " Extreme carpe terms: ")
    i = 0 
    for w_term in extreme_carpe_terms_c2:
        lemma_dict = class2.text_lemma_freq.get(w_term)
        for lemma in lemma_dict:
            pos_dict = class2.lemma_pos_freq.get(lemma)
            #print(str(w_term) +": " + str(pos_dict))
            if "ADJ" in pos_dict:
                #print(str(lemma) + ": "+ str(pos_dict))
                if pos_dict.get("ADJ") > 50:
                    i += 1 
                    print(str(i) + ". T - " + str(w_term) + " " + str(class2.text_lemma_freq.get(w_term)))

    #Print normal words:
    # for term in class1.lemma_pos_freq:
    #     if term not in extreme_carpe_terms_c1 and class1.lemma_pos_freq.get(term) > 10:
    #         i+=1
            #print(str(i) + ". " + str(term) + " " + str(class1.lemma_pos_freq.get(term)) +" " + str(class1.word_class.get(term)))


# ====================== Classify extreme terms and input ================================
    
"""
USED IN STEP 2
"""
def classify_extreme(nB,gender_class_list):
    class1 = gender_class_list[0]
    class2 = gender_class_list[1]
    g1 = class1.gender
    g2 = class2.gender
    result_list = {}
    for lemma in class1.lemma_pos_freq:
        pos_dict = class1.lemma_pos_freq.get(lemma)
        POStag = max(pos_dict, key=pos_dict.get)
        if POStag == "ADJ":
            P_1, P_2 = nB.classify_lemma(lemma, POStag)
            if (P_1 > 0.85) and (P_1 < 0.98): 
                result_list[lemma] = ["M", P_1,P_2] 
            
            if (P_2 > 0.85) and (P_2 < 0.98):
                result_list[lemma] = ["W", P_1,P_2]

    print(" ")
    print("RESULT:")
    print("term [Gender,P(M|term), P(W|term)]")
    for term in result_list:
        print(str(term)+ " " + str(result_list.get(term)))

def classify_with_lemma(pos_list, use_sprakbanken_wordclasses, POS_obj, nB):
    print("CLASSIFY WITH LEMMA: ")
    result_list = {}
    for term in pos_list:
        if (use_sprakbanken_wordclasses == True) and (term.text in POS_obj.wordclass):
            POStag = max(POS_obj.wordclass.get(term.text), key=POS_obj.wordclass.get(term.text).get)
            P_1, P_2 = nB.classify_lemma(term.lemma_, POStag)
        else:
            P_1, P_2 = nB.classify_lemma(term.lemma_, term.pos_)

        if (P_1 and P_2) == None: 
            #print("The term '" +str(term) + "' cannot be classified.")
            result_list[term.text] = None
        elif P_1 > P_2: 
            #print(str(term) + " = MEN  ")
            result_list[term.text] = ["M", P_1,P_2] 
        else:
            #print(str(term) + " = WOMEN  ")
            result_list[term.text] = ["W", P_1,P_2]

    print(" ")
    print("RESULT WITH LEMMA:")
    print("term [Gender,P(M|term), P(W|term)]")
    for term in result_list:
        print(str(term)+  " " +str(result_list.get(term)))

    return result_list

def classify_with_text(pos_list, nB):
    print("CLASSIFY WITH TEXT: ")
    result_list = {}
    for term in pos_list:
        P_1, P_2 = nB.classify_text(term.text, term.lemma_)

        if (P_1 and P_2) == None: 
            result_list[term.text] = None
        elif P_1 > P_2: 
            result_list[term.text] = ["M", P_1,P_2] 
        else:
            result_list[term.text] = ["W", P_1,P_2]

    print(" ")
    print("RESULT WITH TEXT:")
    print("term [Gender,P(M|term), P(W|term)]")
    for term in result_list:
        print(str(term)+  " " +str(result_list.get(term)))
    
    return result_list

def get_synonyms(pos, POS_obj, nB, input_list):
    tree = ET.parse('synpairs.xml')
    root = tree.getroot()
    synonym_list = {}
    for term in input_list: 
        synonyms = [] 
        for word in root[2].findall('syn'):
            if word[0].text == term:
                synonyms.append(word[1].text)
        synonym_list[term] = synonyms
    
    return synonym_list

"""
USED IN STEP 2
Classify the user-input from the terminal
""" 
def classify_input(pos,nB,POS_obj,use_sprakbanken_wordclasses,lemma, text):
    while True:
        print("\nWhat gender would you like to target? (W/M)")
        target_gender = input()
        if target_gender != "W" and target_gender != "M":
            print("You have to write either W or M")
        else:
            break

    while True:
        print(" ")
        print(colored("Type input text:", attrs = ['underline', 'bold'])) 
        inp = input()
        terms  = inp.split()
        lower_terms = []
        for term in terms:
            lower_terms.append(term.lower().strip('"-[@_!$%^&*().<>?/\|}{~:]#'))
        print(" ")
        pos_list = pos.nlp(lower_terms)

        #Classify input text based on lemma
        if lemma:
            lemma_results = classify_with_lemma(pos_list, use_sprakbanken_wordclasses, POS_obj, nB)
            colored_text = ""
            i = 0
            for term in terms:
                term = term.lower().strip('"-[@_!$%^&*().<>?/\|}{~:]#')
                if lemma_results[term] == None:
                    colored_text += terms[i] + " "
                elif lemma_results[term][0] == "M":
                    colored_text += colored(terms[i] + " ", 'blue')
                elif lemma_results[term][0] == "W":
                    colored_text += colored(terms[i] + " ", 'red')
                i += 1
            results = lemma_results
            


        #Classify input text based on text
        if text:
            text_results = classify_with_text(pos_list, nB)
            colored_text = ""
            i = 0
            for term in terms:
                term = term.lower().strip('"-[@_!$%^&*().<>?/\|}{~:]#')
                if text_results[term] == None:
                    colored_text += terms[i] + " "
                elif text_results[term][0] == "M":
                    colored_text += colored(terms[i] + " ", 'blue')
                elif text_results[term][0] == "W":
                    colored_text += colored(terms[i] + " ", 'red')
                i += 1
            results = text_results
            
        #Get a dictionary with all words and their synonyms 
        synonym_list = get_synonyms(pos, POS_obj, nB, lower_terms) #get all synonyms for all words
        synonym_term_list = {}
        for term in synonym_list: 
            if term not in synonym_term_list:
                synonym_pos_list = pos.nlp(synonym_list[term])
                synonym_text_results = classify_with_text(synonym_pos_list, nB)
                synonym_term_list[term] = synonym_text_results
        # synonym_lemma_results = classify_with_lemma(synonym_pos_list, use_sprakbanken_wordclasses, POS_obj, nB)
        
        print("\n============================================\n")
        print(colored("THIS IS YOUR RESULT: \n", attrs = ['bold','underline']))
        print("\nRed words often attract more women, and blue words often attract more men.\n")
        print(colored_text)
        print(" ")

        if target_gender == "W":
            gender = "WOMEN"
            other_gender = "M"
            color = 'blue'
        elif target_gender == "M":
            gender = "MEN"
            other_gender = "W"
            color = 'red'
        
        print(colored("Here are some examples of words that could be changed to target more " + gender + ":", attrs = ['bold']))

        no_synonyms = {}
        for term in results:
            synonyms = []

            if results[term] != None:
                if results[term][0] == other_gender: #If the word is attracting the gender opposite to our target gender, we would like to find a synonym for that. 
                    no_synonyms[term] = False #set this to False = the word has no synonyms
                
                    if (synonym_term_list.get(term) == {}):
                        no_synonyms[term] = False
                    else:
                        for synonym in synonym_term_list.get(term): #for every synonym for the term
                            if synonym_term_list.get(term)[synonym] != None and synonym_term_list.get(term)[synonym][0] == target_gender:
                                synonyms.append(synonym)
                                no_synonyms[term] = True


            if (len(synonyms) > 0):
                print(" ")
                print("The word " + colored(str(term), color) + " could be changed to:")
                print(*synonyms, sep = "\n")
        
        print("\nWe could not find any synonyms for the following words:")
        for term in no_synonyms:
            if no_synonyms[term] == False:
                print(term)
  
            


# ============================== Functions used in STEP 2 =====================================

"""
USED IN STEP 2
Goes through the POS-files and create token-objects (MANUAL_POS)
"""
def read_POS_files(gC,gender,limit,year,POS_obj, use_sprakbanken_wordclasses):
    if gender == "Women":
        f = open("POS-" + str(year) + "-Women", "r", encoding = "utf-8")
    if gender == "Men":
        f = open("POS-" + str(year) + "-Men", "r", encoding = "utf-8")
    
    for row in f: 
        term = row.split(" ")
        if len(term) == 4:
            if use_sprakbanken_wordclasses == True:
                #----Change----
                #Check if the term is in the POS_obj.wordclass-dict, i.e. from the new wordclass-dataset
                if term[0].lower() in POS_obj.wordclass:
                    POStag = max(POS_obj.wordclass.get(term[0].lower()), key=POS_obj.wordclass.get(term[0].lower()).get)
                #if the term isn't available in the POS_obj.wordclass-dict, then we use the spacy_udpipe POStag
                else:
                    POStag = term[2]
                #----End-of-change----
            else:
                POStag = term[2]
            token = MANUAL_POS(term[0].lower(),term[1].lower(),POStag,term[3].strip('\n')) 
            if limit == None:
                extract_word_classes(token,gC,None)
            if limit != None:
                if gC.total_nr >= limit:
                    return
                else:
                    extract_word_classes(token,gC,None)


"""
USED IN STEP 2
Go through the new wordclass-dataset and extract the words and their wordclasses 
This information is added to the POS_obj where the dict = {term1: {WORDCLASS1: Stats, WORDCLASS": Stats}}
"""
def collect_new_POS_tags(POS_obj):
    f = open("export.csv", "r", encoding ="utf-8")
    for row in f:
        word_list = row.split(";")
        term = word_list[0].strip('"').lower() #The term
        word_class = word_list[1].strip('"') #The wordclass for the term
        stats = float(word_list[2].strip('"')) #The number of occurences for the term with that specific wordclass (Stats)

        #Check if something strange has happened when reading from the file, i.e. the worclass doesn't exist
        if word_class != "NN" and word_class != "JJ" and word_class != "AB" and word_class != "VB":
            print("Cannot match the wordclass: " + word_class)
        #Change wordclasses to the ones that spacy_udpipe is using, i.e. "NOUN, ADJ, ADV and VERB"
        else:
            if word_class == "NN":
                word_class = "NOUN"
            elif word_class == "JJ":
                word_class = "ADJ"
            elif word_class == "AB":
                word_class = "ADV"
            elif word_class == "VB":
                word_class = "VERB"
        
        #If the term haven't been seen before
        if term not in POS_obj.wordclass:
            pos_tags = {}
            pos_tags[word_class] = stats
            POS_obj.wordclass[term] = pos_tags
        #If the term have been seen before
        else:
            #If the wordclass for the term haven't been seen before
            if word_class not in POS_obj.wordclass.get(term):
                POS_obj.wordclass.get(term)[word_class] = stats
            #If the wordclass for the term have been seen before, then we want to add the stats
            else:
                POS_obj.wordclass.get(term)[word_class] += stats     


# ===================================== Main-functions ==================================
"""
STEP 1: Write to POS files
"""
def step1_write_POS_to_file(g_list, nB, pos, limit):
    for gender in g_list:
        f = open("POS-2006-"+str(gender), "w", encoding ="utf-8")
        occ = OccupationMerge()
        gC = GenderClass(gender)
        classified_occupations = read_classified_occupations(gender) 
        collect_all_ads(occ, classified_occupations,gender)
        POS_all_ads(pos,occ,gC,limit,f)
        nB.createClass(gC)
        limit = gC.total_nr
        sort_popular_terms(gC)
        f.close()

"""
STEP 2: Collect POStags from POS-files and classify
"""
def step2_collect_POStags_and_classify(g_list, nB, pos, limit, POS_obj):
    #List to be able to access the GenderClass-objects
    gender_class_list = []

    #Read all POStags from the new wordclass-dataset and gather it in the POS_obj
    collect_new_POS_tags(POS_obj)

    #Set this one to True if you want to use språkbankens dataset and False if you want to use spacy_udpipes pos-tagger
    use_sprakbanken_wordclasses = True
    
    for gender in g_list:
        gC = GenderClass(gender)
        gender_class_list.append(gC)
        for year in range(2006, 2011):
            read_POS_files(gC,gender,limit, year, POS_obj, use_sprakbanken_wordclasses)
        nB.createClass(gC)
        limit = gC.total_nr
        #sort_popular_terms(gC)
    #extract_unique_gender_lemmas(gender_class_list)
    #extract_unique_gender_terms(gender_class_list)
    #classify_extreme(nB, gender_class_list)
    calculate_with_lemma = True
    calculate_with_text = False
    classify_input(pos,nB, POS_obj, use_sprakbanken_wordclasses, calculate_with_lemma, calculate_with_text)



def main():
    #All kod här nedanför är för att testa få ihop programmet med server.js
    if sys.argv[1] == "ARG1":
        d = {"key1": 231, "key2": 4657}
        dataToSendBack = json.dumps(d)
        print("HAKLLLÅDASD")
        print(dataToSendBack)
        sys.stdout.flush()
    else:
        print(str(sys.argv[1].toString()))
        sys.stdout.flush()
    # ==================================
    g_list = ["Men", "Women"]
    nB = NaiveBayes()
    pos = POS()
    POS_obj = POStags()
    limit = None 
    #step1_write_POS_to_file(g_list, nB, pos, limit)
    #step2_collect_POStags_and_classify(g_list, nB, pos, limit, POS_obj) #Kommentera bort denna för att köra programmet 
   
main()
