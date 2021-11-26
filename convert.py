import os,subprocess,shutil

#kendi key-value değerlerinizi ekleyiniz.
CATEGORYCOCOYOLO = {
	"key":indis
    }

def boxes_to_yolo(temporarySavePath,yoloFormatFolderSavePath):
    resp = {"result":True,"message":"yolo formatina donusum islemi yapildi."}
    temporaryDatasetFullPath = os.path.join(temporarySavePath,"boxes_dataset")

    try:
        if not os.path.exists(yoloFormatFolderSavePath):
            os.makedirs(yoloFormatFolderSavePath)

        command = "datum convert -i {} -if datumaro -f yolo -o {}".format(temporaryDatasetFullPath,yoloFormatFolderSavePath)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output,error=proc.communicate()
        code = proc.returncode
        error_str_message = error.decode("utf-8")
        if code != 0 and error_str_message != "":
            resp.update({"result":False,"message":error_str_message})
    except Exception as ex:
        resp.update({"result":False,"message":str(ex)})
    return resp

def shapes_to_boxes(datumaroFormatFolderPath,temporarySavePath):
    resp = {"result":True,"message":"Bbox donusum islemi yapildi."}
    temporaryDatasetFullPath = os.path.join(temporarySavePath,"boxes_dataset")
    try:
        if not os.path.exists(temporaryDatasetFullPath):
            os.makedirs(temporaryDatasetFullPath)
        command = "datum transform -t shapes_to_boxes -o {}  {}:datumaro".format(temporaryDatasetFullPath,datumaroFormatFolderPath)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output,error=proc.communicate()
        code = proc.returncode
        error_str_message = error.decode("utf-8")
        if code != 0 and error_str_message != "":
            resp.update({"result":False,"message":error_str_message})
    except Exception as ex:
        resp.update({"result":False,"message":str(ex)})
    return resp

def clearSpaceFolderNameAndSave(datumaroFormatFolderPath):
    resp = {"result":True,"message":"Klasor İsmi Dogru","filename":datumaroFormatFolderPath}
    try:
        if len(datumaroFormatFolderPath.split(" ")) >= 2:
            os.rename(datumaroFormatFolderPath,datumaroFormatFolderPath.replace(" ","_"))
            resp.update({"filename":datumaroFormatFolderPath.replace(" ","_")})
    except Exception as ex:
        resp.update({"result":False,"message":str(ex)})
    return resp

def convert_datumaro_to_yolo(datumaroFormatFolderPath,temporarySavePath,yoloFormatFolderPath):
    for foldername in os.listdir(datumaroFormatFolderPath):
        folderFullPath = os.path.join(datumaroFormatFolderPath,foldername)
        if os.path.isdir(folderFullPath): #klasor ise
            yoloFormatFolderSavePath = os.path.join(yoloFormatFolderPath,foldername)
            resultFolderName = clearSpaceFolderNameAndSave(folderFullPath)
            if resultFolderName["result"]:
                newfolderFullPath = resultFolderName["filename"]
                resultBbox = shapes_to_boxes(newfolderFullPath,temporarySavePath)

                if resultBbox["result"]:
                    resultYolo = boxes_to_yolo(temporarySavePath,yoloFormatFolderSavePath)

                    if resultYolo["result"]:
                        shutil.rmtree(temporarySavePath, ignore_errors=True)


def merge_yolo_format_dataset(mainYoloFolder,mergeYoloPath):

    f = open(os.path.join(mergeYoloPath,"classes.txt"), "w")
    for dtval in categoryCocoYolo:
        f.write(dtval)
        f.write("\n")
    f.close()
    matchCategoryIds = {}
    veriler = {}
    for root, dirs, files in os.walk(mainYoloFolder, topdown=False):
        for name in files:
            filename,ext = os.path.splitext(os.path.basename(os.path.join(root, name)))
            if ext == ".txt" and filename != "train":
                veriler.update({filename:[]})
                file1 = open(os.path.join(root, name), 'r')
                for line in file1:
                    veriler[filename].append(line)

            elif ext == ".names":
                file1 = open(os.path.join(root, name), 'r')
                for index,line in enumerate(file1):
                    line = line.replace("\n","")
                    matchCategoryIds.update({index:CATEGORYCOCOYOLO[line]})

                for vr in veriler:
                    if veriler[vr]: #bos olan txt dosyalarini temizler
                        f = open(os.path.join(mergeYoloPath,"{}.txt".format(vr)), "w")
                        for dtval in veriler[vr]:
                            newStr =""
                            arr = dtval.split(" ")
                            for index,d in enumerate(arr):
                                if index == 0:
                                    newStr+= str(matchCategoryIds[int(d)])+" "
                                elif index != len(arr)-1:
                                    newStr+= d+" "
                                else:
                                    newStr+= d

                            f.write(newStr)
                        f.close()
                veriler = {}

if __name__ == '__main__':
    #not datumaro formatinda klasor icinde her zaman bir annotations klsoru olmalidir.
    datumaroFormatDataset = ""
    temporarySavePath = ""
    yoloFormatDataset = ""
    convert_datumaro_to_yolo(datumaroFormatDataset,temporarySavePath,yoloFormatDataset)

    #elde edilen tum yolo modellerini birlestirmek icin ise
    mergeYoloPath = ""
    merge_yolo_format_dataset(yoloFormatDataset,mergeYoloPath)
