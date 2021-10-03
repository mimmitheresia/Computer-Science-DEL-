class OccupationMerge():
    def __init__(self):
        self.nr_by_occupation = {}
        self.text_by_occupation = {}
        self.head_by_occupation = {}

    def updateNumber(self,occ,nr):
        stored_nr = self.nr_by_occupation.get(occ)
        total_nr = stored_nr + nr 
        self.nr_by_occupation[occ] = total_nr
    
    def updateHead(self,occ,head):
        stored_head = self.head_by_occupation.get(occ)
        total_head = stored_head + head 
        self.head_by_occupation[occ] = total_head

    def updateText(self,occ,text):
        stored_text = self.text_by_occupation.get(occ)
        total_text = stored_text + text
        self.text_by_occupation[occ] = total_text
        
    def addOccNumber(self,row,row_nr):
        if (row_nr % 500 == 0):
            print("Adding number from row: " + str(row_nr))
        index = row.rfind(":")
        occ = row[:index].strip()
        occ_nr = int(row[index+1:])
        #if row.startswith('Projektledare'):
            #print("Occupation in number:" + str(occ)+ " " + str(len(occ)))
        if occ in self.nr_by_occupation:
            self.updateNumber(occ,occ_nr)
        else:
            self.nr_by_occupation[occ] = occ_nr

    def addOccHeads(self,row,row_nr):
        if (row_nr % 500 == 0):
            print("Adding headlines from row: " + str(row_nr))
        index = row.index("{")
        occ = row[:(index-1)].rstrip()
        occ_heads = row[index:].strip("\n")
        #if row.startswith('Projektledare'):
            #print("Occupation in heads:" + str(occ) + " " + str(len(occ)))
        if occ in self.head_by_occupation:
            self.updateHead(occ,occ_heads)
        else:
            self.head_by_occupation[occ] = occ_heads

    def addOccText(self,row, row_nr):
        if (row_nr % 500 == 0):
            print("Adding text from row: " + str(row_nr)) 
        row = row.split(":")
        if len(row) == 2:
            occ = row[0]
            occ_text = row[1].strip("\n")
        if len(row) > 2:
            occ_text = row[len(row)-1]
            occ = ""
            for w in row:
                occ += w
        if occ in self.text_by_occupation:
            self.updateText(occ,occ_text)
        else:
            self.text_by_occupation[occ] = occ_text
    
    def sort_desc(self):
        pass
        #sorted = sorted(occ_dic.items(),key=operator.itemgetter(1),reverse=True)



def merge_file_by_year(occ_mer,path, path_type):
    #Add from 2006-2007
    f = open(str(path)+"-06-07.txt", "r")
    print("Reading from " + str(path)+"-06-07.txt...")
    row_nr = 0 
    for row in f:
        if path_type == "nr":
            occ_mer.addOccNumber(row,row_nr)
        if path_type == "head":
            occ_mer.addOccHeads(row,row_nr)
        if path_type == "text":
            occ_mer.addOccText(row,row_nr)
        row_nr += 1
    f.close()

    #Merge from 2008
    f = open(str(path)+"-08.txt", "r")
    print("Reading from " + str(path)+"-08.txt..")
    row_nr = 0 
    for row in f:
        if path_type == "nr":
            occ_mer.addOccNumber(row,row_nr)
        if path_type == "head":
            occ_mer.addOccHeads(row,row_nr)
        if path_type == "text":
            occ_mer.addOccText(row,row_nr)
        row_nr += 1
    f.close()
    
    #Merge from 2009
    f = open(str(path)+"-09.txt", "r")
    print("Reading from " + str(path)+"-09.txt..")
    row_nr = 0 
    for row in f:
        if path_type == "nr":
            occ_mer.addOccNumber(row,row_nr)
        if path_type == "head":
            occ_mer.addOccHeads(row,row_nr)
        if path_type == "text":
            occ_mer.addOccText(row,row_nr)
        row_nr += 1
    f.close()

    #Merge from 2010
    f = open(str(path)+"-10.txt", "r")
    print("Reading from " + str(path)+"-10.txt..")
    row_nr = 0 
    for row in f:
        if path_type == "nr":
            occ_mer.addOccNumber(row,row_nr)
        if path_type == "head":
            occ_mer.addOccHeads(row,row_nr)
        if path_type == "text":
            occ_mer.addOccText(row,row_nr)
        row_nr += 1
    f.close()
    
def control_check(occ_mer):
    invalid = 0
    for occ in occ_mer.head_by_occupation:
        if occ not in occ_mer.nr_by_occupation:
            print(occ + " " + str(len(occ)))
            invalid +=1 

    print("Invalid: " + str(invalid))  
    
def main():
    occ_mer = OccupationMerge()
    path_list = ["nr-by-occupation", "head-by-occupation", "text-by-occupation" ]
    types = ["nr", "head", "text"]
    i = 0 
    for i in range(0,2):
        merge_file_by_year(occ_mer, path_list[i], types[i])
        if  types[i] == "nr":
            for occ in occ_mer.nr_by_occupation:
                
                print(str(occ)+ ": " + str(occ_mer.nr_by_occupation.get(occ)))
            print("Number of occupations: " + str(len(occ_mer.nr_by_occupation)))
    
        if  types[i] == "head":
            for occ in occ_mer.head_by_occupation:
                pass
                #print(str(occ)+ ": " + str(occ_mer.head_by_occupation.get(occ)))
            print("Number of occupations: " + str(len(occ_mer.head_by_occupation)))

        if  types[i] == "text":
            for occ in occ_mer.text_by_occupation:
                print(str(occ)+ ": " + str(occ_mer.text_by_occupation.get(occ)))
            print("Number of occupations: " + str(len(occ_mer.text_by_occupation)))  
        #control_check(occ_mer)
main()
