import json
import sys
import spacy_udpipe


class POS:
    def __init__(self):
        spacy_udpipe.download("sv") # download Swedish model
        self.nlp = spacy_udpipe.load("sv")
        #pass

def get_final_format(pos_list, terms):
    final_format = ""
    final_format += "{"

    i = 0
    for term in pos_list:
        final_format += str(terms[i]) + " " + str(term.lemma_) + "|"
        i += 1
    final_format = final_format[0:len(final_format)-1]
    final_format += "}"
    return final_format

def clean_input(pos, inp):
    terms = inp.split()
    lower_terms = []
    for term in terms:
        lower_terms.append(term.lower().strip('"-[@_!$%^&*()+,.<>?/\|}{~:]#'))
    print(" ")
    pos_list = pos.nlp(lower_terms)

    final_format = get_final_format(pos_list, terms)
    return final_format

def main():
    inp = ' '.join(map(str, sys.argv[1:len(sys.argv)]))
    pos = POS()
    limit = None
    output = clean_input(pos, inp) 
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdout.write(output)

main()
    