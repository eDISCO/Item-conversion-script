import csv
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from tabulate import tabulate
# loads email and initial+surname as dict for fuzzy matching later on
def loadnames ( filename ):
    # empty dictionary
    conv_table = {}
    with open(filename,'rt') as csvfile:
        spamreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in spamreader:
            conv_table[row[1] + ' ' + row[2]] = row[3]
    return conv_table
# Just list of buildings
def getbuildings ( ):
    buildings = [
        'Alexander Graham Bell building',
        'Alrick Building',
        'BioSpace',
        'Eng Structures Lab',
        'Erskine Williamson Building',
        'Faraday Building',
        'Fleeming Jenkin',
        'Flowave',
        'Hudson Beare Building',
        'James Clark Maxwell Building',
        'John Muir',
        'Mary Bruck',
        'Michael Swann Building',
        'Peter Wilson Building',
        'Sanderson Building',
        'Scottish Microelectronics Centre',
        'SMC',
        'Technology Transfer Centre',
        'William Rankine Building',
        'Unknown'
    ]
    return buildings
def getinstitutes ():
    institutes = {
        'Institute for Bioengineering' : 'IBIO',
        'Institute for Digital Communications' : 'IDCOM',
        'Institute for Energy Systems' : 'IES',
        'Institute for Infrastructure and Environment' : 'IIE',
        'Institute for Integrated Micro and Nano Systems' : 'INMS',
        'Institute for Materials and Processes' : 'IMP'
        }
    return institutes
def flatten_dict(conv_table):
    l = list()
    for key, value in conv_table.items():
        l.append(key)
    return l
names =  loadnames('data.csv')
flat_names = flatten_dict(names)
buildings = getbuildings()
with open('newconvert.csv','w') as outputfile, open('equipment.csv','rt') as inputfile:
    admin_name = 'Admin Account'
    admin_mail = 'fake@example.com'
    spamreader = csv.reader(inputfile,delimiter=',',quotechar='"')
    spamwriter = csv.writer(outputfile,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
    for row in spamreader:
        outlist = [None] * 50
        outlist[1] = row[3] # Manufacturer
        outlist[2] = row[4] # Model
        outlist[4] = row[2] # Description
        outlist[12] = row[14] # availability
        outlist[13] = row[20] # restrictions
        outlist[14] = row[17] # usergroup
        outlist[15] = row[19] # Access
        outlist[17] = row[1] # Category
        #outlist[18] = row[10] # Institute (may need conversion??)
        outlist[19] = "KB" # Site/Campus
        # outlist[20] building need fuzzy matching!!
        outlist[21] = row[11] # Room (raw location from input)
        outlist[27] = row[6] # Manufacturer website
        outlist[29] = row[18] # training_required?
        outlist[37] = row[7] # Asset ID
        outlist[38] = row[28] # Finance ID
        outlist[39] = row[5] # Serial No
        outlist[42] = row[24] # Date of Purchase
        outlist[43] = row[25] # Purchase_cost
        outlist[45] = row[23] # end_of_life
        outlist[46] = row[22] # maintenance
        outlist[49] = row[8] # comments
        # Fuzzy match building:
        if  not row[11]:
            row[11] = 'Unknown'
        # a -- results from fuzzy matching
        a = process.extractBests(row[11], buildings, limit=2)
        if a[0][0] == "SMC":
            outlist[20] = 'Scottish Microelectronics Centre'
        else:
            outlist[20] = a[0][0];
        # Fuzzy match names and emails:
        # Contact 1:
        flat_names = flatten_dict(names)
        b = process.extractBests(row[12],flat_names, limit=2, scorer=fuzz.token_set_ratio)
        custodian_score = b[0][1]
        outlist[22] = b[0][0] # contact 1 name
        outlist[23] = names[b[0][0]] # contact 1 email
        # Contact 2:
        if row[13]:
            c = process.extractBests(row[13],flat_names, limit=2, scorer=fuzz.token_set_ratio)
            technical_score = c[0][1]
            outlist[24] = c[0][0]
            outlist[25] = names[c[0][0]]
        else:
            outlist[24] = ''
            outlist[25] = ''
        Comment = "|Building: " + row[11] + "\n"\
                + "|Owner: " + row[12] + "\n"\
                + "|Technical: " + row[13] + "\n"
        outlist[49] += Comment
        # It manufacturer and model is not given, use
        # Description as title
        if not outlist[1] and not outlist[2]:
            outlist[0] = row[2]
        institutes = getinstitutes()
        if row[10]:
            d = process.extract(row[10],institutes, limit=2)
            outlist[18] = d[0][2]
        else:
            outlist[18] = 'School of Engineering'
        #Show data, prompt for corrections:
        row1 = [row[12], row[11], row[13]]
        row2 = [outlist[22], outlist[20], outlist[24]]
        print(tabulate([row1, row2]))
        print(b, c)
        ans = input('is everything correct?')
        if ans[0] == 'y':
            pass
        elif ans[0] == 's':
            outlist[22] = b[1][0]
            outlist[23] = names[b[1][0]]
        elif ans[0] == 'a':
            outlist[22] = admin_name
            outlist[23] = admin_mail
        if len(ans) == 1:
            pass
        elif ans[1] == 's':
            oustlist[24] = c[1][0]
            outlist[25] = names[c[1][0]]
        elif ans[1] == 'a':
            outlist[24] = admin_name
            outlist[25] = admin_mail
        elif ans[1] == 'e':
            outlist[24] = ''
            outlist[25] = ''
        print('\n\n\n')
        # Write out the data
        spamwriter.writerow(outlist)

