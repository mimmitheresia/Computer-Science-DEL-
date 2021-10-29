# coding=utf-8
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

class GenderClass:
    def __init__(self,gender): 
        self.gender = gender
        self.total_nr = 0
        self.lemma_pos_freq = {} #lemma_pos_freq {lemma1: {word_class1:freq, word_class2:freq}}
        self.lemma_text_freq = {} #lemma_word {lemma1: {word1:freq, word2:freq}}
        self.text_lemma_freq = {} #word_lemma {word1: {lemma1:freq,lemma2:freq} }
        self.text_lemma_pos = {}
        self.lemma_freq = {}
        self.lemma_count = 0
        self.text_count = 0 
    
class NaiveBayes:
    def __init__(self):
        self.class_list = []
        self.N = 0
        self.unique_lemmas = {}
        
    def createClass(self,gC):
        self.class_list.append(gC)
        self.P_c = 1/len(self.class_list)
        self.N += gC.total_nr

    def classify_lemma(self,lemma):
        lemma_freq = 0
        
        class1 = self.class_list[0] #Men class
        class2 = self.class_list[1] #Women class 
        N = class1.lemma_count + class2.lemma_count
        for g_class in self.class_list:
            try:
                l_freq = g_class.lemma_freq[lemma]
                lemma_freq += l_freq
            except:
                continue
        P_t = lemma_freq/N   
        
        if P_t == 0:
            return None, None 
        
        else:  
            #CHECK CLASS1
            if lemma not in class1.lemma_freq:
                P_c1_t =  0
                c1_lemma_freq = 0
            else: #if lemma is in class
                c1_lemma_freq = class1.lemma_freq[lemma]
                P_t_c1 = c1_lemma_freq/class1.total_nr
                P_c1_t = (P_t_c1*self.P_c) / P_t
                #print("Term frequency in men: " + str(c1_term_freq))
            
            #CHECK CLASS2
            if lemma not in class2.lemma_freq:
                P_c2_t =  0
                c2_term_freq = 0
            else: #if lemma is in class
                c2_lemma_freq = class2.lemma_freq[lemma]  
                P_t_c2 = c2_lemma_freq/class2.total_nr
                P_c2_t = (P_t_c2*self.P_c) / P_t
                #print("Term frequency in women: " + str(c2_term_freq))
        return P_c1_t, P_c2_t

class POStags:
    def __init__(self):
        self.wordclass = {}

# ============================== Classify all lemmas and synonyms =================================
        
            
def write_all_info_to_file(lemma, P_2, sorted_synonyms,f):
    
    final_format = "{" + str(lemma) + "[" + str(round(P_2, 2)) + ",{"
    if sorted_synonyms == " " or sorted_synonyms == []:
        final_format += " "
    else:
        for synonym in sorted_synonyms:
            final_format += str(synonym[0]) + ":" + str(synonym[1]) + ","
        final_format = final_format[0:len(final_format)-1]
    final_format += "}]}"
    f.write(final_format + "\n")


def classify_synonyms(pos_list, nB):
    result_list = {}
    for term in pos_list:
        P_1, P_2 = nB.classify_lemma(term.lemma_)    
        if (P_1 and P_2) != None: 
            if P_2 > 0.4:
                result_list[term.text] = round(P_2,2)

    return result_list

def get_synonyms(lemma):
    tree = ET.parse('/Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/synpairs.xml')
    root = tree.getroot()
    synonyms = [] 
    for word in root[2].findall('syn'):
        if word[0].text == lemma:
            synonyms.append(word[1].text)
    return synonyms

def classify_lemmas(nB, pos):
    #f = open("All_information.txt", "w", encoding = "utf-8")
    result_list = {}
  
    for lemma in nB.unique_lemmas:
        P_1, P_2 = nB.classify_lemma(lemma) #round(P_2, 2)
       
        synonym_list = get_synonyms(lemma) #get all synonyms for the lemma 
        if not synonym_list:
            sorted_synonyms = " "

        else:
            synonym_pos_list = pos.nlp(synonym_list)
            classified_synonyms = classify_synonyms(synonym_pos_list, nB) #Får tillbaka {synonym1: p(kvinna), synonym2: p(kvinna)}
            sorted_synonyms = sorted(classified_synonyms.items(), key=lambda x: x[1], reverse=True)

        #write_all_info_to_file(lemma, P_2, sorted_synonyms,f)
    #f.close()

# ============================ Gather data from språkbanken and POS-files =====================================

"""
Here we count the frequency of each lemma in the recruitment-ad dataset 
"""
def extract_word_classes(token,gC,f,nB):
    special_char = '"-[@_!$%^&*().,+<>?/\|}{~:]#'
    if not any(c in special_char for c in token.text):
        if (token.pos_ == "NOUN") or (token.pos_ == "ADJ") or (token.pos_ == "ADV") or ((token.pos_ == "VERB")):
            gC.total_nr +=1
            nB.unique_lemmas[token.lemma_] = True
            if token.lemma_ not in gC.lemma_freq: 
                gC.lemma_count +=1
                gC.lemma_freq[token.lemma_] = 1

            else: 
                gC.lemma_count +=1
                gC.lemma_freq[token.lemma_] += 1            

"""
Goes through the POS-files and create token-objects (MANUAL_POS)
"""
def read_POS_files(gC,gender,limit,year,POS_obj, use_sprakbanken_wordclasses, nB):
    if gender == "Women":
        f = open("/Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/POS-" + str(year) + "-Women", "r", encoding = "utf-8")
    if gender == "Men":
        f = open("/Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/POS-" + str(year) + "-Men", "r", encoding = "utf-8")
    
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
                extract_word_classes(token,gC,None, nB)
            if limit != None:
                if gC.total_nr >= limit:
                    return
                else:
                    extract_word_classes(token,gC,None, nB)



"""
Goes through the new wordclass-dataset and extract the words and their wordclasses 
This information is added to the POS_obj where the dict = {term1: {WORDCLASS1: Stats, WORDCLASS": Stats}}
"""
def collect_new_POS_tags(POS_obj):
    f = open("/Users/ewelynstrandberg/Desktop/KTH/DEL/DEL/export.csv", "r", encoding ="utf-8")
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
            read_POS_files(gC,gender,limit, year, POS_obj, use_sprakbanken_wordclasses, nB)
        nB.createClass(gC)
        limit = gC.total_nr
    
    classify_lemmas(nB, pos)
   

def main():
    g_list = ["Men", "Women"]
    nB = NaiveBayes()
    pos = POS()
    POS_obj = POStags()
    limit = None
    step2_collect_POStags_and_classify(g_list, nB, pos, limit, POS_obj) 
 
main()