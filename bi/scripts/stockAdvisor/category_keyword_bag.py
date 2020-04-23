import json
import csv
print "In keywords bag!!"

CATEGORY1 = "Competition"
CATEGORY2 = "Expansion - geography/segment"
CATEGORY3 = "Financial & Market Performance"
CATEGORY4 = "Innovation & Product Launch"
CATEGORY5 = "Legal & Compliance"
CATEGORY6 = "Market Potential & Growth"
catJsonPath = "/home/marlabs/codebase/stock-advisor/jsondata/stockCategories_nl_understanding.json"
filterLimitOnKeywords = 20

cat1Keywords = []
cat2Keywords = []
cat3Keywords = []
cat4Keywords = []
cat5Keywords = []
cat6Keywords = []

def traverseKeywords(keywords):
    keywordText = []
    for keyword in keywords:
        keywordText.append(keyword["text"])
    return keywordText



def addCat1(keywords):
    cat1Keywords.extend(traverseKeywords(keywords))


def addCat2(keywords):
    cat2Keywords.extend(traverseKeywords(keywords))

def addCat3(keywords):
    cat3Keywords.extend(traverseKeywords(keywords))

def addCat4(keywords):
    cat4Keywords.extend(traverseKeywords(keywords))

def addCat5(keywords):
    cat5Keywords.extend(traverseKeywords(keywords))

def addCat6(keywords):
    cat6Keywords.extend(traverseKeywords(keywords))



options = {CATEGORY1: addCat1,
            CATEGORY2: addCat2,
            CATEGORY3: addCat3,
            CATEGORY4: addCat4,
            CATEGORY5: addCat5,
            CATEGORY6: addCat6
}
with open(catJsonPath) as data_file:
    data = json.load(data_file)
    #print data
for row in data:
    #print row["Category"]
    #for keyword in row["keywords"]:
    if row["Category"] != "":
        keywords = row["keywords"]
        if len(keywords) >20:
            keywords = keywords[:filterLimitOnKeywords]
        options[row["Category"]](keywords)

cat1Keywords = set(cat1Keywords)
cat2Keywords = set(cat2Keywords)
cat3Keywords = set(cat3Keywords)
cat4Keywords = set(cat4Keywords)
cat5Keywords = set(cat5Keywords)
cat6Keywords = set(cat6Keywords)
print "Total keywords for cat 1 : "
print len(cat1Keywords)
print "Total keywords for cat 2 : "
print len(cat2Keywords)
print "Total keywords for cat 3 : "
print len(cat3Keywords)
print "Total keywords for cat 4 : "
print len(cat4Keywords)
print "Total keywords for cat 5 : "
print len(cat5Keywords)
print "Total keywords for cat 6 : "
print len(cat6Keywords)

print "after deducting intersections......"

cat1Keywords = (cat1Keywords-cat2Keywords-cat3Keywords-cat4Keywords-cat5Keywords-cat6Keywords)
cat2Keywords = (cat2Keywords-cat1Keywords-cat3Keywords-cat4Keywords-cat5Keywords-cat6Keywords)
cat3Keywords = (cat3Keywords-cat2Keywords-cat1Keywords-cat4Keywords-cat5Keywords-cat6Keywords)
cat4Keywords = (cat4Keywords-cat2Keywords-cat3Keywords-cat1Keywords-cat5Keywords-cat6Keywords)
cat5Keywords = (cat5Keywords-cat2Keywords-cat3Keywords-cat4Keywords-cat1Keywords-cat6Keywords)
cat6Keywords = (cat6Keywords-cat2Keywords-cat3Keywords-cat4Keywords-cat5Keywords-cat1Keywords)

print "Total keywords for cat 1 : "
print len(cat1Keywords)
print "Total keywords for cat 2 : "
print len(cat2Keywords)
print "Total keywords for cat 3 : "
print len(cat3Keywords)
print "Total keywords for cat 4 : "
print len(cat4Keywords)
print "Total keywords for cat 5 : "
print len(cat5Keywords)
print "Total keywords for cat 6 : "
print len(cat6Keywords)
cat1Keywords = list(cat1Keywords)
#print cat1Keywords[0]
#for item in cat1Keywords:
    #item = item.encode("ascii")
tests={CATEGORY1: cat1Keywords,
       CATEGORY2: cat2Keywords,
       CATEGORY3:cat3Keywords,
       CATEGORY4:cat4Keywords,
       CATEGORY5:cat5Keywords,
       CATEGORY6:cat6Keywords}
with open('/home/marlabs/Desktop/concept_keywords.csv','w') as fout:
    writer=csv.writer(fout)
    writer.writerows([tests.keys()])
    for row in zip(*tests.values()):
        row=[s.encode('utf-8') for s in row]
        writer.writerows([row])
