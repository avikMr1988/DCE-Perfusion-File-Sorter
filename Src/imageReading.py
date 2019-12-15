import pydicom
import os
import shutil
import numpy as np
import cv2 as cv

def prepareFiles(path):
    thisDir             =   os.getcwd()
    dicomFiles          =   [x for x in os.listdir(path)]
    patientStudy        =   dict()
    patientImages       =   dict()
    for file in dicomFiles:
        dcmF = pydicom.dcmread(thisDir +'/WholeDataSet3rdRound/' + file,force=True)
        dataElemSeriesNr = dcmF.data_element("SeriesNumber")
        dataElemPatientStudy = dcmF.data_element("PatientName")
        if dataElemPatientStudy.value.original_string in patientStudy.keys():
            if dataElemSeriesNr.value.original_string in patientStudy[dataElemPatientStudy.value.original_string].keys():
                patientStudy[dataElemPatientStudy.value.original_string][dataElemSeriesNr.value.original_string].append(thisDir +'/WholeDataSet3rdRound/' + file)
            else:
                patientStudy[dataElemPatientStudy.value.original_string].__setitem__(dataElemSeriesNr.value.original_string,list())
                patientStudy[dataElemPatientStudy.value.original_string][dataElemSeriesNr.value.original_string].append(thisDir +'/WholeDataSet3rdRound/' + file)
        else:
            patientImages = dict()
            if dataElemSeriesNr.value.original_string in patientImages.keys():
                patientImages[dataElemSeriesNr.value.original_string].append(thisDir +'/WholeDataSet3rdRound/' + file)
            else:
                patientImages.__setitem__(dataElemSeriesNr.value.original_string,list())
                patientImages[dataElemSeriesNr.value.original_string].append(thisDir +'/WholeDataSet3rdRound/' + file)
            patientStudy.__setitem__(dataElemPatientStudy.value.original_string,patientImages)
    return patientStudy

def organizeData(path):
    patientStudy = prepareFiles(path)
    thisDir             =   os.getcwd()
    if not os.path.isdir("Patient Studies JPG"):
        os.makedirs("Patient Studies JPG")
    perfusionImages = dict()
    pCount = 1
    for study in patientStudy.keys():
        patientStudyPath = thisDir + '/Patient Studies JPG/' + 'Patient_' + str(pCount)
        if not os.path.isdir(patientStudyPath):
            os.makedirs(patientStudyPath)
        pCount = pCount + 1
        patientDetails = patientStudy[study]
        perfusionImages = dict()
        #t10Images = dict()
        for sNo in patientDetails.keys():
            images = patientDetails[sNo]
            for image in images:
                dcmF = pydicom.dcmread(image,force=True)
                imageAcquisitionType = dcmF.data_element("SeriesDescription").value
                if(imageAcquisitionType == "t1_vibe_tra_dyn"):
                    sliceNumber     =   dcmF.data_element("InstanceNumber").value.original_string
                    timePoint       =   dcmF.data_element("AcquisitionNumber").value.original_string
                    if sliceNumber in perfusionImages.keys():
                        perfusionImages[sliceNumber].append(image)
                    else:
                        perfusionImages.__setitem__(sliceNumber,list())
                        perfusionImages[sliceNumber].append(image)
        # Add when needed
                # else if(imageAcquisitionType == 't1_vibe_tra_pre_flip_2deg' or  imageAcquisitionType == 't1_vibe_tra_pre_flip_15deg'):
                #     sliceNumber     =   dcmF.data_element("InstanceNumber").value
                #     if sliceNumber in perfusionImages.keys():
                #         perfusionImages[sliceNumber].append(image)
                #     else:
                #         perfusionImages.__setitem__(sliceNumber,list())
                #         perfusionImages[sliceNumber].append(image)
                # else if(imageAcquisitionType == ''):
                # else if(imageAcquisitionType == ''):
                # else:
        for key in perfusionImages.keys():
            perfusionImagePath = patientStudyPath + '/Slice_' + str(key)
            if not os.path.isdir(perfusionImagePath):
                os.makedirs(perfusionImagePath)
            for image in perfusionImages[key]:
                ds= pydicom.dcmread(image)
                timePoint = ds.data_element("AcquisitionNumber").value.original_string
                imageData = ds.pixel_array
                center = ds.data_element("WindowCenter").value
                width = ds.data_element("WindowWidth").value

                min = center - int(width / 2)
                max = center + int(width/2)

                for row in range(0,imageData.shape[0]):
                    for col in range(0,imageData.shape[1]):
                        if imageData[row,col] < min:
                            imageData[row,col] = 0
                        elif imageData[row,col] > max:
                            imageData[row,col] = 255
                        else:
                            imageData[row,col] = int(imageData[row,col] * 255/(max - min))

                cvImage = np.zeros((imageData.shape[0],imageData.shape[1],3),dtype=np.uint16)
                cvImage[:,:,0] = imageData
                cvImage[:,:,1] = imageData
                cvImage[:,:,2] = imageData
                cv.imwrite(perfusionImagePath + '/' + timePoint + '.jpg',imageData)
                #shutil.copyfile(image,perfusionImagePath + '/' + os.path.basename(image))

                
            
        
organizeData('/home/avik/Downloads/Patient Data Sets/WholeDataSet3rdRound/')


    
""" import numpy as np
import cv2 as cv

dcmF = pydicom.dcmread('/home/avik/Downloads/Patient Data Sets/Patient Studies/Patient_1/Slice_1/46382682',force=True)
imageData = dcmF.pixel_array
center = dcmF.data_element("WindowCenter").value
width = dcmF.data_element("WindowWidth").value

min = center - int(width / 2)
max = center + int(width/2)
print(min,max)
for row in range(0,imageData.shape[0]):
    for col in range(0,imageData.shape[1]):
        if imageData[row,col] < min:
            imageData[row,col] = 0
        elif imageData[row,col] > max:
            imageData[row,col] = 255
        else:
            imageData[row,col] = int(imageData[row,col] * 255/(max - min))
print(imageData)
cvImage = np.zeros((imageData.shape[0],imageData.shape[1],3))
cvImage[:,:,0] = imageData
cvImage[:,:,1] = imageData
cvImage[:,:,2] = imageData
cvImage = cvImage/255
cv.imshow('',cvImage)
cv.waitKey(0)
cv.destroyAllWindows()
 """

