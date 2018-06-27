function corrs = rsaWrapper(ds,nbrhood,measure_args,center_ids,nproc,plotting,resultsFile)

%% Performs RSA
save('~/Desktop/test.mat','ds','nbrhood','measure_args','center_ids','nproc')
nbrhood.neighbors = nbrhood.neighbors';
ds_cv= cosmo_searchlight(ds,nbrhood,@cosmo_target_dsm_corr_measure,measure_args,...
        'center_ids',center_ids,'nproc',nproc);
corrs = ds_cv.samples(center_ids);

ds_cv.samples = corrs;

ds_cv.v_inf_out=plotting.v_inf;
ds_cv.f_inf_out=plotting.f_inf;
ds_cv.vo=plotting.vo;
ds_cv.fo=plotting.fo;
opt.ShowEdge=false;
opt.Grid = [0 0 0];
opt.verbose = 0;
opt.DataRange = [0 .2];
opt.ColBarSize = [0 0 0 0];
opt.View = [270 0];
ds_cv.opt = opt;

resultsDir = fileparts(resultsFile);
if ~exist(resultsDir,'dir')
    mkdir(resultsDir)
end
save(resultsFile,'ds_cv');