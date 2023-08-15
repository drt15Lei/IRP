#program takes 2 arguments, the ID of a PMC 'xxxxxxxx_bioc.json' output and the DOI HTML of the same paper 'xxxxxxxx_DOI.html', and the suffix for the config name, requires both files and 'config_template_mod.json' to be in the same directory
from lxml import etree, html
import json
import spacy
import re
import argparse
from lxml.etree import _Attrib
import os.path
nlp = spacy.load('en_core_web_md')
stop_words = spacy.lang.en.stop_words.STOP_WORDS

##########################################################
#Input a string of text, output that string with stop words removed
def remove_stopwords(text):
    words = text.split()
    filtered_words = []
    for word in words:
        if word.lower() not in stop_words:
            filtered_words.append(word)
    return " ".join(filtered_words)

##########################################################
#A way of measuring how similar 2 passages are, based on number of unique words, input 2 strings of 1 or more words seperated by spaces, output a ratio of how many unqiue words are in common between the 2 divided by total unique words in both
def sentence_sim(sen1, sen2):
    words1 = set(sen1.lower().split())
    words2 = set(sen2.lower().split())
    
    comm = len(words1.intersection(words2))
    total = len(words1.union(words2))

    # Return 0 if total == 0 to avoid dividing by 0
    if total == 0:
        return 0
    else:
        return comm / total
    
##########################################################    

#Inputs a given set of passages and attempts to find a match in the element tree, and outputs the tag and attributes of the match which is deepest in the tree (longest XPath)
def find_match(text, thresh, links_allowed):

    #Function to help detect if element has an 'a' tag nested within it, to try and avoid headers being detected as the content table hyperlinks
    def descendant_check(element):
            if links_allowed == True:
                return False
            for child in element.iterdescendants():
                if child.tag == 'a':
                    return True
            return False
        
    #initialise the list of longest matches  
    longest_matches = []  

    for content in text:
        #reset longest match for new query
        longest_match = None  
        #reset longest XPath to 0
        longest_path_length = 0  

        for element in tree.iter():
            if element.tag != etree.Comment and element.tag != 'a' and element.tag != 'li' and not descendant_check(element):  #To avoid html comment, no text, and hyperlinks (contents table problem)
                element_text = ''.join(t for t in element.itertext())
                cleaned_element_text = remove_stopwords(element_text)
                cleaned_content = remove_stopwords(content)
                similarity = sentence_sim(cleaned_element_text, cleaned_content)
                if content == element_text or similarity > thresh:
                    path = element.getroottree().getpath(element)
                    path_length = len(path.split('/'))
                    if path_length > longest_path_length:
                        longest_path_length = path_length
                        match = [element.tag, dict(element.attrib)]
                        longest_match = match
        
        longest_matches.append(longest_match)

    return longest_matches


#Seperate version of function above that does not allow the matched element to be a 'p' tag, to avoid sections being defined as paragraphs
def find_match_sec(text, thresh, links_allowed):

        
    #initialise the list of longest matches    
    longest_matches = []  

    for content in text:
        longest_match = None  
        #reset longest XPath to 0
        longest_path_length = 0  

        for element in tree.iter():
            if element.tag != etree.Comment and element.tag != 'a' and element.tag != 'p' and element.tag != 'li':  #To avoid html comment, no text, and hyperlinks (contents table problem)
                element_text = ''.join(t for t in element.itertext())
                cleaned_element_text = remove_stopwords(element_text)
                cleaned_content = remove_stopwords(content)
                similarity = sentence_sim(cleaned_element_text, cleaned_content)
                if content == element_text or similarity > thresh:
                    path = element.getroottree().getpath(element)
                    path_length = len(path.split('/'))
                    if path_length > longest_path_length:
                        longest_path_length = path_length
                        match = [element.tag, dict(element.attrib)]
                        longest_match = match
        
        longest_matches.append(longest_match)

    return longest_matches










##################################################################################  
#Input a list of matches from find_match function
#Outputs tags and attributes dictionaries in a list, in the format needed for the config file          
#Normalises 'id' tag values into a regex, only works with common prefix
def filter_match(matches):
    regex_pattern = '.*'
    for item in matches:
        if type(item) is list and 'id' in item[1]:
            templ = item[1]['id']
            match = re.match('[^0-9\[\]]*', templ)
            if match:
        # appends the match of hopefully the ID prefix to expression that means any digits
                 regex_pattern = match.group(0) + '[0-9]+'
    for item in matches:
        if item is not None and 'id' in item[1].keys():
            item[1]['id'] = regex_pattern
            
    new = []
    for i in matches:
        if i is not None and i not in new:
         new.append(i)

    new_data = []

    for item in new:
        if item is not None:
            new_item = {'tag': item[0], 'attrs': item[1]}
            new_data.append(new_item)
    return new_data


 





##################################################################################

parser = argparse.ArgumentParser(description="A simple argument parser")
parser.add_argument('prefix')
parser.add_argument('journal')
args = parser.parse_args()

with open(args.prefix + '_PMC_bioc.json') as json_file:
#with open('20709820_PMC_bioc.json') as json_file:
    bioc_data = json.load(json_file)
pas = bioc_data['documents'][0]['passages']

#unused currently
#if os.path.isfile(args.prefix + '_PMC_tables.json'):
    #with open(args.prefix + '_PMC_tables.json', 'r', encoding='utf-8') as json_file:
if os.path.isfile('20709820' + '_PMC_tables.json'):
    with open('20709820_PMC_tables.json', 'r', encoding='utf-8') as table_file:
        table_data = json.load(table_file)

with open('config_template_mod.json') as json_file:
    template = json.load(json_file)


################################################################################

#json stuff

#Title
title = []
for entry in pas:
        if entry['infons'].get('iao_id_1') == 'IAO:0000305':
            title.append(entry['text'])
            
#Keywords
keyw = []
for entry in pas:
        if entry['infons'].get('iao_id_1') == 'IAO:0000630':
            keyw.append(entry['text'])  
                      
# List of all Headers and Sub
head_list = []
sub_list = []
for entry in pas:
        head_list.append(entry['infons'].get('section_title_1'))
        sub_list.append(entry['infons'].get('section_title_2'))
        
head_list = [value for value in head_list if value is not None]
sub_list = [value for value in sub_list if value is not None]

head_list = list(set(head_list))
sub_list = list(set(sub_list))

            


#IAO for Abs, Int, Method, Res, Disc
sec = ['IAO:0000315','IAO:0000316','IAO:0000317','IAO:0000318','IAO:0000319']
  
#sec_dict is a list, one index for all the text from each section combined, for defined by section
#full_para contains every seperate paragraph from these sections as a list
sec_dict = []
full_para = []
for iao in sec:   
    temp = []
    for entry in pas:
        if entry['infons'].get('iao_id_1') == iao:
            temp.append(entry['text'])
            full_para.append(entry['text'])
    sec_dict.append(' '.join(temp))

#Same as above but uses the sub section headers to attempt to extract sub sections as 1 long string
sub_sec_list = []            
for sh in sub_list:
    temp = []
    for entry in pas:
        if entry['infons'].get('section_title_2') == sh:
            temp.append(entry['text'])
    sub_sec_list.append(' '.join(temp))
            
  

# List of all References 
ref_list = []
for entry in pas:
        if entry['infons'].get('iao_id_1') == 'IAO:0000320':
            ref_list.append(entry['text'])


#################################################################################

#Define which parser to use
parser = etree.HTMLParser(remove_blank_text=False)
#Create the element tree from the DOI HTML ready to be searched
tree = etree.parse(args.prefix + '_DOI.html', parser) 



#Title
template['config']['title']['defined-by'] = filter_match(find_match(title, 0.3, False))
#Paragraphs
template['config']['paragraphs']['defined-by'] = filter_match(find_match(full_para, 0.3, True))
#Keywords
template['config']['keywords']['defined-by'] = filter_match(find_match(keyw, 0.3, False))
#Headers and Sub-headers
template['config']['sections']['data']['headers'] = filter_match(find_match(head_list, 0.3, False))
template['config']['sub-sections']['data']['headers'] = filter_match(find_match(sub_list, 0.3, False))
# Sections and Sub-sections
template['config']['sections']['defined-by'] = filter_match(find_match_sec(sec_dict, 0.3, True))
template['config']['sub-sections']['defined-by'] = filter_match(find_match_sec(sub_sec_list, 0.3, True))
#References
template['config']['references']['defined-by'] = filter_match(find_match(ref_list, 0.3, True))



#writes to file with naming scheme similar to pre existing configs, suffix determined by arg 'journal'
with open('config_' + args.journal + '.json', "w") as file:
    json.dump(template, file, indent=3)


