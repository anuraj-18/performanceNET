from flask import Flask, request, render_template,redirect,session,url_for

import urllib2
import requests
"""
from bs4 import BeautifulSoup
"""
app = Flask(__name__)
"""
def getPlayerNo(name,country):
    playername=name.lower()

    link="http://www.espncricinfo.com/india/content/player/caps.html?country="+country_dic[country]+";class=1"

    page=urllib.request.urlopen(link)
    soup=BeautifulSoup(page,"html.parser")

    name=soup.find_all("li",attrs={"class":"ciPlayername"})
    newlink=""
    for i in range(len(name)):
        if playername in str(name[i]).lower():
            c=0
            for j in range(len(str(name[i]))):
                if str(name[i])[j]=="\"":
                    c=c+1
                    if c==5:
                        for k in range(j+1,len(str(name[i]))):
                            newlink=newlink+str(name[i])[k]
                            if(str(name[i])[k+1]=='"'):
                                break

    playerno=""
    for i in range(len(newlink)-6,-1,-1):
        playerno=playerno+newlink[i]
        if newlink[i-1]=="/":
            break
    playerno=int(playerno[::-1])
    return playerno

def getCareerAvg(name,country,format1):
    playername=name

    link="http://www.espncricinfo.com/india/content/player/caps.html?country="+country_dic[country]+";class=1"

    page=urllib.request.urlopen(link)
    soup=BeautifulSoup(page,"html.parser")

    name=soup.find_all("li",attrs={"class":"ciPlayername"})
    newlink=""
    for i in range(len(name)):
        if playername in str(name[i]):
            c=0
            for j in range(len(str(name[i]))):
                if str(name[i])[j]=="\"":
                    c=c+1
                    if c==5:
                        for k in range(j+1,len(str(name[i]))):
                            newlink=newlink+str(name[i])[k]
                            if(str(name[i])[k+1]=='"'):
                                break

    playerno=""
    for i in range(len(newlink)-6,-1,-1):
        playerno=playerno+newlink[i]
        if newlink[i-1]=="/":
            break
    playerno=int(playerno[::-1])


    newlink="http://www.espncricinfo.com"+newlink
    page=urllib.request.urlopen(newlink)
    soup=BeautifulSoup(page,"html.parser")

    name=soup.find_all("tr",attrs={"class":"data1"})
    if format1=="ODI":
        k=str(name[1].find_all("td",attrs={"nowrap":"nowrap"})[6])
    else:
        k=str(name[0].find_all("td",attrs={"nowrap":"nowrap"})[6])
    k=k[:len(k)-5]
    avg=""
    for i in range(len(k)-1,-1,-1):
        avg=avg+k[i]
        if(k[i-1]==">"):
            break
    avg=avg[::-1]
    avg=avg.strip()
    avg=float(avg)
    return avg

def HomeAwayAverage(name,country,format1):
    playerno=getPlayerNo(name,country)
    homeavg=0
    awayavg=0
    statslink="http://stats.espncricinfo.com/ci/engine/player/"+str(playerno)+".html?class="+format_dic[format1]+";template=results;type=batting"
    page=urllib.request.urlopen(statslink)
    soup=BeautifulSoup(page,"html.parser")

    name=soup.find_all("tr",attrs={"class":"data1"})
    for i in range(len(name)):
        if "home".lower() in str(name[i]).lower():
            homeavg=name[i].find_all("td")[7].text
            homeavg=float(homeavg)

        if "away" in str(name[i]).lower():
            awayavg=name[i+1].find_all("td")[7].text
            awayavg=float(awayavg)
            break

    avg=[homeavg,awayavg]
    return avg

def getAverageLast5WithTeam(name,country,opp,format1):
    playerno=getPlayerNo(name,country)

    statslink="http://stats.espncricinfo.com/ci/engine/player/"+str(playerno)+".html?class="+format_dic[format1]+";template=results;type=batting;view=innings"

    page=urllib.request.urlopen(statslink)
    soup=BeautifulSoup(page,"html.parser")
    score=[]
    innings=5
    c=0
    name=soup.find_all("tr",attrs={"class":"data1"})
    for i in range(len(name)-1,0,-1):
        k=str(name[i].find_all("a", attrs={"class":"data-link"})[0])
        k=k[:len(k)-4]
        team=""
        for j in range(len(k)-1,0,-1):
            team=team+k[j]
            if k[j-1]==">":
                break
        team=team[::-1]
        if team==opp:
            k=name[i].find_all("td",attrs={"class":"padAst"})
            print(k)
            if k:
                k=k[0]
                k=str(k)
                k=k[19:]
                k=k[0:len(k)-5]
                if k=='DNB':
                    continue
                score.append(int(k))

            else:
                k=name[i].find_all("td")
                k=k[0]
                k=str(k)
                k=k[4:]
                k=k[0:len(k)-6]
                score.append(int(k))
                innings=innings-1
            c=c+1
        if c==5:
            break
    sum=0
    for i in range(5):
        sum=sum+score[i]
    if innings==0:
        innings=1
    return sum/innings


def getAverageLast5(name,country,format1):
    playerno=getPlayerNo(name,country)

    statslink="http://stats.espncricinfo.com/ci/engine/player/"+str(playerno)+".html?class="+format_dic[format1]+";template=results;type=batting;view=innings"

    page=urllib.request.urlopen(statslink)
    soup=BeautifulSoup(page,"html.parser")

    name=soup.find_all("tr",attrs={"class":"data1"})

    score=[]
    k=""
    innings=5
    for i in range(len(name)-1,0,-1):
        k=name[i].find_all("td",attrs={"class":"padAst"})
        if k:
            k=k[0]
            k=str(k)
            k=k[19:]
            k=k[0:len(k)-5]
            if k=='DNB':
                continue
            score.append(int(k))
        else:
            k=name[i].find_all("td")
            k=k[0]
            k=str(k)
            k=k[4:]
            k=k[0:len(k)-6]
            score.append(int(k))
            innings=innings-1
        if len(score)==5:
            break
    sum=0
    for i in range(5):
        sum=sum+score[i]
    if innings==0:
        innings=1
    return sum/innings
"""

@app.route('/')
def player_analysis():
  return render_template("playerrate.html")

if __name__ == '__main__':
  app.run()
