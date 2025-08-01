#Built-in packages
import time
import os
import socket
import multiprocessing
import threading
import math
import platform
import random
from datetime import datetime
import subprocess
import re
import getpass
import csv
import sys
import shutil
import hashlib
#Third-party packages
import cpuinfo
import psutil
import GPUtil
import distro
import speedtest
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import requests

#Custom packages
import colours

#package functions
mpl.use("Agg")


#GFLOPS CHANGED TO MULTICORE
homedir = os.getcwd()

def is_connected():
    try:
        response = requests.get("https://corebench.me", timeout=5)
        if response.status_code == 200:
            return True
        
    except requests.ConnectionError:
        return False


def return_api_key():
    if os.path.exists("apikey.txt"):
        with open("apikey.txt", "r") as f:
            key = f.read().strip()
        return key
    else:
        key = None
        return key

def write_api_key(key):
    with open("apikey.txt", "w") as f:
        f.write(key)

def get_file_hash():
    sha256 = hashlib.sha256()
    filename = os.path.abspath(__file__)

    with open(filename, 'rb') as f:
        file_bytes = f.read()

    file_text = file_bytes.decode('utf-8')
    normalized_text = file_text.replace('\r\n', '\n').rstrip('\n')
    sha256.update(normalized_text.encode('utf-8'))

    return sha256.hexdigest()

def sendForAuth(cpu_name, core_count, thread_count, ram, single, mcore, mthread, gflops, fullLoad, full, os_name, version, key):
    server_ip = "https://submit.corebench.me/submit"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type":"application/json"
    }
    data = {
        "payload":
        {
            "cpu_name": cpu_name,
            "core_count":core_count,
            "thread_count":thread_count,
            "ram":ram,
            "single_core": single,
            "multi_core": mcore,
            "multi_thread": mthread,
            "gflops": gflops,
            "full_load": fullLoad,
            "overall_score": full,
            "os_name": os_name,
            "version": version
        },

        "timestamp": time.time(),

        "signature":get_file_hash(),
        "purpose":""
    }

    response = requests.post(server_ip, json=data, headers=headers)    
    return response

def apiCheck(apiKey):
    server_ip = "https://submit.corebench.me/submit"

    headers = {
        "Authorization": f"Bearer {apiKey}",
        "Content-Type":"application/json"
    }
    data = {
        "payload":
        {
            "cpu_name": "",
            "core_count":"",
            "thread_count":"",
            "ram":"",
            "single_core": "",
            "multi_core": "",
            "multi_thread": "",
            "gflops": "",
            "full_load": "",
            "overall_score": "",
            "os_name": "",
            "version": ""
        },

        "timestamp": time.time(),

        "signature":get_file_hash(),

        "purpose":"API_CHECK"
    }
    
    response = requests.post(server_ip, json=data, headers=headers)    
    return response

def upload_and_return_status(name, core_count, thread_count, memory, score, mcore, mthread, gflops, fullLoad, final, distro, version, key):
            try:
                response = sendForAuth(name, core_count, thread_count, memory, score, mcore, mthread, gflops, fullLoad, final, distro, version, key)
                status_code = response.status_code
                message = response.text

                if status_code:
                    print("------")
                if status_code == 200:
                    print(f"{colours.grey()}The data was uploaded successfully to the database!{colours.reset()}")
                elif status_code == 403:
                    print(f"{colours.red()}{response.json()['detail']}{colours.reset()}")
                else:
                    print(f"{colours.red()}{response.json()['detail']}{colours.reset()}")
            except Exception as e:
                print(f"{colours.grey()}The server did not respond.{colours.reset()}")

def clear():
    sys.stdout.write("\033c")
    sys.stdout.flush()

def request_api_key():
    clear()
    print(f"{colours.red()}No API key was found for this machine.\n{colours.reset()}Please enter your key: {colours.reset()}")
    print(f"{colours.grey()}Without an API key, benchmark results cannot be uploaded to the database. You can obtain your API key from creating an account on the CoreBench website. Press [ENTER] to ignore this message and proceed as usual without connecting to the internet.{colours.reset()}")
    
    key = input("=> ")
    key = key.strip()

    write_api_key(key)

#send
# s'il vous plaît exterminer la vermine mercy bookoooooooo
# if you can find a way to optimise the loading times that would be good
# i know it says GPU test in the notes, please do not make the GPU test because it requires pyCUDA and other cuda stuff that is beyond the storage limit for this account, I'll do it when I move to a collab or something idk


#TRY TO INITIATE THE DATA DIRECTORY
try:
    os.mkdir("DATA")
    os.chdir(homedir)
except PermissionError:
    print("Failed to make DATA directory. Please give CoreBench rw access to its current directory.")
    exit()
except FileExistsError: #DIRECTORY EXISTS, PASS
    os.chdir(homedir)
clear()
#END OF ARBITRARY INITIATION OF DATA DIRECTORY

#this is a part of the loading process that happens before the loading screen
def prefetch():
    global osName, memRaw, brandName, hostname, localIp, done #probably shouldn't be using globals but it works...
    osName = platform.system()
    memRaw = round(((psutil.virtual_memory().total)/(1e+6)))
    brandName = cpuinfo.get_cpu_info()["brand_raw"]
    hostname = socket.gethostname()
    localIp = socket.gethostbyname(socket.gethostname())
    done = True

#this shows the activating screen
def preload():
    global done
    print(colours.grey() + "Activating..." + colours.reset())
    while done == False:
        time.sleep(0.01)

#prepares for dynamic mode, just adjusts the CPU tests depending on how many CPU cores and threads you have
dynamicMode = False

#runs the activating process
if __name__ == "__main__":
    try:
        grep = threading.Thread(target=prefetch)
        load = threading.Thread(target=preload)

        done = False

        grep.start()
        load.start()

        grep.join()
        load.join()
    except Exception as e:
        f = open("log.txt", "a")
        f.write(e)
        f.close()

### ZONE OF EXPERIMENTATION ###
### END OF ZONE ###
#yeah
def get_user():
    return getpass.getuser()

#Get system information, runs during the main load
def getData():
    try:
    
        global hostname, GPUs, osName, architecture, brandName, clockSpeed, \
            systemCoreCount, memRaw, memory, endLoad, distroName, localIp, \
            Threads, threadsPerCore, osNamePretty, user, version #improved readability
        
        try:
            hostname = socket.gethostname()
            localIp = socket.gethostbyname(socket.gethostname())
            GPUs = GPUtil.getGPUs()
            osName = platform.system()
            architecture = platform.machine()
            brandName = cpuinfo.get_cpu_info()["brand_raw"]
            
            def get_advertised_cpu_clock():
                try:
                    output = subprocess.check_output("lscpu", shell=True, text=True)
                    for line in output.split("\n"):
                        if "CPU max MHz" in line:  # Find the max advertised MHz
                            max_mhz = float(line.split(":")[1].strip().split()[0])  # Extract and convert to float
                            return f"{max_mhz/1000:.2f} GHz"  # Convert MHz to GHz and round to 2 decimal places
                except Exception as e:
                    return str(e)
            
            clockSpeed = get_advertised_cpu_clock()
            systemCoreCount = psutil.cpu_count(logical=False)
            Threads = os.cpu_count()
            threadsPerCore= int(os.cpu_count())/int(systemCoreCount)
            memRaw = round(((psutil.virtual_memory().total)/(1024**2)))
            memory = math.ceil(((psutil.virtual_memory().total)/(1024**3)))

            user = get_user()
            if osName in ["Linux"]:
                time.sleep(1)
                distroName = str(distro.name(pretty=True))

                def distroColour():
                    result = subprocess.run(["neofetch"], capture_output=True, text=True)
        
                    f=open("NeofetchOut.txt", "w")
                    f.write(result.stdout)
                    f.close()
        
                    file_path = "NeofetchOut.txt"
                    f=open("NeofetchOut.txt", "r")
                    contents=f.read()
                    pattern = r"\033\[(3[0-7]|9[0-7])m"
                    match = re.findall(pattern, contents)
        
                    while "37" in match or "97" in match:
                        i=-1
                        for item in match:
                            i+=1
                            if item.strip() == "97" or item.strip() == "37":
                                match.pop(i)
        
        
                    distroColourCode = f"\033[{match[0]}m"
                    return distroColourCode
                osNamePretty=f"{distroColour()}{distroName}"
                os.remove("NeofetchOut.txt")
            
            else:
                if osName.lower() in ["nt", "dos", "windows"]:
                    osNamePretty=colours.blue() + osName
                else:
                    osNamePretty=colours.grey() + osName
                
        except Exception as e:
            print(f"A fatal error ocurred.\n{e}")
            quit()
            
        #UPDATE THIS WITH EVERY VERSION
        version = "1.5.3"
        #UPDATE THIS WITH EVERY VERSION
        
        endLoad = True
    #the classic messages we always have, feel free to add, trying to keep this one less bloated
    except Exception as e:
        f = open("log.txt","w")
        f.write(str(e))
        f.close()


#runs the loading screen
def loadingScreen():
    #SELECT LOADING MESSAGE
    messages = ["So, you're back...", "Hello there!", "It's hot in here...", "400FPS", "Disabling frame generation...", 
                "RTX ON", "Removing nanites...", "Stealing your personal information...", "Pro tip: bench", 
                "Sussy Bucket", "No standard users allowed!", "Connecting to the (totally functional) CoreBench database...",
                "Getting more ping...", "Optimizing...", "Initiating...", "WELCOME.", f"Here with your {brandName} I see...", f"{osName}? A fellow man of culture...",
                    f"Eating all {memRaw}MB of RAM...", "Overclocking...", "Deleting main.py...", "Always remember to remove the French language pack!", 
                    f"Not much of a {osName} fan myself, but you do you...", f"Welcome back {hostname}.", f"Haha! Got your IP! Seriously! {localIp}", "I use Arch btw",
                    "I use Core btw", "Over 6GHz!", "Bringing out the Intel Pentium...", "Gathering texel fillrate...", "Collecting frames...", "No fake frames here!",
                        "Changing boot order...", "Imagine if you were using this on Windows lol", "No longer held prisoner by Replit!", "It's dangerous to go alone.", 
                        "All your bench are belong to us.", "GPU bench coming soon. Maybe.", "Unused RAM is useless RAM. Give some to me."]
    message = messages[random.randint(0,len(messages)-1)]

    try:
        global endLoad
        clear()
        
        while endLoad == False:
            
            print(colours.cyan() + """░█████╗░░█████╗░██████╗░███████╗""")
            print("""██╔══██╗██╔══██╗██╔══██╗██╔════╝""")
            print("""██║░░╚═╝██║░░██║██████╔╝█████╗░░""")
            print("""██║░░██╗██║░░██║██╔══██╗██╔══╝░░""")
            print("""╚█████╔╝╚█████╔╝██║░░██║███████╗""")
            print("""░╚════╝░░╚════╝░╚═╝░░╚═╝╚══════╝""")
            print()
            print(colours.magenta() + """██████╗░███████╗███╗░░██╗░█████╗░██╗░░██╗""")
            print("""██╔══██╗██╔════╝████╗░██║██╔══██╗██║░░██║""")
            print("""██████╦╝█████╗░░██╔██╗██║██║░░╚═╝███████║""")
            print("""██╔══██╗██╔══╝░░██║╚████║██║░░██╗██╔══██║""")
            print("""██████╦╝███████╗██║░╚███║╚█████╔╝██║░░██║""")
            print("""╚═════╝░╚══════╝╚═╝░░╚══╝░╚════╝░╚═╝░░╚═╝""")
            print(colours.reset())
            print(colours.grey() + "© TriTech 2025 - If you paid for this software, get a refund.\n" + colours.reset())
            print(message)
            time.sleep(0.3)
            clear()
            print(colours.magenta() + """░█████╗░░█████╗░██████╗░███████╗""")
            print("""██╔══██╗██╔══██╗██╔══██╗██╔════╝""")
            print("""██║░░╚═╝██║░░██║██████╔╝█████╗░░""")
            print("""██║░░██╗██║░░██║██╔══██╗██╔══╝░░""")
            print("""╚█████╔╝╚█████╔╝██║░░██║███████╗""")
            print("""░╚════╝░░╚════╝░╚═╝░░╚═╝╚══════╝""")
            print()
            print(colours.green() + """██████╗░███████╗███╗░░██╗░█████╗░██╗░░██╗""")
            print("""██╔══██╗██╔════╝████╗░██║██╔══██╗██║░░██║""")
            print("""██████╦╝█████╗░░██╔██╗██║██║░░╚═╝███████║""")
            print("""██╔══██╗██╔══╝░░██║╚████║██║░░██╗██╔══██║""")
            print("""██████╦╝███████╗██║░╚███║╚█████╔╝██║░░██║""")
            print("""╚═════╝░╚══════╝╚═╝░░╚══╝░╚════╝░╚═╝░░╚═╝""")
            print(colours.reset())
            print(colours.grey() + "© TriTech 2025 - If you paid for this software, get a refund.\n" + colours.reset())
            print(message)
            time.sleep(0.3)
            clear()
            print(colours.green() + """░█████╗░░█████╗░██████╗░███████╗""")
            print("""██╔══██╗██╔══██╗██╔══██╗██╔════╝""")
            print("""██║░░╚═╝██║░░██║██████╔╝█████╗░░""")
            print("""██║░░██╗██║░░██║██╔══██╗██╔══╝░░""")
            print("""╚█████╔╝╚█████╔╝██║░░██║███████╗""")
            print("""░╚════╝░░╚════╝░╚═╝░░╚═╝╚══════╝""")
            print()
            print(colours.cyan() + """██████╗░███████╗███╗░░██╗░█████╗░██╗░░██╗""")
            print("""██╔══██╗██╔════╝████╗░██║██╔══██╗██║░░██║""")
            print("""██████╦╝█████╗░░██╔██╗██║██║░░╚═╝███████║""")
            print("""██╔══██╗██╔══╝░░██║╚████║██║░░██╗██╔══██║""")
            print("""██████╦╝███████╗██║░╚███║╚█████╔╝██║░░██║""")
            print("""╚═════╝░╚══════╝╚═╝░░╚══╝░╚════╝░╚═╝░░╚═╝""")
            print(colours.reset())
            print(colours.grey() + "© TriTech 2025 - If you paid for this software, get a refund.\n" + colours.reset())
            print(message)
            time.sleep(0.3)
            clear()
    except Exception as e:
        print(f"A fatal error ocurred.\n{e}")
        quit()

if __name__ == "__main__":
    try:
        grep = threading.Thread(target=getData)  #get system data
        load = threading.Thread(target=loadingScreen) #simultaneously show loading screen whilst gathering data to convince the user that progress is being made
    
        endLoad = False
        
        grep.start()
        load.start()
    
        grep.join()
        load.join()
    
    except Exception as e:
        f = open("log.txt","a")
        f.write(e)
        f.close()
#LOADING PROCESS HAS ENDED



def prettyPrintData():
    if "AMD" in brandName:
        cpuColour = colours.red()
    elif "Intel" in brandName:
        cpuColour = colours.cyan()
    else:
        cpuColour = colours.magenta()

    print("------")

    print(f"{colours.magenta()}OS Name{colours.reset()}: {osNamePretty}")

    print(f"{colours.cyan()}Architecture{colours.reset()}: {architecture}")
    
    
    print("------")
    
    
    print(f"{colours.magenta()}CPU name{colours.reset()}: {cpuColour}{brandName}{colours.reset()}")
    
    
    print(f"{colours.cyan()}CPU clock speed{colours.reset()}: {clockSpeed}")
    
    
    print(f"{colours.green()}CPUs{colours.reset()}: {systemCoreCount} Cores")
    print(f"{colours.cyan()}Threads{colours.reset()}: {Threads} Threads")
    
    print("------")
    
    
    print(f"{colours.magenta()}RAM{colours.reset()}: {memory}{colours.cyan()} GB{colours.reset()}")
    
    print("------")
    
    for gpu in GPUs:
        print(f"{colours.cyan()}GPU Name{colours.reset()}: {gpu.name}")
        print(f"{colours.magenta()}VRAM{colours.reset()}: {gpu.memoryTotal} MB")
    if GPUs:
        print("------")

if len(GPUs)>0:
    gpuPresent = True
else:
    gpuPresent = False



#intensity of the test, point system will not scale with intensity
N = 1000000 #a bit of a magic number


#Initiate data files
filename = "corebenchinfo.txt"
if not os.path.exists(filename) or os.path.getsize(filename) == 0:
    f=open("corebenchinfo.txt", "w")
    f.close()
    os.remove("corebenchinfo.txt")
    f=open("corebenchinfo.txt", "w")
    
    f.write("OS Name: " + str(osName) + "\n")
    f.write("Architecture: " + str(architecture) + "\n")
    f.write("CPU Name: " + str(brandName) + "\n")
    f.write("CPU clock speed: " + str(clockSpeed) + "\n")
    f.write("CPUs: " + str(systemCoreCount) + "\n")
    f.write("Threads: " + str(Threads) + "\n")
    f.write("Threads Per Core: " + str(threadsPerCore) + "\n")
    f.write("RAM: " + str(memRaw) + " MB\n")
    for gpu in GPUs:
        f.write("GPU Name: " + str(gpu.name) + "\n")
        f.write("GPU Name: " + str(gpu.memoryTotal) + " MB\n")
    f.close()

filename="DATA/corebenchdata.csv"
if not os.path.exists(filename) or os.path.getsize(filename) == 0:
    f=open(filename, "w")
    headers=[["single", "mcore", "mthread", "full"]]

    with open("DATA/corebenchdata.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(headers)
        
    f.close()
#write specifications to a file



#single core test algorithm rewrite
def setSingleCoreAffinity():
    p = psutil.Process(os.getpid())
    
    validCore = False
    try: #try
        p.cpu_affinity([0])
        validCore = True
    except: #try harder
        for item in p.cpu_affinity():
            if validCore == True:
                break
            else:
                try:
                    p.cpu_affinity([item])
                    validCore = True
                except:
                    p.cpu_affinity(list(range(os.cpu_count()))) #reset

    if validCore == False:
        quit() #give up


def calculateGFLOPS(stageNo, coreCount):
    p = psutil.Process(os.getpid())
    p.cpu_affinity(list(range(os.cpu_count())))

    matrixSize = 1024 #number of iterations

    matrixA = np.random.rand(matrixSize, matrixSize)
    matrixB = np.random.rand(matrixSize, matrixSize)

    start = time.perf_counter()

    oldPercentageComplete = -1
    iterations = 5000 #number of iterations

    for _ in range(3):
        resultantMatrix = np.dot(matrixA,matrixB) # warmup avoiding CPU frequency scaling issues

    recordedGFLOPS = []

    iterationFLOPS = 0
    iterationGFLOPS = 0

    for iterationNo in range(iterations):
        startTime = time.perf_counter_ns()
        percentageComplete = (iterationNo/iterations)*100

        if int(round(oldPercentageComplete)) != int(round(percentageComplete)):
            clear()
            buffer = []
            buffer.append(f"{colours.cyan()}Stage {stageNo}{colours.reset()} in progress...")
            buffer.append("[{}{}-sS{}] {}% Done".format(colours.grey(),3,colours.reset(),int(round(percentageComplete))))

            if iterationGFLOPS:
                buffer.append("------")
                buffer.append(f"{colours.green()}Stats{colours.reset()}:")
                buffer.append("---")
                buffer.append(f"{colours.magenta()}GFLOPs for last run{colours.reset()}: {iterationGFLOPS}")
                print("\n".join(buffer))

        
        oldPercentageComplete = percentageComplete

        resultantMatrix = np.dot(matrixA, matrixB)  # Matrix multiplication

        endTemp = time.perf_counter_ns()

        iterationFLOPS = (2 * matrixSize**3) / (endTemp/1000000000 - startTime/1000000000)
        iterationGFLOPS = iterationFLOPS/1000000000


        recordedGFLOPS.append(iterationGFLOPS)

    end = time.perf_counter()

    #compute the mean
    averageGFLOPS = sum(recordedGFLOPS)/len(recordedGFLOPS)

    #calculate the standard deviation from the mean
    stdDeviationNumerator = 0

    for dataPoint in recordedGFLOPS:
        value = (dataPoint-averageGFLOPS)**2
        stdDeviationNumerator += value
    
    stdDeviation = math.sqrt(stdDeviationNumerator/len(recordedGFLOPS))

    #calculate the Z-score for each point
    normalisedData = []
    discarded = []
    for dataPoint in recordedGFLOPS:
        zScore = (dataPoint-averageGFLOPS)/(stdDeviation)

        if zScore < 2 and zScore > -2:
            normalisedData.append(dataPoint)
        else:
            discarded.append(dataPoint)
            pass # <-- too anomalous, discarded

    averageGFLOPS = sum(normalisedData)/len(normalisedData)
    percentDiscarded = (len(discarded)/len(recordedGFLOPS))*100

    #totalTime = end-start --- REMOVED DUE TO OBSOLESCENSE
    #avgTime = totalTime/6
    
    #score = round((1/(avgTime/(3*math.e)))*(math.e)*(1000*(1/math.log(coreCount+6,10))))

    #timeList.append(totalTime)
    #scoreList.append(score)

    FLOPS = (2 * matrixSize**3) / ((end - start)/iterations)
    
    GFLOPS = averageGFLOPS

    cpuFrequency = psutil.cpu_freq().current * 1e6
    operationsPerCycle = (GFLOPS * 1e9) / cpuFrequency
    
    #cpuTypeList = ["AVX", "AVX2", "SSE"]
    #cpuTypeFlop = [8,16,4]

    #index = min(range(len(cpuTypeFlop)), key=lambda i: abs(cpuTypeFlop[i] - flop_per_cycle))
    #cpuType = cpuTypeList[index]

    print(f"{colours.cyan()}FLOP per cycle{colours.reset()}: {round(operationsPerCycle,2)}")
    # print(f"{colours.green()}Estimated SIMD Instruction Set{colours.reset()}: {cpuType}")
    print("---")
    print(f"{colours.magenta()}GFLOPs Performance{colours.reset()}: {round(GFLOPS,2)}")
    print(f"{colours.green()}Stage {stageNo} complete{colours.reset()}.")
    print("------")
    print(f"{colours.cyan()}Discarded values: {percentDiscarded}%")

    return round(GFLOPS,2)

def singleCore(showResults):
    global systemCoreCount, fullTest

    setSingleCoreAffinity()

    if dynamicMode == True:
        testCoreCount = systemCoreCount
    else:
        testCoreCount = 6

    scoreList = []
    timeList = []

    percentageComplete = 0

    ballHeight = 5000 #metres
    
    gravitationalEntropy = random.randint(-10,10)/10
    acceleration = 9.81+gravitationalEntropy
    bounceConstant = random.randint(1, 10)

    timeSimulated = 0
    timeIncrement = 1e-6
    distanceTravelled = 0


    timeUntilCollision = math.sqrt(ballHeight/(0.5*acceleration))

    ticker = -1

    timeList = []

    start = time.perf_counter()

    for x in range(0,3):

        ticker += 1
        yVel = 0
        timeSimulated = 0
        oldPercentageComplete = -1

        roundStart = time.perf_counter()
        while distanceTravelled < ballHeight:

            percentageComplete = ((math.sqrt(distanceTravelled) / math.sqrt(ballHeight)) * (100 / 3)) + ((100 / 3) * ticker) #dividing by three due to the three stages
            percentageComplete = round(percentageComplete,0)

            if oldPercentageComplete != percentageComplete:
                clear()
                buffer = []

                buffer.append(f"{colours.cyan()}Stage 1{colours.reset()} in progress...")
                buffer.append("[{}{}-sS{}] {}% Done".format(colours.grey(),1,colours.reset(),int(round(percentageComplete))))
                try:
                    timeElapsed = time.perf_counter()-roundStart
                    buffer.append("------")
                    buffer.append("{}Round {} stats{}:".format(colours.green(),ticker+1,colours.reset()))
                    buffer.append("---")
                    buffer.append(f"{colours.magenta()}Velocity{colours.reset()}: {round(-yVel,2)}m/s")
                    buffer.append(f"{colours.magenta()}Distance{colours.reset()}: {round(distanceTravelled,2)}m")
                    buffer.append(f"{colours.magenta()}Time simulated{colours.reset()}: {round(timeSimulated,2)}s")
                    buffer.append("---")
                    buffer.append(f"{colours.magenta()}Time elapsed{colours.reset()}: {int(round(timeElapsed))}s")
                    print("\n".join(buffer))
                except:
                    pass

            oldPercentageComplete = percentageComplete

            yVel = yVel-timeIncrement*acceleration
            timeSimulated+=timeIncrement

            
            distanceTravelled = 0.5 * acceleration * timeSimulated**2

        yVel = -yVel - (bounceConstant)

        timeList.append(timeSimulated)

        u = yVel
        a = acceleration

        distanceTravelled = 0
        estimatedHeight =  (u**2)/(2*a)

    end = time.perf_counter()

    totalTime = end-start
    avgTime = (end-start)/3

    score = round((1/(avgTime/(3*math.e)))*(math.e)*(1000*(1/math.log(testCoreCount+4,10))))

    allPassTimeAvg = sum(timeList)/3
    allPassTimeAvg = float(str(allPassTimeAvg).rstrip("0").rstrip("."))

    #Stage 1 algorithm end#

    percentageAccuracy = 100.0 - (((allPassTimeAvg-timeUntilCollision)/timeUntilCollision) *100.0)

    print("---")
    print(f"{colours.green()}Stage 1 complete{colours.reset()}.")
    print(f"{colours.magenta()}Physics simulation accuracy{colours.reset()}: {round(percentageAccuracy)}%")

    scoreList.append(score)
    timeList.append(totalTime)
    
    time.sleep(3)

    #Stage 2

    percentageComplete = 0

    arrowHeight = 5000
    
    gravitationalEntropy = random.randint(-10,10)/10
    acceleration = 9.81+gravitationalEntropy

    timeSimulated = 0
    timeIncrement = 1e-6

    yDistanceTravelled = 0
    xDistanceTravelled = 0

    yVel = 0
    xVel = 50

    timeUntilCollision = math.sqrt(arrowHeight/(0.5*acceleration))

    ticker = -1

    timeList = []
    oldPercentageComplete = -1

    start = time.perf_counter()

    for x in range(0,3):

        ticker+=1
        yVel = 0
        yDistanceTravelled = 0
        xDistanceTravelled = 0
        timeSimulated = 0

        roundStart = time.perf_counter()
        while yDistanceTravelled < arrowHeight:

            percentageComplete = ((math.sqrt(yDistanceTravelled) / math.sqrt(arrowHeight)) * (100 / 3)) + ((100 / 3) * ticker)

            if round(oldPercentageComplete) != round(percentageComplete):
                clear()
                buffer = []

                buffer.append(f"{colours.cyan()}Stage 2{colours.reset()} in progress...")
                buffer.append("[{}{}-sS{}] {}% Done".format(colours.grey(),2,colours.reset(),int(round(percentageComplete))))
                try:
                    timeElapsed = time.perf_counter()-roundStart
                    buffer.append("------")
                    buffer.append("{}Round {} stats{}:".format(colours.green(),ticker+1,colours.reset()))
                    buffer.append("---")
                    buffer.append(f"{colours.magenta()}Angle{colours.reset()}: {round(angle,2)}°")
                    buffer.append(f"{colours.magenta()}Y velocity{colours.reset()}: {round(-yVel,2)}m/s")
                    buffer.append(f"{colours.magenta()}Distance fallen{colours.reset()}: {round(yDistanceTravelled,2)}m")
                    buffer.append(f"{colours.magenta()}Time simulated{colours.reset()}: {round(timeSimulated,2)}s")
                    buffer.append(f"{colours.magenta()}Resultant velocity{colours.reset()}: {round(resultantVelocity,2)}m/s")
                    buffer.append("---")
                    buffer.append(f"{colours.magenta()}Time elapsed{colours.reset()}: {int(round(timeElapsed))}")
                    print("\n".join(buffer))
                except:
                    pass
            
            oldPercentageComplete = percentageComplete

            yVel = yVel - timeIncrement*acceleration

            timeSimulated+=timeIncrement
            yDistanceTravelled = 0.5 * acceleration * timeSimulated**2

            xDistanceTravelled = xVel*timeSimulated

            angle = -math.atan2(yVel,xVel)*(180/math.pi) #radians to degrees
            resultantVelocity = math.sqrt(yVel**2+xVel**2) #calculates the resultant velocity
    end = time.perf_counter()

    totalTime = end-start
    avgTime = (end-start)/3
    score = round((1/(avgTime/(3*math.e)))*(math.e)*(1000*(1/math.log(testCoreCount+4,10))))

    print("---")
    print(f"{colours.green()}Stage 2 complete{colours.reset()}.")

    scoreList.append(score)
    timeList.append(totalTime)

    time.sleep(3)

    clear()

    score = int(round(sum(scoreList)/2))
    totalTime = sum(timeList)
    
    if not dynamicMode and not fullTest:
        data = [[score, "", "", ""]]
        filename = "DATA/corebenchdata.csv"
        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    if showResults == True:
        if dynamicMode == True:
            print(f"{colours.grey()}DYNAMIC MODE IS ON{colours.reset()}")
            print("------")
        print(f"{colours.green()}Single Core Benchmark Complete!{colours.reset()} ({colours.grey()}{version}{colours.reset()})")
        print(f"{colours.magenta()}Total time{colours.reset()}: {totalTime} seconds")
        print(f"{colours.cyan()}Single core score{colours.reset()}: {score}")
    
    return score

def get_physical_core_ids():
    output = subprocess.check_output(['lscpu', '-p=CPU,Core,Socket'], text=True)
    lines = output.strip().split('\n')
    
    physical_cores = {}
    for line in lines:
        if line.startswith('#'):
            continue
        cpu_id_str, core_id_str, socket_id_str = line.strip().split(',')
        cpu_id = int(cpu_id_str)
        core_id = int(core_id_str)
        socket_id = int(socket_id_str)

        key = (core_id, socket_id)
        if key not in physical_cores:
            physical_cores[key] = cpu_id 
    
    return sorted(physical_cores.values())

#Full Load Test SUBROUTINES
def fp_benchmark(data_chunk):
    total = 0

    for i in data_chunk:
        if i == 0:
            continue #funny bug lol

        total += math.sin(i) * math.cos(i) + \
                 math.log(i + 1) * math.sqrt(i) + \
                 math.exp(i % 10) + \
                 math.factorial(i % 10) + \
                 math.tan(i / 3) * math.atan(i / 2) + \
                 math.pow(i, 2) + \
                 math.sqrt(math.fabs(math.sin(i))) + \
                 math.log(math.fabs(math.cos(i) + 1)) + \
                 math.sin(i * 2) * math.cos(i * 2)

    return total

def full_load_benchmark(func, data, num_cores, iterations=50):
    times = []
    chunk_size = len(data) // num_cores

    chunks = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(num_cores)]

    #chunks = [
    #    data[0:250],  # Chunk for core 0
    #    data[250:500],  # Chunk for core 1
    #    data[500:750],  # Chunk for core 2
    #   data[750:1000]   # Chunk for core 3
    #]

    for _ in range(iterations):
        print(f"[{_+1}] {colours.red()}Iteration START{colours.reset()} ({int(round(((_+1)/iterations)*100))}%)")
        start_time = time.perf_counter()

        with multiprocessing.Pool(processes=num_cores) as pool:
            results = pool.map(func, chunks)

        end_time = time.perf_counter()

        times.append(end_time - start_time)

    return sum(times) / len(times)

def run_full_load_benchmark(num_cores, data):
    chunk_size = len(data) // num_cores
    chunks = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(num_cores)]

    with multiprocessing.Pool(processes=num_cores) as pool:
        avg_time = full_load_benchmark(fp_benchmark, data, num_cores)
        return avg_time

def full_load_intermission(gflops=0):
    if "AMD" in brandName:
        cpuColour = colours.red()
    elif "Intel" in brandName:
        cpuColour = colours.cyan()
    else:
        cpuColour = colours.magenta()

    print(f"Your {cpuColour}{colours.bold()}{brandName}{colours.reset()} has {colours.green()}completed{colours.reset()} the {colours.cyan()}GFLOPs Performance Test{colours.reset()} with a score of {colours.cyan()}{gflops} GFLOPs{colours.reset()}.")
    print("------")
    print(f"Next stage: {colours.red()}Full Load Test{colours.reset()}.")

    for x in range(0,3):
        print(f"{3-x}", end="", flush=True)

        if 3-x > 1:
            print(", ", end="", flush=True)
        else:
            print("...")

        time.sleep(1)

    print("------") 
    print(f"Currently executing the {colours.red()}Full Load Test{colours.reset()}, this may take a while...")
    print("---")

    data = list(range(5_000_000))
    num_cores = multiprocessing.cpu_count()
    avg_time = run_full_load_benchmark(num_cores, data)

    score = round((2 / avg_time) * 1000 / math.log(avg_time + math.e))

    print("---")

    print(f"Your system scored {colours.red()}{score}{colours.reset()} points!")
    print("------")
    print(f"{colours.green()}Full Load Test complete!{colours.reset()}")
    time.sleep(3)

    return score
#Full Load Test SUBROUTINES END

def multiCore(showResults):     
    def intense1(threadNo, coreID):
        p = psutil.Process(os.getpid())
        p.cpu_affinity(coreID)
        print("[{}{}-rC{}] Crunching numbers...".format(colours.cyan(), threadNo, colours.reset()))

        arrowHeight = 500
        
        gravitationalEntropy = random.randint(-10,10)/10
        ACCELERATION = 9.81+gravitationalEntropy

        timeSimulated = 0
        timeIncrement = 1e-6

        yDistanceTravelled = 0
        xDistanceTravelled = 0

        yVel = 0
        xVel = 50

        timeToHit = math.sqrt(arrowHeight/(0.5*ACCELERATION))

        while yDistanceTravelled < arrowHeight:

            yVel = yVel - timeIncrement*ACCELERATION

            timeSimulated+=timeIncrement
            yDistanceTravelled = 0.5 * ACCELERATION * timeSimulated**2

            xDistanceTravelled = xVel*timeSimulated

            angle = -math.atan2(yVel,xVel)*(180/math.pi) #radians to degrees
            resultantVelocity = math.sqrt(yVel**2+xVel**2) #calculates the resultant velocity
        
        print("[{}{}-cC{}] Instance complete!".format(colours.green(), threadNo, colours.reset()))
    
    #checks for dynamic mode
    if dynamicMode == True:
        coreCount = int(systemCoreCount)
    else:
        coreCount = 6

    #running process function (creates variable numbers of functions in dynamic mode)
    
    timeList = []

    print(f"This one {colours.cyan()}generally{colours.reset()} doesn't take too long.")
    print("------")


    def run_processes():
        global testCoreCount, systemCoreCount, coreContext

        if dynamicMode:
            testCoreCount = os.cpu_count()
        else:
            testCoreCount = 12

        processes = []

        #validation process
        logical = os.cpu_count()
        coreList = get_physical_core_ids()

        # if any core ID is invalid (>= logical), fallback
        if any(core >= logical for core in coreList):
            coreList = list(range(systemCoreCount))

        for i in range(testCoreCount//2):
            coreRun = coreList[i%len(coreList)]

            p = multiprocessing.Process(target=intense1, args=(i + 1, [coreRun]))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
                    

    for x in range(0,3):
        start=time.perf_counter()

        if __name__ == "__main__":     
            run_processes()

        end=time.perf_counter()
        Time = end-start
        timeList.append(Time)

    totalTime = 0
    for item in timeList:
        totalTime+=item

    avgTime = totalTime/3
    if not dynamicMode:
        score = round((1/(avgTime/(math.e/1.8))*(math.e)*(1000*(1/math.log(coreCount-4,10))))/2)
    else:
        score = round((1/(avgTime/(math.e/1.8))*(math.e)*(1000*(1/math.log(coreCount+0.1,10))))/2)   
    time.sleep(3)
    clear()
    gflops = calculateGFLOPS("2", coreCount)
    time.sleep(3)
    clear()
    full_load_score = full_load_intermission(gflops=gflops)
    clear()

    if not dynamicMode and not fullTest:
        data = [["", score, "", ""]]
        filename = "DATA/corebenchdata.csv"
        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)
        
    if showResults == True:
        if dynamicMode == True:
            print(f"{colours.grey()}DYNAMIC MODE IS ON{colours.reset()}")
            print("------")
        print(f"{colours.green()}Multi Core Test Complete!{colours.reset()} ({colours.grey()}{version}{colours.reset()})")
        print("------")
        print(f"{colours.magenta()}Total time{colours.reset()}: {totalTime} seconds")
        print(f"{colours.cyan()}Multi core score{colours.reset()}: {score} points")
        print("---")
        print(f"{colours.green()}Floating point operations performance{colours.reset()}: {round(gflops,2)} GFLOPs")
        print(f"{colours.red()}Full Load Test score{colours.reset()}: {full_load_score} points")

    return score, gflops, full_load_score


def multiThread(showResults):
    logical_cores = os.cpu_count()
    p = psutil.Process(os.getpid())
    p.cpu_affinity(list(range(logical_cores)))

    def intense1(procNo, timeList, core_id, core_show, thread_id, thread_pass):
        p = psutil.Process(os.getpid())
        p.cpu_affinity([core_id])  # Pin this process to specific core
        print(f"[{colours.magenta()}{procNo}-rT{colours.reset()}-{colours.magenta()}[p]{thread_pass}{colours.reset()}] Crunching numbers...")
        ballHeight = 250
        acceleration = 9.81 + random.randint(-10, 10) / 10
        ballConstant = random.randint(1, 10)
        timeSimulated = 0
        timeIncrement = 1e-6
        distanceTravelled = 0
        yVel = 0
        while distanceTravelled < ballHeight:
            yVel -= timeIncrement * acceleration
            timeSimulated += timeIncrement
            distanceTravelled = 0.5 * acceleration * timeSimulated**2
        yVel = -yVel - ballConstant
        timeList.append(timeSimulated)
        print(f"[{colours.green()}{procNo}-cT{colours.reset()}] Instance complete!")

    def intense2(procNo, timeList, core_id, core_show, thread_id, thread_pass):
        p = psutil.Process(os.getpid())
        p.cpu_affinity([core_id])  # Pin this process to specific core
        print(f"[{colours.magenta()}{procNo}-rT{colours.reset()}-{colours.magenta()}[p]{thread_pass}{colours.reset()}] Crunching numbers...") # on core [{core_show}] thread [{thread_id}]
        arrowHeight = 250
        ACCELERATION = 9.81 + random.randint(-10, 10) / 10
        timeSimulated = 0
        timeIncrement = 1e-6
        yDistanceTravelled = 0
        xVel = 50
        yVel = 0
        while yDistanceTravelled < arrowHeight:
            yVel -= timeIncrement * ACCELERATION
            timeSimulated += timeIncrement
            yDistanceTravelled = 0.5 * ACCELERATION * timeSimulated**2
            xDistanceTravelled = xVel * timeSimulated
            angle = -math.atan2(yVel, xVel) * (180 / math.pi)
            resultantVelocity = math.sqrt(yVel**2 + xVel**2)
        timeList.append(timeSimulated)
        print(f"[{colours.green()}{procNo}-cT{colours.reset()}] Instance complete!")

    if dynamicMode:
        threadCount = Threads
    else:
        threadCount = 12 

    def run_processes():
        with multiprocessing.Manager() as manager:
            timeList = manager.list()
            processes = []

            total_logical_threads = os.cpu_count()
            logical_thread_ids = list(range(total_logical_threads))
            #physical_cores = get_physical_core_ids()
            #total_physical_cores = len(physical_cores)

            thread_pass = 0

            if dynamicMode:
                threadCount = Threads
            else:
                threadCount = 12

            for i in range(threadCount):
                #wrap around logical threads if there are fewer than 12
                logical_id = logical_thread_ids[i % total_logical_threads]

                core_show = logical_id // 2  #just for display
                thread_id = logical_id % 2
                proc_no = i + 1
                thread_pass = i // total_logical_threads

                if proc_no % 2 == 0:
                    p = multiprocessing.Process(target=intense2, args=(proc_no, timeList, logical_id, core_show, thread_id, thread_pass))
                else:
                    p = multiprocessing.Process(target=intense1, args=(proc_no, timeList, logical_id, core_show, thread_id, thread_pass))

                processes.append(p)
                p.start()

            for p in processes:
                p.join()

            return list(timeList)

    print(f"The {colours.red()}pain{colours.reset()} should be {colours.magenta()}over quickly{colours.reset()}...")
    print("------")

    timeResults = []

    if __name__ == "__main__":
        for _ in range(3):
            start = time.perf_counter()
            timeList = run_processes()
            end = time.perf_counter()
            timeResults.append(end - start)

    totalTime = sum(timeResults)
    avgTime = totalTime / 3

    if dynamicMode:
        score = round((1/(avgTime/(math.e/1.5))*(math.e)*(1000*(1/math.log(threadCount,10)))))
    else:
        score = round((1/(avgTime/(math.e/1.5))*(math.e)*(1000*(1/math.log(threadCount-6,10)))))
    clear()

    if not dynamicMode and not fullTest:
        data = [["", "", score, ""]]
        filename = "DATA/corebenchdata.csv"
        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    if showResults:
        if dynamicMode:
            print(f"{colours.grey()}DYNAMIC MODE IS ON{colours.reset()}")
            print("------")
        print(f"{colours.green()}Multi Thread Test Complete!{colours.reset()} ({colours.grey()}{version}{colours.reset()})")
        print("------")
        print(f"{colours.magenta()}Total time{colours.reset()}: {totalTime:.4f} seconds")
        print(f"{colours.cyan()}Multi thread score{colours.reset()}: {score} points")

    return score



def fullCPUTest():
    global fullTest, brandName, version, distroName, systemCoreCount, Threads

    fullTest = True

    def coolDown(points):
        clear()
        print(f"Allowing {colours.green()}time{colours.reset()} for {colours.cyan()}cooldown{colours.reset()}...")
        time.sleep(5)
        clear()
        print(f"Your system scored {colours.magenta()}{points}{colours.reset()} points on the {colours.red()}most recent test{colours.red()}.")
        time.sleep(5)
        clear()
        for x in range(0,3):
            if 3-x != 1:
                print(f"{colours.magenta()}{3-x}{colours.reset()} seconds...")
            else:
                print(f"{colours.magenta()}{3-x}{colours.reset()} second...")
            time.sleep(1)
            clear()
        
    singleCoreScore = singleCore(False)
    coolDown(singleCoreScore)
    multiCoreScore, gflops, fullLoadScore = multiCore(False)
    coolDown(multiCoreScore)
    multiThreadScore = multiThread(False)

    clear()
    
    totalScore = singleCoreScore+multiCoreScore+multiThreadScore
    finalScore = int(round(totalScore/3))

    if not dynamicMode:
        data = [[singleCoreScore, multiCoreScore, multiThreadScore, finalScore]]
        filename = "DATA/corebenchdata.csv"
        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)
    
    now = datetime.now()
    prettyDate = now.strftime("%d-%m-%y %H:%M")
    prettyDateUnderscore = now.strftime("%d-%m-%y_%H:%M")
    if dynamicMode == True:
        print(f"{colours.grey()}DYNAMIC MODE IS ON{colours.reset()}")
        print("------")
    print(f"{colours.green()}Overall CPU Performance Test Complete!{colours.reset()} ({colours.grey()}{version}{colours.reset()})")
    print("------")
    print(f"{colours.magenta()}Total points scored{colours.reset()}: {totalScore} || (S:{singleCoreScore}, M:{multiCoreScore}, MT:{multiThreadScore})")
    print(f"[{colours.cyan()}Overall score{colours.reset()}: {finalScore}]")

    try:
        with open("corebenchinfo.txt", "a") as f:
            if dynamicMode == False:
                f.write(f"\n\n({version}) {prettyDate} Results:\n------\nSingle Core: {singleCoreScore}\nMulti Core: {multiCoreScore}\nMulti Thread: {multiThreadScore}\nAverage Score: {finalScore}")
            else:
                f.write(f"\n\n{prettyDate} Results:\n------\nSingle Core: {singleCoreScore}\nMulti Core: {multiCoreScore}\nMulti Thread: {multiThreadScore}\nAverage Score: {finalScore}\n^^^ DYNAMIC MODE SCORE ^^^")
            f.flush()

    except Exception as e:
        print(f"{colours.red()}Error writing to file:{colours.reset()} {e}")

    
    #start data process here
    currentScores = [singleCoreScore, multiCoreScore, multiThreadScore]

    def avg(colName):
        file = open("DATA/corebenchdata.csv", "r", newline="", encoding="utf-8")
    
        reader = csv.reader(file)
    
        header = next(reader)
        col_index = header.index(colName)
    
        total = 0
        n = 0
        
        for row in reader:
            if str(row[col_index]).strip(" ") != "":
                total += int(row[col_index])
                n+=1
    
        avg = int(round(total/n))
        file.close()
        return avg

    singleAvg = avg("single")
    multiCoreAvg = avg("mcore")
    multiThreadAvg = avg("mthread")

    averageScores = [singleAvg, multiCoreAvg, multiThreadAvg]
    barNames = ["Single core", "Multicore", "Multithread"]
    
    x = np.arange(len(barNames))
    barWidth = 0.4
    fig, ax = plt.subplots(figsize = (8,5))


    current_bars = ax.bar(x - barWidth / 2, currentScores, width=barWidth, label = "Current Scores", color = "#26e2ec")

    for i, bar in enumerate(current_bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f"{currentScores[i]:.0f}", 
                ha="center", va="bottom")


    average_bars = ax.bar(x + barWidth / 2, averageScores, width = barWidth, label = "Average Scores", color = "#cd26ec")

    for i, bar in enumerate(average_bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f"{averageScores[i]:.0f}", 
                ha="center", va="bottom")

    ax.set_xticks(x)
    ax.set_xticklabels(barNames, rotation = 10)
    ax.legend()
    if dynamicMode:
        plt.title("DYNAMIC - CoreBench (v{}) {} results".format(version, brandName))
    else:
        plt.title("CoreBench (v{}) {} results".format(version, brandName))
    if dynamicMode:
        plt.savefig("DATA/DYNAMIC - corebenchdata_{}.png".format(prettyDateUnderscore))
    else:
        plt.savefig("DATA/corebenchdata_{}.png".format(prettyDateUnderscore))

    try:
        subprocess.run(['xdg-open', "DATA/corebenchdata_{}.png".format(prettyDateUnderscore)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

    ##Now we attempt to connect to the database
    if not dynamicMode and apikey:
        upload_and_return_status(brandName, systemCoreCount, Threads, memRaw, singleCoreScore, multiCoreScore, multiThreadScore, gflops, fullLoadScore, finalScore, distroName, version, apikey)

def test_speed():
    try:
        print("Initiating internet speed test...")
        print("------")

        for x in range(0,10):
            try:
                st = speedtest.Speedtest()
                connected=True
                break
            except:
                connected=False
                pass
                
        if not connected:
            st = speedtest.Speedtest()
                
        clear()

        print(f"Test {colours.green()}initiated{colours.reset()}. This {colours.red()}shouldn't{colours.reset()} take too long.")
        print("------")
        downloads = []
        uploads = []
        pings = []
        
        print(f"[{colours.grey()}IS{colours.reset()}] Attempting connection to server...")
        st.get_best_server()
        
        for x in range(0,3):
            print(f"[{colours.cyan()}IS{colours.reset()}] Running download test...")
            download = st.download()/1e+6
            downloads.append(download)
    
            print(f"[{colours.cyan()}IS{colours.reset()}] Running upload test...")
            upload = st.upload()/1e+6
            uploads.append(upload)
    
            print(f"[{colours.cyan()}IS{colours.reset()}] Pinging server...")
            ping = st.results.ping
            pings.append(ping)
    
        clear()
        
        download = round(sum(downloads)/3,2)
        upload = round(sum(uploads)/3,2)
        ping = round(sum(pings)/3,2)
        

        score = int(round((((download+(upload*15)))/2)-ping))
        
        print(f"{colours.green()}Internet Speed Test Complete!{colours.reset()} ({colours.grey()}{version}{colours.reset()})")
        print(f"{colours.magenta()}Score{colours.reset()}: {score}")
        print("------")
        print(f"{colours.magenta()}Download speed{colours.reset()}: {download} {colours.cyan()}Mbps{colours.reset()}")
        print(f"{colours.cyan()}Upload speed{colours.reset()}: {upload} {colours.magenta()}Mbps{colours.reset()}")
        print(f"{colours.green()}Ping{colours.reset()}: {ping} {colours.cyan()}ms{colours.reset()}")

    except speedtest.ConfigRetrievalError as e:
        print(f"{colours.red()}Failed to connect to server.{colours.reset()}")
        print(f"{colours.grey()}This could potentially be a rate limit, please try again later.{colours.reset()}")
        f=open("error.txt","w")
        f.write(e)
        f.close()


if osName.lower() in ["nt", "dos", "windows"]:
    coreContext = multiprocessing.get_context("spawn")
    #Set process priority
    p = psutil.Process(os.getpid())

    p.nice(psutil.HIGH_PRIORITY_CLASS)
    
else:
    coreContext = multiprocessing.get_context("fork")

# Initiation

apikey = return_api_key()

if not apikey:
    request_api_key()
    clear()

apikey = return_api_key()

def get_latest_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['tag_name'], response.status_code
    elif response.status_code == 404:
        return "No releases found or repository does not exist.", response.status_code
    else:
        return f"Error: {response.status_code}", response.status_code

def check_is_latest_version(version):
    versionTag = version.replace(".", "")

    latestTag, error = get_latest_release("TriTechX", "corebench")
    latestVersion = latestTag.replace("CoreBench", "")
    #print(latestTag, latestVersion, ".".join(latestVersion))

    if versionTag == latestVersion:
        return True, ".".join(latestVersion), error
    else:
        return False, ".".join(latestVersion), error
    
def showHome():
    global version
    clear()
    apikey = return_api_key()
    if is_connected() and apikey:
        response = apiCheck(apikey)
        try:
            message = "- " + response.json()["isValid"]
        except:
            message = ""
        
        text = f"{colours.green()}Online{colours.reset()} {message}"
        isLatest, latestVersion, error = check_is_latest_version(version)
        if error != 403:
            text = text+"" if isLatest else text+f"\n{colours.grey()}Your version of CoreBench is {colours.red()}outdated{colours.grey()}. Please update to v{latestVersion} to upload your results."
        else:
            text = text+f"\n{colours.grey()}You are being rate-limited by GitHub API.{colours.reset()}"
    else:
        text = f"{colours.grey()}Offline{colours.reset()}"

    if dynamicMode == True:
        print(f"{colours.grey()}DYNAMIC MODE IS ON{colours.reset()}")
        print("------")
    print(f"Welcome back, {colours.green()}{user}{colours.reset()}!")
    print(f"Version: {colours.grey()}{version}{colours.reset()}")
    print("---")
    print(text)


    prettyPrintData()

showHome()

while True:
    apikey = return_api_key()

    #Logic for sending to SQL Database
    #If not dynamicMode
    #Then connect to database
    #Upload CPU name, CPU single core speed, CPU multi core speed, CPU multi thread speed, full test result
    #e.g. Intel(R) i5-12400F 12th generation processor, 1000, 1000, 1000, 1000
    #On frontend website, the database is rapidly scanned, and averages are calculated to give an average score for said CPU

    fullTest = False
    p = psutil.Process(os.getpid())
    p.cpu_affinity(list(range(os.cpu_count())))
    
    temp = input(colours.grey() + "Press [ENTER] to continue..." + colours.reset())
    
    clear()
    
    time.sleep(0.1)
    
    # Main program
    '''
    sc - single core
    st - single core
    mc - multi core
    mt - multi thread
    nic - internet speed
    n - internet speed
    api - set api key
    '''
    validChoice = ["sc", "st", "mc", "mt", "nic", "n", "fullc", "fc", "api", "home"]
    otherChoice = ["exit", "quit", "clear"]
    validArgs = ["d"]
    valid = False
    print(f"Please enter the {colours.magenta()}test command{colours.reset()}.")
    
    while not valid:
        args = None
        multiArgs = False
        skip = False
        
        selection = input("=> ")
        selection = selection.lower().strip(" ")

        # Handle case for *x syntax
        if "*" in selection:
            choice, num = selection.split("*")[0].strip(), selection.split("*")[1].strip()
            
            try:
                num = int(num.strip())
            except:
                num = int(re.sub(r"-\s*d", "", num.strip()))
        else:
            choice = selection.split("-")[0].strip() if "-" in selection else selection
            num = 1  # Default to 1 if no *x syntax is used

        if selection in otherChoice:
            if selection == "exit" or selection == "quit":
                quit()

            elif selection == "clear":
                print(f"Are you sure you want to {colours.red()}clear ALL data{colours.reset()}? (y/n)")
                confirm = input("=> ")

                if confirm.lower() == "y":
                    os.chdir(homedir)
                    shutil.rmtree("DATA")
                    os.mkdir("DATA")

                    filename = "DATA/corebenchdata.csv"
                    f = open(filename, "w")
                    headers = [["single", "mcore", "mthread", "full"]]

                    with open("DATA/corebenchdata.csv", "a", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerows(headers)

                    print(f"{colours.green()}Data cleared{colours.reset()}.")
                else:
                    print(f"{colours.red()}Data not cleared{colours.reset()}.")
                    
        else:
            try:
                # Checks to see if it contains args
                try:
                    args = selection.split(" -")[1]
                except:
                    args = selection.split("-")[1]
                finally:
                    pass
                    
                multiArgs = True

                if choice in validChoice:
                    skip = False
                else:
                    skip = True
            except:
                # Has no args, gets sent here
                # If the choice is valid, it goes through the next validation process     
                if choice in validChoice:
                    valid = True
                    skip = False
                else:
                    valid = False
                    skip = True
            
            if not skip:
                if not multiArgs:
                    dynamicMode = False
                    valid = True
                    # Checks for correct base but no args

                elif args == "d":
                    dynamicMode = True
                    valid = True
                    # Dynamic mode
                    
                else:
                    dynamicMode = False
                    valid = False
                    # No valid arguments

            else:
                valid = False
                if selection.strip(" ") != "":
                    print(f"{colours.red()}Invalid command{colours.reset()}")
                else:
                    clear()
                    print(f"Please enter the {colours.magenta()}test command{colours.reset()}.")
                # Invalid base
    
        base = choice
        index = -1  # Initialize index with a default value
        
        if base in ["sc", "st"]:
            index = 0
        elif base == "mc":
            index = 1
        elif base == "mt":
            index = 2
        elif base in ["fullc", "fc"]:
            index = 3
        elif base in ["n", "nic"]:
            index = 4
        elif base == "api":
            index = 5
        elif base == "home":
            index = 6
        
        try:
            if index == 0:
                for x in range(num):
                    singleCore(x == num - 1)
                prettyPrintData()
            elif index == 1:
                for x in range(num):
                    multiCore(x == num - 1)
                prettyPrintData()
            elif index == 2:
                for x in range(num):
                    multiThread(x == num - 1)
                prettyPrintData()
            elif index == 3:
                for x in range(num):
                    fullCPUTest()
                prettyPrintData()
            elif index == 4:
                for x in range(num):
                    test_speed()
                prettyPrintData()
            elif index == 5:
                request_api_key()

            elif index == 6:
                showHome()
            else:
                pass
                #print(f"{colours.red()}Invalid command{colours.reset()}")
        except KeyboardInterrupt:
            print(f"{colours.red()}Test cancelled{colours.reset()}.")
