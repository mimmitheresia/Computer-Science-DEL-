import difflib as dl

class OccupationStatistic:
    def __init__(self, occ, w, m ): 
        self.occupation = occ
        self.ratio_women = w 
        self.ratio_men = m

class OccupationAds:
    def __init__(self,occ,nr):
        self.occupation = occ
        self.occ_nr = nr

def readStatistics():
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
    return statistic_obj_dict, statistic_occ_list

def readTotalAds():
    ads_obj_dict = {}
    ads_occ_list = []
    f = open("total-nr-by-occupation.txt", "r")
    for row in f:
        index = row.rfind(":")
        occ = row[:index].strip()
        occ_nr = int(row[index+1:])
        occ_ads = OccupationAds(occ,occ_nr)
        ads_obj_dict[occ] = occ_ads
        ads_occ_list.append(occ)
    return ads_obj_dict, ads_occ_list

def matchOccupationLabels(w, m,ad_occ, ad_obj):
    first = w[5]
    i  = 1
    for obj in m:
        print(" ")
        print(str(i) + ". Dominated occupation by: " + str(obj.occupation) + ": " + str(obj.ratio_women))
        #print(st)
        match = dl.get_close_matches(obj.occupation, ad_occ, cutoff = 0.1, n=10)
        print("Similar match in ad labels:")
        for element in match:
            obj = ad_obj.get(element)
            print(element + ': ' + str(dl.SequenceMatcher(None, obj.occupation, element).ratio()) + " occupation frequency: " + str(obj.occ_nr) )
        i += 1

def returnDominated(statistic_obj_dict):
    w_dominated = []
    m_dominated =[]

    for label in statistic_obj_dict:
        obj = statistic_obj_dict.get(label)
        if obj.ratio_women > 85:
            w_dominated.append(obj)
        if obj.ratio_men > 85:
            m_dominated.append(obj)
    return w_dominated,m_dominated



def main():
    statistic_obj_dict, statistic_occ_list = readStatistics()
    ads_obj_dict, ads_occ_list = readTotalAds()
    w_dominated, m_dominated = returnDominated(statistic_obj_dict)
    matchOccupationLabels(w_dominated, m_dominated,ads_occ_list, ads_obj_dict)
    #for obj in statistic_obj_list:
     #   print(str(obj.occupation) + ": " + str(obj.ratio_women) + " " + str(obj.ratio_men))
    

main()
