from flask import Flask, request, render_template,redirect,session,url_for
import os,pip,sys,time
import urllib,re
try:
    from bs4 import BeautifulSoup
except:
    package='beautifulsoup4-4.4.1-py3-none-any.whl '
    pip.main(['install','--user',package])
    raise ImportError("Restarting")



app = Flask(__name__)

country_dic={"England":"1","Australia":"2","South Africa":"3","West Indies":"4","New Zealand":"5","India":"6","Pakistan":"7","Sri Lanka":"8"}

format_dic={"ODI":"2","Test":"1"}

rankings_test = {"India" : 1, "South Africa" : 2, "Australia" : 3, "New Zealand" : 4, "England" : 5,"Sri Lanka" : 6, "Pakistan" : 7,"West Indies" : 8,"Bangladesh" : 9}

rankings_odi = {"India" : 1, "South Africa" : 2, "England" : 3, "New Zealand" : 4, "Australia" : 5, "Pakistan" : 6,"Bangladesh" : 7,"Sri Lanka" : 8,"West Indies" : 9}

condition_count = {"India" : "spin", "South Africa" : "fast", "Australia" : "fast", "New Zealand" : "fast", "England" : "fast","Sri Lanka" : "spin", "Pakistan" : "spin","West Indies" : "medium","Bangladesh" : "spin","UAE" : "spin"}

ground = {'Thiruvananthapuram':'India','Kochi':'India','Visakhapatnam':'India','Margao':'India','Chandigarh':'India','Ahmedabad':'India','Kanpur':'India','Delhi':'India','Nagpur':'India','Mohali':'India','Jaipur':'India','Pune':'India','Rajkot':'India','Vadodara':'India','Hyderabad (Deccan)':'India','Bengaluru':'India','Mumbai (BS)':'India','Kolkata':'India','Mumbai':'India','Faridabad':'India','Guwahati':'India','Gwalior':'India','Indore':'India','Cuttack':'India','Chennai':'India','Dharamsala':'India','Ranchi':'India','Jamshedpur':'India','Johannesburg':'South Africa','Centurion':'South Africa','Cape Town':'South Africa','Port Elizabeth':'South Africa','Durban':'South Africa','Bloemfontein':'South Africa','Benoni':'South Africa','East London':'South Africa','Kimberley':'South Africa','Pietermaritzburg':'South Africa','Potchefstroom':'South Africa','Paarl':'South Africa','Southampton':'England','Bristol':'England','Birmingham':'England','Manchester':'England','Leeds':'England','The Oval':'England',"Lord's":'England','Chester-le-Street':'England','Cardiff':'England','Nottingham':'England','Kuala Lumpur':'Australia','Brisbane':'Australia','Melbourne':'Australia','Adelaide':'Australia','Sydney':'Australia','Perth':'Australia','Canberra':'Australia','Colombo (RPS)':'Sri Lanka','Pallekele':'Sri Lanka','Dambulla':'Sri Lanka','Kingston':'West Indies','North Sound':'West Indies','Port of Spain':'West Indies','Harare':'Zimbabwe','Dhaka':'Bangladesh','Auckland':'New Zealand','Hamilton':'Ireland','Wellington':'New Zealand','Napier':'New Zealand','Aukland':'New Zealand','Hambantota':'Sri Lanka','Colombo (PSS)':'Sri Lanka','Hobart':'Sri Lanka','Galle':'Sri Lanka','Gros Islet':'West Indies','Bridgetown':'West Indies','Roseau':'West Indies',"St John's":'West Indies','Basseterre':'West Indies','Christchurch':'New Zealand','Karachi':'Pakistan','Glasgow':'scotland','Belfast':'Ireland','Colombo (SSC)':'Sri Lanka','Abu Dhabi':'uae','Multan':'Pakistan','Lahore':'Pakistan','Peshawar':'Pakistan','Rawalpindi':'Pakistan','Bulawayo':'Zimbabwe','Chittagong':'Bangladesh',}

batting_pos=[47,47,50,50,45,42,40,30]

def rankCoeff(teamRank,oppRank):
    return (10-(teamRank-oppRank))/100

def conditionCoeff(team,opp):
    if condition_count[team]==condition_count[opp]:
        return 1
    else:
        return 0.5

def awayPerfCoeff(awayAvg,rwithteam,careerAvg,conditionCoeff,bp):
    return ((awayAvg/batting_pos[bp-1])**(3/2)*(rwithteam)**(1/3))*conditionCoeff

def homePerfCoeff(homeAvg,careerAvg,conditionCoeff,bp):
    return ((homeAvg/batting_pos[bp-1])**(3/2))*conditionCoeff

def recentFormCoeff(recentForm,careerAvg,conditionCoeff,bp):
    return ((recentForm/batting_pos[bp-1])**(1/3))/(conditionCoeff**(1/2))

def outputSigmoid(v):
    return v

def neuralNet(pc,rfc,cc,rc,bpcoeff):
    weights=[4,12,1,0.75,5]
    coeff=[pc,rfc,cc,rc,bpcoeff]

    potential=0
    for i in range(5):
        potential=potential+(weights[i]*coeff[i])
    outp=outputSigmoid(potential)
    outp=outp/22.75
    outp=float(format(outp,'.2f'))
    return outp

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


def getCareerAvg(playerno,name,country,format1):
    playername=name
    """http://www.espncricinfo.com/india/content/player/28081.html"""
    link="http://www.espncricinfo.com/"+country.lower()+"/content/player/"+str(playerno)+".html"
    page=urllib.request.urlopen(link)
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

def HomeAwayAverage(playerno,name,country,format1):
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

def getAverageLast5WithTeam(playerno,country,opp,format1):
    statslink="http://stats.espncricinfo.com/ci/engine/player/"+str(playerno)+".html?class="+format_dic[format1]+";template=results;type=batting;view=innings"

    page=urllib.request.urlopen(statslink)
    soup=BeautifulSoup(page,"html.parser")
    score=[]
    innings=5
    c=0
    no=0
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
                no=no+1
            c=c+1
        if c==5:
            break
    sum=0
    innings=c-no
    if innings==0:
        innings=1
    for i in range(len(score)):
        sum=sum+score[i]
   
    return sum/innings


def getAverageLast5(playerno,country,format1):

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

def getRecentFormInOpposition(playerno,format1,country,opp):
    url = "http://stats.espncricinfo.com/ci/engine/player/"+str(playerno)+".html?class="+format_dic[format1]+";template=results;type=batting;view=innings"
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'html.parser')
    g=soup.find_all("tr",{"class":"data1"})
    total=[];
    count=0;
    innings=0

    for i in range(len(g) - 1, 0, -1):
        if(count == 5):
            break
        tuple = g[i].find_all("td")
        try:
            if (opp == ground[tuple[11].text] and tuple[10].text == ("v " + opp)):

                if("*" not in str(re.findall('[0-9]+\**', tuple[0].text))):
                    innings = innings + 1

                count +=1
                total = total + (re.findall('[0-9]+', tuple[0].text))
        except:
            continue

    sum=0
    if len(total)==0:
        return -1

    else:
        for i in total:
            sum = sum + int(i)

        return sum/innings

@app.route('/',methods=["POST","GET"])
def player_analysis(name=None,avglast5=None,avglast5withteam=None,opp=None,place=None,homeavg=None,awayavg=None,avgwithteam=None,format1=None):
    if request.method=="POST":
        name=request.form["name"]
        name=name.split(" ")
        name = name[0].upper() +" "+ name[1].title()

        country=request.form["country"]
        opp=request.form["opposition"]
        format1=request.form["format"]
        place=request.form["place"]
        playerno=getPlayerNo(name,country)
        avgwithteam=getRecentFormInOpposition(playerno,format1,country,opp)
        avglast5=getAverageLast5(playerno,country,format1)
        avglast5withteam=getAverageLast5WithTeam(playerno,country,opp,format1)
        avg=HomeAwayAverage(playerno,name,country,format1)
        homeavg=avg[0]
        awayavg=avg[1]
        career_avg=getCareerAvg(playerno,name,country,format1)
        if avgwithteam==-1:
            if place=="Away":
                avgwithteam=avglast5
            else:
                avgwithteam=avglast5
        bp=request.form["bp"]
        bp=int(bp)
        desired_avg=batting_pos[bp-1]
        bpcoeff=desired_avg/avglast5
        pc=0
        if place=="Away":
            pc=awayPerfCoeff(avgwithteam,avglast5withteam,career_avg,conditionCoeff(country,opp),bp)
        else:
            pc=homePerfCoeff(homeavg,career_avg,conditionCoeff(country,opp),bp)
        rfc=recentFormCoeff(avglast5,career_avg,conditionCoeff(country,opp),bp)
        cc=conditionCoeff(country,opp)
        rc=0
        if format1=="ODI":
            rc=rankCoeff(rankings_odi[country],rankings_odi[opp])
        else:
            rc=rankCoeff(rankings_test[country],rankings_test[opp])
        rating=neuralNet(pc,rfc,cc,rc,bpcoeff)
        return render_template("playerrate.html",rating=rating,format1=format1,name=name,avglast5=avglast5,avglast5withteam=avglast5withteam,opp=opp,place=place,career_avg=career_avg,homeavg=homeavg,awayavg=awayavg,avgwithteam=avgwithteam)

    else:
        return render_template("playerrate.html")
"""
@app.route('/try1',methods=["POST","GET"])
def try1(name=None,avglast5=None,avglast5withteam=None,opp=None,place=None,homeavg=None,awayavg=None,avgwithteam=None,format1=None):
    if request.method=="POST":
        name=request.form["name"]
        name=name.split(" ")
        name = name[0].upper() +" "+ name[1].title()
        country=request.form["country"]
        opp=request.form["opposition"]
        format1=request.form["format"]
        place=request.form["place"]
        avgwithteam=request.form["last5teamavg"]
        avglast5=getAverageLast5(name,country,format1)
        avglast5withteam=getAverageLast5WithTeam(name,country,opp,format1)
        avg=HomeAwayAverage(name,country,format1)
        homeavg=avg[0]
        awayavg=avg[1]
        career_avg=getCareerAvg(name,country,format1)
        return render_template("try.html",format1=format1,name=name,avglast5=avglast5,avglast5withteam=avglast5withteam,opp=opp,place=place,career_avg=career_avg,homeavg=homeavg,awayavg=awayavg,avgwithteam=avgwithteam)

    else:
        return render_template("try.html")

"""
if __name__ == '__main__':
  app.run()
