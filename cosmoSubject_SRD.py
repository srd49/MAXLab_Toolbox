import scipy.io as sio
import matlab.engine
from pathlib import Path
import RSAConvert as rsa_convert
eng = matlab.engine.start_matlab()

class cosmoSubject:
    def __init__(self,sub,scan,analysis,targetDsmInfo,\
                 dataDir='/Volumes/SD_Back/Grad_Projects/FB/audioRSA/data',smoothing='noNormNoSmooth', \
                 rm_badVo =1,meshDens=64,maskFlag=0,featureMetric = 'count',featureCount=50,nPerms = 1):
        self.subj = sub
        self.rm_badVo =rm_badVo
        self.dataDir = dataDir
        self.preprocDir = dataDir + '/preproc/' + scan
        self.betaDir = dataDir + '/results/' + scan + '/GLM/' + smoothing + '/' + sub
        self.subjSurfPath = self.preprocDir + '/' + sub + '/surf'
        self.meshDens = meshDens
        self.maskFlag= maskFlag
        self.featureMetric = featureMetric # count or radius
        self.featureCount = featureCount
        self.nPerms = nPerms;
        self.corrType = 'Spearman'
        self.setLength = 'CVCC_train' 
        self.targetDsmInfo = targetDsmInfo
        self.roiFlag=0
        self.resultsDir = dataDir + '/results/' + scan + '/' + analysis +'/' + self.targetDsmInfo + '/' + self.setLength + '/' + sub
        self.betaFile = self.betaDir + '/beta_' + self.setLength
    def getTargetDSM(self):
        target_dsm,rsaWords= eng.createDSM(self.setLength,self.targetDsmInfo,nargout=2); # need to recreate this function in python
        self.target_dsm = target_dsm
        self.rsaWords = rsaWords
    def getParams(self):
        return 'ToDo'
    def setDsParams(self,numWords):
        chunks = matlab.double([1]*numWords)
        targets = eng.transpose(matlab.double(list(range(1,numWords+1))));
        labels = self.rsaWords
        return {'chunks': chunks, 'targets': targets,'labels':labels}

    def getData(self,betaFile,numWords=18):
        DS_params = self.setDsParams(numWords)
        data_fn= betaFile + '+tlrc';
        ds=eng.cosmo_fmri_dataset(data_fn,'chunks',DS_params['chunks'],'targets',DS_params['targets'],'labels',DS_params['labels']);
        self.ds = ds
        
    def getSurfaces(self):
        inflated_fn= '{0}/{1}'.format(self.subjSurfPath, 'ico{0}_mh.inflated_alCoMmedial.asc'.format(str(self.meshDens)))
        v_inf,f_inf=eng.surfing_read(inflated_fn,nargout=2);
        pial_fn= '{0}/{1}'.format(self.subjSurfPath, 'ico{0}_mh.pial_al.asc'.format(str(self.meshDens)))
        white_fn= '{0}/{1}'.format(self.subjSurfPath, 'ico{0}_mh.smoothwm_al.asc'.format(str(self.meshDens)))
        surfDef = (white_fn,pial_fn)
        return {'surfDef':surfDef,'v_inf':v_inf,'f_inf':f_inf}

    def getNbrs(self):
        nbrFile = self.subjSurfPath + '/' + 'nbrhood_meshDense_' + str(self.meshDens) + '_metric_' + self.featureMetric \
        + '_' + str(self.featureCount) + '_mask_' + str(self.maskFlag) + '.mat'
        from pathlib import Path
        my_file = Path(nbrFile)
        if not my_file.is_file():
            surfInfo = self.getSurfaces()
            nbrhood,vo,fo,out2in= eng.cosmo_surficial_neighborhood(self.ds,surfInfo['surf_def'],self.featureMetric,self.featureCount,nargout=4)
        else:
            mat_contents = eng.load(nbrFile)
            nbrhood = mat_contents['nbrhood']
            vo = mat_contents['vo']
            fo  =mat_contents['fo']
            center_ids = matlab.double(list(range(1,len(mat_contents['nbrhood']['neighbors'])+1)))
        return {'center_ids':center_ids,'vo':vo,'fo':fo,'nbrhood':nbrhood}
    
    def getMeasure(self):
        measure_args={'type':self.corrType,'target_dsm':self.target_dsm,'center_data':1}
        return measure_args
    
    def getRoiVox(self,roi,nbrInfo):
        self.roiFlag=1
        self.roi=roi
        roiDir = '{0}/{1}/{2}/'.format('/Volumes/SD_Back/Grad_Projects/FB/ROIs/surface_masks_new',self.subj,'Anat2Func')
        roiName = '{0}_func.1D'.format(roi)
        roiFile = '{0}{1}'.format(roiDir,roiName)
        nbrInfo['center_ids'] = matlab.double([1]) #set to 1 for ROI based analysis since first nbr will contain ROI
        
        my_file = Path(roiFile)
        if my_file.is_file():
            x = rsa_convert.Converter(self.subj)
            roiVerts = x.getVerts(roiDir,roiName,21,7)
            roiVerts  = [v+2 for v in roiVerts] # Check this adding one business... indexing might be wrong somewhere
            if roiName[0:2] == 'rh':
                roiVerts  = [v+40962 for v in roiVerts]

            vox = []
            for r in roiVerts:
                tmp = nbrInfo['nbrhood']['neighbors'][r][0] 
                vox.extend(list(tmp[0:len(tmp)]))
            vox = set(vox)
            vox = list(vox)

            nbrInfo['nbrhood']['neighbors'][0] = matlab.double(matlab.double(vox))
            return nbrInfo
        
    def getPlotting(self):
        nbrInfo = self.getNbrs()
        surfInfo = self.getSurfaces()
        plotting = {'vo':nbrInfo['vo'],'fo':nbrInfo['fo'],'v_inf':surfInfo['v_inf'],'f_inf':surfInfo['f_inf']}
        return plotting
    def createSuffix(self):
        if self.roiFlag is 1:
            suffix = '{0}_meshDens_{1}_mask_{2}_rmBadVo_{3}_{4}.mat'.format(self.corrType,str(self.meshDens), \
                                                                         str(self.maskFlag),str(self.rm_badVo),self.roi)
        else:
            suffix = '{0}_{1}_{2}_meshDens_{3}_mask_{4}_rmBadVo_{5}.mat'.format(self.featureMetric,str(self.featureCount), \
                                                                                 self.corrType,str(self.meshDens), \
                                                                                 str(self.maskFlag),str(self.rm_badVo))
        suffix = '{0}/{1}'.format(self.resultsDir,suffix)
        self.suffix = suffix
        return suffix
    def runRSA(self,nbrInfo,nproc,plotting):
        measure_args=self.getMeasure();
        for perm in range(1,self.nPerms+1):
#             if perm>1:
#                 # Permutes Targets and is later used to permute the model DSM in the function cosmo_target_dsm_corr_measure
#                 ds['sa']['targets'] = eng.cosmo_randomize_targets(self.ds)
            ds_cv= eng.rsaWrapper(self.ds,nbrInfo['nbrhood'],measure_args,nbrInfo['center_ids'],nproc, plotting, self.suffix);
            
        return ds_cv
    
        
#     def setRoiVox():
    
#     def setVox():

#     def getVox():

#     def plotResults():
