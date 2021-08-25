import json
import os
import shutil
from pathlib import Path

# 自动标注的条件是假设文字大小一致，根据字符长度进行判断，除了公司名称采用直接的数字作为标签，其他标签采用自定义并在该表中体现
# 5表示非公司名称的字符个数对应的实际标签
OvalTable = {5: "印章5", 6: "印章6", 15: "中编码", 13: "下编码"}
CircleTable = {13:"印章编码",5:"质检专用章",6:"法定代表人章"}

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
                    point = clockwise(point)
                    if point!=None:
                        index += 1
                        test(point,index)
                    labelRes.append({"transcription":text,"points":point})
                else:
                    point = jsonData[typeDict[len(text)]]
                    point = clockwise(point)
                    if point!=None:
                        index += 1
                        test(point,index)

                    labelRes.append({"transcription": text, "points": point})
            f.write(f"image/{texts[0]}_{type}.png\t{labelRes}\n")

def mergefiles(root,types):

    resultFile = os.path.join(root, "label.txt")
    if os.path.exists(resultFile):
        os.remove(resultFile)
    with open(resultFile,"a+") as f:
        for type in types:
            typepath = os.path.join(root, type)
            if not os.path.exists(typepath):
                continue
            folder = os.path.join(typepath,'image')
            dst_folder = os.path.join(root, 'image')
            copyTree(folder, dst_folder)  # 复制文件夹并覆盖
            label = os.path.join(typepath,f"label_{type}.txt")
            txt = open(label,'r').read()
            f.write(txt)

def clockwise(points:list):
    start, end = points[0], points[-1]
    if (pow(start[0],2)+pow(start[1],2))>=(pow(end[0],2)+pow(end[1],2)):
        return points
    if (pow(start[0],2)+pow(start[1],2))<(pow(end[0],2)+pow(end[1],2)):
        return points.reverse()




# 测试次序
def test(points,index):
    import numpy as np
    import matplotlib.pyplot as plt
    # plt.ion()
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    n = np.arange(len(x))

    # fig, ax = plt.subplots()

    plt.scatter(x, y, c='r')

    for i, txt in enumerate(n):
        plt.annotate(txt, (x[i], y[i]))
    # plt.ion()
    plt.figure(index)
    plt.pause(5)
    plt.close()



if __name__ == '__main__':
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

