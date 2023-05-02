#retourne la pos d'une certaine valeur dans la dataframe
import pandas as pd


def get_positions(dt, value):
    
    listofpos = []

    result = dt.isin([value])#trans data en boole basé sur la val à cherch

    seriesobj = result.any()#retourne une data frame en tableau en boole

    positions = list(seriesobj[seriesobj == True].index)#ret les column ou la valeure est true

    #check chaque ligne pour la valeur true
    for pos in positions:
        rows = list(result[pos][result[pos] == True].index)

        for row in rows:
            listofpos.append((row,pos))#ajoute dans la liste la position des val true


    return listofpos#ret la liste des pos
