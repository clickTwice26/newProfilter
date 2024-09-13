def search(msg : str,wordlist : list) -> bool:
    wlist = []
    msg = msg.replace("*", "")
    msg = msg.replace("@", "")
    msg = msg.lower()

    for i in wordlist:
        if i.lower() in msg:
            startCount = msg.index(i.lower())
            # print(startCount)
            try:
                # print(msg[startCount+len(i):], msg[(startCount-1):])
                if msg[startCount+len(i)] in [" ", "\n", "*","/","-","."] and msg[startCount-1] in [" ", "\n", "*","/","-","."]:
                    # print(f"{i} Detected")
                    if i not in wlist:
                        wlist.append(i)
            except IndexError:
                    # print(f"{i} Detected")
                    if i not in wlist:
                        wlist.append(i.lower())

    percentage = (len(wlist)/len(msg.split()))*100
    severity = float(percentage)
    # print(wlist)

    if(len(wlist)>=1):
        return True,wlist,severity
    else:
        return False,[],0.0