import json
import os
import shutil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# 自动标注的条件是假设文字大小一致，根据字符长度进行判断，除了公司名称采用直接的数字作为标签，其他标签采用自定义并在该表中体现
# 5表示非公司名称的字符个数对应的实际标签
OvalTable = {15: "c15",13: "v13", 6: "t6", 5: "t5"}
CircleTable = {13: "v13", 5: "t5", 6: "t6"}

# 找到所有涉及到的关键字
def findFile(rootpath="./tools/Oval",type="Circle"):
    # 印章信息
    filepath = Path(rootpath).joinpath("SealInfo.csv")
    # 印章样例生成
    oldpath = Path(rootpath).joinpath("image")
    newpath = Path(rootpath).joinpath("sample")
    if not newpath.exists():
        newpath.mkdir(exist_ok=False)

    # 存放每个位置的关键字长度以及对应的文件名称
    resDict ={}
    res = filepath.read_text(encoding='utf-8')
    for i in res.split("\n"):
        line = i.split(",")
        for index,data in enumerate(line):
            # 创建位置的字典
            if data =="":
                continue
            if index == 1 or index==2:
                index = 1
            if index not in resDict.keys():
                resDict[index] = {}

            sDict = resDict[index]

            # 不存在的放入
            if len(data) not in sDict.keys():
                sDict[len(data)] = (data,line[0]+".png")
    classes = sum([len(resDict[i]) for i in resDict.keys()])
    classinfo = [resDict[i].keys() for i in resDict.keys()]

    # 真正需要标注的数据列表
    lists = []
    mainlist = [] # 需要标注主文字的列表
    otherlist = [] # 需要标注其他文字的列表
    for i in resDict.keys(): # 位置字典
        sDict = resDict[i]
        for j in sDict.keys(): # 字长字典
            lists.append(sDict[j][1])
            if i==0:
                mainlist.append(sDict[j][1])
            else:
                otherlist.append(sDict[j][1])
    lists = list(set(lists))

    print(f"Total {classes} classes, include {classinfo}")
    print(f"Total {len(lists)} images, {len(set(mainlist))} main, {len(set(otherlist))} vice, detail:\n mainList:{set(mainlist)}\n\n viceList:{set(otherlist)}")

    # 将其放入需要标注的文件夹
    for l in lists:
        l = l.replace('.png',f"_{type}.png")
        shutil.copy(oldpath.joinpath(l),newpath.joinpath(l))

def forceMergeFlatDir(srcDir, dstDir):
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)
    for item in os.listdir(srcDir):
        srcFile = os.path.join(srcDir, item)
        dstFile = os.path.join(dstDir, item)
        forceCopyFile(srcFile, dstFile)

def forceCopyFile (sfile, dfile):
    if os.path.isfile(sfile):
        shutil.copy2(sfile, dfile)
def isAFlatDir(sDir):
    for item in os.listdir(sDir):
        sItem = os.path.join(sDir, item)
        if os.path.isdir(sItem):
            return False
    return True
def copyTree(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isfile(s):
            if not os.path.exists(dst):
                os.makedirs(dst)
            forceCopyFile(s,d)
        if os.path.isdir(s):
            isRecursive = not isAFlatDir(s)
            if isRecursive:
                copyTree(s, d)
            else:
                forceMergeFlatDir(s, d)

# 读取所有标注的json文件，并进行汇总，作为基础数据
def readJson(root,type='Circle'):
    sampleroot = os.path.join(root, "sample")
    labelPath = Path(root).joinpath(f'baseLabel_{type}.json')
    resJson = {}
    cnt = 0
    for file in os.listdir(sampleroot):
        file = os.path.join(sampleroot,file)
        if os.path.splitext(file)[-1]!=".json":
            continue
        cnt += 1
        res = json.load(open(file,'r',encoding='utf-8'))
        res = res['shapes']
        for r in res:
            if r['label'] not in resJson.keys():
                resJson[r['label']] = r["points"]
    if cnt ==0:
        assert "没有标注文件"
    print("总数据：",len(resJson.keys()),"\n字典如下:\n",resJson.keys())
    json.dump(resJson,open(labelPath,'w'))
    return resJson

def generalData(root=None,jsonData=None, type='Circle'):
    typeDict = eval(type+'Table')
    lines = Path(root).joinpath("SealInfo.csv").read_text(encoding='utf-8').split("\n")
    resPath = Path(root).joinpath(f"label_{type}.txt")
    index = 0
    with open(resPath, 'w') as f:
        for line in lines:
            labelRes = []
            if line =="":
                continue
            texts= line.split(',')
            for index,text in enumerate(texts):
                if text == "" or text=="★":
                    continue
                if index == 0:
                    point = jsonData[str(len(text))]
                    point = np.around(np.array(point), decimals=1).tolist()
                    point = clockwise(point)
#                     if point!=None:
#                         index += 1
#                         plottest(point,index)
                    labelRes.append({"transcription":text,"points":point})
                else:
                    point = jsonData[typeDict[len(text)]]
                    point = np.around(np.array(point), decimals=1).tolist()
                    point = clockwise(point)
#                     if point!=None:
#                         index += 1
#                         plottest(point,index)

                    labelRes.append({"transcription": text, "points": point})
            f.write(f"image/{texts[0]}_{type}.png\t{labelRes}\n")

def mergefiles(root,types):
    res = ''
    resultDir = os.path.join(root, "label")
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)
    resultFile = os.path.join(root, "label.txt")
    if os.path.exists(resultFile):
        os.remove(resultFile)

    for type in types:
        typepath = os.path.join(root, type)
        if not os.path.exists(typepath):
            continue
        folder = os.path.join(typepath,'image')
        dst_folder = os.path.join(root, 'image')
        copyTree(folder, dst_folder)  # 复制文件夹并覆盖
        label = os.path.join(typepath,f"label_{type}.txt")
        res += open(label,'r').read()
    #  生成单个标签文件
    with open(resultFile, "w") as f:
        f.write(res)
    # 一个文件对应一个标签文件
    resLists = res.split("\n")
    for resList in resLists:
        if resList=="":
            continue
        filename = resList.split('\t')[0].split('/')[-1].replace(".png",".txt")
        with open(os.path.join(resultDir,filename),'w') as f:
            f.write(resList)


def clockwise(points:list):
    start, end = points[0], points[-1]
    if (pow(start[0],2)+pow(start[1],2))>=(pow(end[0],2)+pow(end[1],2)):
        return points
    if (pow(start[0],2)+pow(start[1],2))<(pow(end[0],2)+pow(end[1],2)):
        return points.reverse()


# 多项式拟合
def Curve_Fitting(points,deg):
    half = int(len(points)/2)
    x = [i[0] for i in points[:half]]
    y = [i[1] for i in points[:half]]

    parameter = np.polyfit(x, y, deg)    #拟合deg次多项式
    p = np.poly1d(parameter)             #拟合deg次多项式
    aa=''                               #方程拼接  ——————————————————
    for i in range(deg+1): 
        bb=round(parameter[i],2)
        if bb>0:
            if i==0:
                bb=str(bb)
            else:
                bb='+'+str(bb)
        else:
            bb=str(bb)
        if deg==i:
            aa=aa+bb
        else:
            aa=aa+bb+'x^'+str(deg-i)    #方程拼接  ——————————————————
    plt.scatter(x, y)     #原始数据散点图
    plt.plot(x, p(x), color='g')  # 画拟合曲线
   # plt.text(-1,0,aa,fontdict={'size':'10','color':'b'})
    plt.legend([aa,round(np.corrcoef(y, p(x))[0,1]**2,2)])   #拼接好的方程和R方放到图例
    plt.show()
#    print('曲线方程为：',aa)
#    print('     r^2为：',round(np.corrcoef(y, p(x))[0,1]**2,2))

from numpy import *

# 测试次序
def plottest(points,index):

    # plt.ion()
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    n = np.arange(len(x))

    plt.scatter(x, y, c='r')

    for i, txt in enumerate(n):
        plt.annotate(txt, (x[i], y[i]))
    # plt.ion()
    plt.figure(index)
    plt.pause(5)
    plt.close()


def main():
    types = ['Oval','Circle','Person']
    workdir = r'.\tools'
    for type in types:
        root = os.path.join(workdir,type)
        if not os.path.exists(root):
            continue

        if not os.path.exists(os.path.join(root,f"baseLabel_{type}.json")):
            # 找个需要标注的文件，并生成sample
            findFile(rootpath=root,type=type)

        if os.path.exists(os.path.join(root,'sample')):
            print("不存在基础标注数据，读取所有标注数据")
            jsonData = readJson(root)
        else:
            print("存在基础标注数据，直接读取文件")
            jsonData = json.load(open(os.path.join(root,f"baseLabel_{type}.json"), 'r', encoding='utf-8'))
        # 生成最终的标注文件
        if not os.path.exists(os.path.join(root,f"label_{type}.txt")):
            generalData(root, jsonData=jsonData, type=type)

    if not (os.path.exists(os.path.join(workdir,'image')) and os.path.exists(os.path.join(workdir,'label.txt'))) :
        mergefiles(workdir,types)


def test():
    points = [[64.20433436532508, 216.71826625386998], [53.80612244897959, 196.17346938775512], [46.40816326530613, 178.57142857142858], [43.091836734693885, 157.14285714285714], [42.58163265306122, 135.96938775510205], [48.19387755102041, 114.03061224489797], [57.37755102040816, 95.40816326530613], [69.62244897959184, 79.08163265306122], [83.65306122448979, 64.28571428571429], [99.9795918367347, 54.59183673469388], [121.15306122448979, 47.704081632653065], [142.3265306122449, 44.89795918367347], [165.03061224489795, 44.13265306122449], [181.6122448979592, 48.724489795918366], [202.78571428571428, 57.90816326530612], [218.6020408163265, 69.38775510204081], [230.33673469387753, 82.6530612244898], [244.11224489795921, 100.76530612244898], [252.53061224489795, 118.62244897959184], [256.6122448979592, 137.5], [256.86734693877554, 160.96938775510205], [252.27551020408163, 180.35714285714286], [243.34693877551018, 200.25510204081633], [267.3265306122449, 212.24489795918367], [276.2551020408163, 187.75510204081633], [281.6122448979592, 165.56122448979593], [282.12244897959187, 138.5204081632653], [277.53061224489795, 112.5], [268.60204081632656, 90.56122448979592], [251.51020408163265, 65.05102040816327], [235.69387755102042, 49.48979591836735], [215.28571428571428, 33.673469387755105], [193.60204081632654, 24.23469387755102], [168.3469387755102, 17.602040816326532], [139.26530612244898, 17.602040816326532], [114.01020408163265, 22.448979591836736], [92.07142857142858, 30.867346938775512], [69.87755102040816, 43.62244897959184], [50.744897959183675, 60.96938775510204], [35.183673469387756, 83.16326530612245], [23.448979591836732, 106.88775510204081], [19.112244897959187, 134.18367346938777], [18.602040816326536, 158.41836734693877], [22.683673469387756, 183.67346938775512], [31.867346938775512, 207.90816326530611], [43.46130030959753, 227.55417956656348]]
    # Curve_Fitting(points,5)
    pass

if __name__ == '__main__':
    main()
    # test()
