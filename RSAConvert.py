import csv
import glob
import os
import re
import subprocess

class Converter:
    def __init__(self, sub):
        self.subName = sub
        self.fsDir = '/Applications/freesurfer/subjects/'
        self.roiDir = '/Volumes/SD_Back/Grad_Projects/FB/ROIs/'
        self.sumaDir = '/Applications/freesurfer/subjects/' + sub + '/surf/SUMA/'
    def checkROINames(self,roiDir,roi,filt):
        # Filt is the search pattern for the 1D result files
        print(roi)
        if filt[0] == 'L':
            hemi = 'lh'
        else:
            hemi = 'rh'
        self.hemi = hemi
        roiName = filt[2:]
        print(filt)
        print(filt[0])
        print(hemi)
        print(roiName)
        newROI = hemi + '.' + roiName + '.label'
        subprocess.check_output(['mv', roiDir+'/'+roi, roiDir+'/'+newROI])
        return newROI
    def getROINames(self,maskDir,filt):
        # Filt is the search pattern for the 1D result files
        sub = self.subName
        os.chdir(maskDir)
        rois = glob.glob('*' + filt[0] + filt[1])
        if len(rois)>0:
            tmp = [self.checkROINames(maskDir,r,filt[0]) for r in rois if(r[0:1] != 'lh' or r[0:1] != 'rh' or filt[0] != 'lh' or filt[0] != 'rh')] 
            self.ROIs = tmp
            self.maskDir = maskDir
            return 1
        else:
            return 0
    def getVerts(self,roiDir,roi,skipLines,readCol):
        print(roi)
        surf2read = roiDir + roi
        print(surf2read)
        roiReader = csv.reader(open(surf2read),delimiter=' ',skipinitialspace=True)
        track = 0
        roiVerts = []
        for r in roiReader:
            if track>skipLines:
                if isinstance(readCol,int):
                    if float(r[readCol])>0:
                        if readCol==0: #reading a label file
                            roiVerts.append(int(r[readCol]))
                        else: #reading a 1D file
                            roiVerts.append(track-(skipLines+1))
                else:
                    roiVerts.append(r)
            track+=1
        return roiVerts
    def write_results2label(self,roi,inputDir,hemi,outDir):        
        sub = self.subName
        maskDir = self.roiDir + 'surface_masks_new/'
        #  Gets Relevant Vertices for ROI
        print(sub)
        inputDir = maskDir + sub + '/Func2Anat/'
        sumaDir = self.sumaDir
        surface = hemi + '.pial.asc'
        roiVerts = self.getVerts(inputDir,roi,20,7)
        print(roiVerts[0])
        pialCoords = self.getVerts(sumaDir,surface,1,'surf')
        print(pialCoords[0])
        
        #  Generate Labels
        label = []
        for r in roiVerts:
            foo = []
            foo.append(r)
            foo.extend(pialCoords[r])
            label.append(foo)
        label_format = ['  '.join(map(repr, r)) for r in label] # Formats labels so it's easy to print
        
        print(label_format[0])
        # Print ROI to .label file
        header = ['#!ascii label  , from subject ' + sub + ' vox2ras=TkReg',len(label_format)] # Prints Header for Freesurfer Format
        # [:-3] since results files should be saved as 1D file... could use regexp in the future
        with open(outDir + roi[:-3] + '.label', 'w', newline='') as out:
                    spamwriter = csv.writer(out, delimiter='\n');
                    spamwriter.writerow(header)

        with open(outDir + roi[:-3] + '.label', 'a', newline='') as out:
                spamwriter = csv.writer(out, delimiter='\n');
                spamwriter.writerow(label_format)
    
    def write_label21D(self,hemi,roi,inputDir,outDir):
        sumaDir = self.sumaDir
        roiVerts = self.getVerts(inputDir,roi,1,0)
        surfReader = csv.reader(open(sumaDir + hemi + ".pial.asc"),delimiter=' ',skipinitialspace=True)
        # Identifies ROI Vertices on the Surface    
        i=0;
        for row in surfReader:
            if i==1:
                r = [0]*int(row[0])
            elif i>1:
                if i+1 in roiVerts:
                    r[i] = 1;
            i=i+1
        # Prints Out 1D Label File
        newName = roi.replace('label','1D')
        if not os.path.isdir(outDir):
            os.mkdir(outDir)
        with open(outDir + newName, 'w', newline='') as out:
            spamwriter = csv.writer(out, delimiter='\n');
            spamwriter.writerow(r)
    def mapAnat2Func(self,roi,hemi):
        maskDir = self.roiDir + 'surface_masks_new/' + self.subName + '/Anat2Func/'
        cmd = []
        cmd.append('/Volumes/SD_Back/Grad_Projects/FB/ROIs/mapAnat2Func.sh')
        cmd.append(maskDir)
        cmd.append(self.sumaDir)
        cmd.append(roi)
        cmd.append(hemi)
        subprocess.check_output(['echo', maskDir])
        foo = subprocess.check_output(cmd)
    def mapFunc2Anat(self,roi,hemi):
        maskDir = self.roiDir + 'surface_masks_new/' + self.subName
        cmd = []
        cmd.append('/Volumes/SD_Back/Grad_Projects/FB/ROIs/mapFunc2Anat.sh')
        cmd.append(maskDir)
        cmd.append(self.sumaDir)
        cmd.append(roi)
        cmd.append(hemi)
        subprocess.check_output(['echo', maskDir])
        foo = subprocess.check_output(cmd)
        