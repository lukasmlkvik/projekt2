import json
import pandas
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import math
import statistics


"""******************** pomocne funkcie ********************"""
def recordToJson(record, names):
    row = {};
    for n in names:
        if n in record:
            row[n] = record[n]
        else:
            row[n] = None;
    return row

def rankRow(row, alfa = 0.5):

    r1 = row["pomer"]
    r2 = 1
    pom = row["distance"]
    if pom <row["motiv.leg_distance"]:
        pom = row["motiv.leg_distance"]
    if pom!=0:
        r2 = 1 - (abs(row["distance"]-row["motiv.leg_distance"])/pom)

    return alfa * r1 + (1-alfa) * r2




"""******************** nacinatine dat ********************"""

legs = pandas.read_csv("legs.csv")

f = open("final1.json");
jsonData = json.load(f);
f.close();
f = open("final2.json");
jsonData = [*jsonData,*json.load(f)]
f.close();


"""******************** filtrovanie ********************"""

print(len(jsonData))

pom = jsonData
jsonData = []
for d in pom:
    if len(d["alternatives"])!=0:
        jsonData.append(d)

print(len(jsonData))


"""******************** spojenie dat ********************"""

"""stlpce, ktore sa pridaju do jsonu"""
columns = ["motid","leg_distance","worthwhileness_rating"];

"""premapovanie transport kategory na slopocny format (motiv)"""
transportMap =  [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37]

"""premapovanie transport kategory na slopocny format (json)"""
transportMap2= {'bike': 1, 'walking': 7, 'car': 9, 'train': 10, 'taxi': 23, 'genericpubtrans': 4,
                'bus': 15, 'subway': 12, 'tram': 11, 'carsharing': 25, 'bikesharing': 17, 'boat': 13}


mapa = {}
for i in range(0,len(legs)):
    mapa[legs["legid"][i]] = legs.iloc[i][columns]


"""spojenie dat do jsonu"""
for d in jsonData:
    motiv ={}
    if(mapa.__contains__(d["legId"])):
        motiv = recordToJson(mapa[d["legId"]],columns)
        motiv["motid"] = transportMap[motiv["motid"]]
    else:
        motiv = recordToJson({}, columns)

    d["motiv"] = motiv
    for a in d["alternatives"]:
        for s in a["segments"]:
            s["transport"] = transportMap2[s["transport"]]

"""******************** filtrovanie2 ********************"""
pom = jsonData
jsonData = []
for d in pom:
    if d["motiv"]["motid"]!=None:
        jsonData.append(d)

print(len(jsonData))
"""******************** vytvorenie ohodnotenia ********************"""

def rankFunction(motiv, alternativa, alfa = 0.5):
    poc = len(alternativa["segments"])

    poc2 = 0;
    sum = 0
    sum2 = 0
    dur = 0
    dur2 = 0
    for s in alternativa["segments"]:
        sum = sum + s["distance"]
        dur = dur + s["duration"]
        if motiv["motid"] == s["transport"]:
            poc2 = poc2 + 1
            sum2 = sum2 + s["distance"]
            dur2 = dur2 + s["duration"]
    sum = sum * 1000
    sum2 = sum2 * 1000
    alternativa["pomer"] = None;
    alternativa["distance"] = sum;
    alternativa["distanceMotId"] = sum2;
    alternativa["travelDuration"] = dur;
    alternativa["travelDurationMotId"] = dur2;
    r1 = 1
    if poc!=0:
        r1 = poc2/poc
        alternativa["pomer"] = r1
    r2 = 1
    pom = sum
    if pom <motiv["leg_distance"]:
        pom = motiv["leg_distance"]
    if pom!=0:
        r2 = 1 - (abs(sum-motiv["leg_distance"])/pom)

    return alfa * r1 + (1-alfa) * r2


for d in jsonData:
    for a in d["alternatives"]:
        a["rank"] = rankFunction(d["motiv"],a);


"""******************** transformovanie na tabulku (jedna alternativa = jeden riadok)********************"""

def getAtribute(obj, atr,oddelovac = "."):
    a = atr.split(oddelovac)
    b = obj
    for i in a:
        b = b[i]
    return b

tabulka = pandas.DataFrame()

"""parametre z ktorych sa stanu stlpce (z hlavneho zaznamu)"""
selectedAtributesFromRoot = ["legId", "date","time",  "tripId","from.latitude","from.longitude","to.latitude","to.longitude","motiv.motid","motiv.leg_distance", "motiv.worthwhileness_rating"]

"""parametre z ktorych sa stanu stlpce (z alternativy)"""
selectedAtributesFromAlternative = ["id", "totals.co2", "totals.productivity","totals.price","totals.availableTime","totals.vias","totals.duration", "travelDuration","travelDurationMotId","pomer","distanceMotId","distance","rank"]

for a in [*selectedAtributesFromRoot,*selectedAtributesFromAlternative]:
    tabulka[a] = []



for d in jsonData:
    for a in d["alternatives"]:
        row = []
        for at in selectedAtributesFromRoot:
            row.append(getAtribute(d,at,"."))
        for at in selectedAtributesFromAlternative:
            row.append(getAtribute(a,at,"."))
        tabulka.loc[len(tabulka.index)] = row

print(tabulka)



"""
zefektivnit
spojit


popis datasetov - prezentacia (statistika) + vyhodnotenie prepojenia(id)

"""
