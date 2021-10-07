import difflib as dl

class OccupationStatistic:
    def __init__(self, occ, r_w, r_m ): 
        self.occupation = occ
        self.ratio_women = r_w
        self.ratio_men = r_m

class OccupationAds:
    def __init__(self,occ,nr):
        self.occupation = occ
        self.occ_nr = nr



def readAdTerms():
    ads_obj_dict = {}
    ads_occ_list = []
    f = open("2006-2011-occupation-frequency.txt","r",encoding="utf8")
    for row in f:
        index = row.rfind(":")
        occ = row[:index].strip()
        occ_nr = int(row[index+1:])
        occ_ads = OccupationAds(occ,occ_nr)
        ads_obj_dict[occ] = occ_ads
        ads_occ_list.append(occ)
    return ads_obj_dict, ads_occ_list

def return_similarity_match(stat_gender, ad_occ, ad_obj, gender):
    #Assumption 5 adjectives per ad description. 
    i  = 31
    total_nr = 0 
    print(str(gender) + " dominated occupation label in statistic: ")
    for obj in stat_gender[30:]:
        print(" ")
        print(" ")
        if gender == "Men":
            print((str(i) + "."+ str(obj.occupation) + " - ratio: " + str(obj.ratio_men)+ "%"))
        if gender == "Women":
            print((str(i) + "."+ str(obj.occupation) + " - ratio: " + str(obj.ratio_women)+ "%"))
        print(" ")
        match = dl.get_close_matches(obj.occupation, ad_occ, cutoff = 0.1, n=11)
        print("Most similar occupation labels in ad set:")
        for element in match:
            obj = ad_obj.get(element)
            print(element + " - frequency of ads: " + str(obj.occ_nr) )
            total_nr += obj.occ_nr

        i += 1
    print("Total nr of ads: " + str(total_nr))

def return_manual_match(stat_gender, ad_occ,ad_obj, gender):
    #manual created dict
    #{stat_index, [ad_indexs]}  = {index of accurate label in stat_women, list of index of accurate ad match in match-list}
    #if match is set to True: all matches are included 
    if gender == "Women":
        accurate_gender_ads = {0:0, 2:0, 3:"ALL", 4:0, 5:0, 8:0, 9:0, 10:[0,1],11:0, 14:3} 
        f = open("women-ad-occupations.txt", "w", encoding = "utf-8")
    if gender == "Men":
        accurate_gender_ads = { 0:0, 11:6, 18:[0,1,4], 19:0, 31:0,32:0, 36:[0,3], 37:[1,2], 38:[1,2], 39:0, 40:[0,1], 55:0}
        f = open("men-ad-occupations.txt", "w", encoding = "utf-8")
    
    i  = 1
    total_nr = 0 
    nr_of_acc_occ = 0 
    stat_index = 0
    stat_nr = len(stat_gender)
    print(str(stat_nr) + " "+str(gender) + " dominated occupation labels in Statistic set: ")
    one_hit = {}
    for obj in stat_gender:
        if stat_index in accurate_gender_ads:
            print("stat_index: " + str(stat_index))
            print(" ")
            if gender == "Men":
                print((str(i) + "."+ str(obj.occupation) + " - ratio: " + str(obj.ratio_men)+ "%"))
            if gender == "Women":
                print((str(i) + "."+ str(obj.occupation) + " - ratio: " + str(obj.ratio_women)+ "%"))
            i += 1
            print(" ")
            ad_matches = dl.get_close_matches(obj.occupation, ad_occ, cutoff = 0.1, n=10)
            ad_indexs = accurate_gender_ads.get(stat_index)
            if (type(ad_indexs) == int): #one accurate match
                acc_occ = returnOneAccurate(ad_matches,ad_indexs)
            if (type(ad_indexs) == list): # >1 accurate match
                acc_occ = returnSeveralAccurate(ad_matches,ad_indexs)
            if ((ad_indexs) == "ALL" ): #all matches are accurate
                acc_occ = ad_matches 
            print("Accurate match in ad set:") 
            for acc_sim in acc_occ:
                if acc_sim not in one_hit:
                    one_hit[acc_sim] = True
                    obj = ad_obj.get(acc_sim)
                    print(acc_sim + " - nr of valid ads: " + str(obj.occ_nr))
                    f.write(str(acc_sim) + "\n")
                    nr_of_acc_occ += 1 
                    total_nr += obj.occ_nr
        stat_index +=1      
        
    print("Number of accurate occupations: " + str(nr_of_acc_occ))
    print("Total nr of ads: " + str(total_nr))

def returnOneAccurate(ad_matches, ad_indexs):
    ad_i = 0
    for similar_ad_occ in ad_matches:
        if ad_i == ad_indexs:
            return [similar_ad_occ]
        ad_i +=1

def returnSeveralAccurate(ad_matches, ad_indexs):
    
    returnlist = []
    for acc in ad_indexs:
        ad_i = 0
        for similar_ad_occ in ad_matches:
            if ad_i == acc:
                returnlist.append(similar_ad_occ)
            ad_i +=1
    return returnlist

def returnDominatedOccupations(statistic_obj_dict,gender):
    stat_gender = []
 
    for label in statistic_obj_dict:
        obj = statistic_obj_dict.get(label)
        if gender == "Women":
            if obj.ratio_women > 85:
                stat_gender.append(obj)
        if gender == "Men":
            if obj.ratio_men > 85:
                stat_gender.append(obj)
    return stat_gender

def readStatisticTerms():
    statistic_occ_list = []
    statistic_obj_dict = {}
    f = open("statistics07-all-occupations.txt", "r")
    nr = 0 
    for row in f: #occupation  #total  #women-%  #women-mean-age  #men-%  #men-mean-age
        if nr > 2:
            i = 0
            for chr in row:
                if chr.isdigit():
                    i = row.index(chr)
                    break
            occ = row[0 : i-1]
            digit_string = row[i:].strip("\n")
            digit_list = digit_string.split()
            last_index = len(digit_list)
            men_ratio = int(digit_list[last_index-2])
            women_ratio = 100-men_ratio
            occ_sta = OccupationStatistic(occ,women_ratio,men_ratio)
            statistic_obj_dict[occ] = (occ_sta)
            statistic_occ_list.append(occ)
        nr +=1
    return statistic_obj_dict

def main():
    gender = "Men"
    statistic_obj_dict = readStatisticTerms()
    ads_obj_dict, ads_occ_list = readAdTerms()
    stat_gender = returnDominatedOccupations(statistic_obj_dict, gender)
    #return_similarity_match(stat_gender, ads_occ_list, ads_obj_dict, gender)
    return_manual_match(stat_gender,ads_occ_list, ads_obj_dict,gender)
    #for obj in statistic_obj_list:
     #   print(str(obj.occupation) + ": " + str(obj.ratio_women) + " " + str(obj.ratio_men))
    

main()
