
import json 
import csv

#Function to get all unqiue abbreviations as a dictionary from 1 abbreviations output file
def get_abbreviations(file_path):
    with open(file_path, 'r') as file:
        dictionary = json.load(file)

    abbreviations = {}

    for document in dictionary["documents"]:
        for passage in document["passages"]:
            algorithm1 = passage.get('extraction_algorithm_1', '')
            algorithm2 = passage.get('extraction_algorithm_2', '')
            #filter out abbreviations exclusively extracted with 'abbreviations_section' algorithm
            if algorithm1 == 'fulltext' or algorithm2 == 'fulltext':
                abbreviations[(passage["text_short"]).strip(':').strip()] = passage["text_long_1"]

    return abbreviations

#initialise table
table_full = []
#iterate thorugh each journal
journals = ['American_journal_of_respiratory_and_critical_care_medicine', 'Blood','BMC_medical_genetics', 'Circulation_Cardiovascular_genetics','European_journal_of_human_genetics','Human_molecular_genetics','Journal_of_human_genetics','Molecular_psychiatry','Nature_communications','Scientific_reports','The_pharmacogenomics_journal','Translational_psychiatry']
for journal in journals:
    m = open(journal + '/matching_ids.txt', 'r') 
    id_list = m.read().splitlines()
    m.close()
    pmc_list =[journal + '_PMC']
    doi_list = [journal + '_UNIQUE_PMC']
    #iterate through IDs of matching files
    for id in id_list:
        #run function on both PMC and DOI version of output file 
        abbpmc = get_abbreviations(journal + '/PMC/' + id + '_PMC_abbreviations.json')
        abbdoi = get_abbreviations(journal + '/DOI/' + id + '_DOI_abbreviations.json')

        unique_keys_1 = set(abbpmc.keys()) - set(abbdoi.keys())
        unique_keys_2 = set(abbdoi.keys()) - set(abbpmc.keys())
        
        pmc_list.append(len(abbpmc))
        #doi_list.append(len(abbdoi))
        doi_list.append(len(unique_keys_1))
        
        #write the unique abbreviations of each paper to file in the journal subdirectory
        with open(str(journal + '/' + id + '_ab_compare.txt'), 'w') as outfile:
            outfile.write('Keys unique to ' + 'PMC' + ':\n')
            for key in unique_keys_1:
                outfile.write(key + '   :   ')
                outfile.write(abbpmc[key] + '\n')
        

            outfile.write('\nKeys unique to ' + 'DOI' + ':\n')
            for key in unique_keys_2:
                outfile.write(key + '   :   ')
                outfile.write(abbdoi[key] + '\n')
                
    table_full.append(pmc_list)
    table_full.append(doi_list)
    

# transpose table, not working as intended

transposed = table_full

# Write data to CSV file
with open('comparison_table.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(transposed)
