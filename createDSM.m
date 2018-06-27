function [target_dsm,rsaWords] = createDSM(setLength,targetDSM,varargin)

dsmDir = '/Volumes/SD_Back/Grad_Projects/FB/Model_DSM/';
% If Using Auditory Sim Mat
target_dsm= csvread(fullfile(dsmDir,['rsa' targetDSM '.csv']),1,1);
rsasetWords = {'SAND' 'TANNED' 'MASK' 'TEAMS' 'TOADS' 'DENSE' 'MOST' 'NEST' ...
    'DANCE' 'SEND' 'TEND' 'MAX'  'SEAMS' 'ZONES' 'NETS' 'MEANT' 'MIST' ... 
    'MAPS' 'PEACE' 'MEAT' 'NOSE' 'PEAT' 'KNEES' 'SOAK' 'SPIN' 'SPIT' 'STOOP' ...
    'SKIN' 'SNIP' 'STOKE'};

if strcmpi(setLength,'full')||strcmpi(setLength,'identity')
    words = {'SAND','TANNED','MASK','TEAMS','TOADS','DENSE','MOST','NEST',...
        'DANCE','SEND','TEND','MAX','SEEMS','ZONES','NETS','MEANT','MIST', ...
        'MAPS','PEACE','MEAT','NOSE','PEAT','KNEES','SOAK','SPIN','SPIT', ...
        'STOOP','SKIN','SNIP','STOKE'};
elseif strcmpi(setLength,'cvcc')
    words = {'SAND','TANNED','MASK','TEAMS','TOADS','DENSE','MOST','NEST',...
        'DANCE','SEND','TEND','MAX','SEAMS','ZONES','NETS','MEANT','MIST', ...
        'MAPS'};
elseif strcmpi(setLength,'cvcc_train')
    words = {'SAND','TANNED','MASK','TEAMS','TOADS','DENSE','MOST','NEST',...
        'DANCE'};
elseif strcmpi(setLength,'cvcc_untrain')
    words = {'SEND','TEND','MAX','SEEMS','ZONES','NETS','MEANT','MIST', ...
        'MAPS'};
elseif strcmpi(setLength,'MOA')||strcmpi(setLength,'POA')||strcmpi(setLength,'VOI')...
        ||strcmpi(setLength,'All_Art_Features')||strcmpi(setLength,'AVG')
%     words = {'SAND','TANNED','MASK','TEAMS','TOADS','DENSE','MOST','NEST',...
%         'DANCE','SEND','TEND','MAX','SEAMS','ZONES','NETS','MEANT','MIST',...
%         'MAPS','SPIN','SPIT','STOOP','SKIN','SNIP','STOKE'};
    words = {'SAND','TANNED','MASK','TEAMS','TOADS','DENSE','MOST','NEST',...
        'DANCE','SEND','TEND','MAX','SEAMS','ZONES','NETS','MEANT','MIST', ...
        'MAPS'};
end

track = 1;
for w = 1:length(words)
    tmp = find(strcmpi(rsasetWords,words{w}));
    if ~isempty(tmp)
        idx(track) = tmp;
        rsaWords2{track} = words{w};
        track = track+1;
    end
end
rsaWords = rsaWords2;  
target_dsm = target_dsm(idx,idx); % reorder the matrix so that the ordre of the rows and columns of the similarity matrix are the same as that of ds.sa.labels

if strcmpi(setLength,'identity')
    target_dsm = (diag(ones(1,length(rsaWords)),0)-1)*-1;
end

end
