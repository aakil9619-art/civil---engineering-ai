def performance_profile(answers):
    by_topic={}
    for a in answers:
        t=a.get("topic","Unknown"); x=by_topic.setdefault(t,{"topic":t,"attempted":0,"correct":0,"time":0})
        x["attempted"]+=1; x["correct"]+=int(a.get("is_correct",False)); x["time"]+=float(a.get("time_seconds",0))
    result=[]
    for x in by_topic.values():
        x["accuracy"]=round(100*x["correct"]/x["attempted"],2) if x["attempted"] else 0
        x["avg_time"]=round(x["time"]/x["attempted"],2) if x["attempted"] else 0
        x["status"]="Strong" if x["accuracy"]>=80 else ("Needs Practice" if x["accuracy"]<60 else "Developing")
        result.append(x)
    return sorted(result,key=lambda x:x["accuracy"])
