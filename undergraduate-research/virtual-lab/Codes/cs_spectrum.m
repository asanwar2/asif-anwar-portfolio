% % For an NaI scintillation detector, the energy resolution is 10% or
% % below. Using 10% as our resolution, that would mean that the FWHM for
% % every photopeak is 10% of the mean energy for that peak. Using FWHM =
% % 2.35 * sigma, we were able to produce the photopeaks using a gaussian
% % distribution

rme = 511; % rest mass energy in keV
init_en = 662; % initial energy in keV

xray = normrnd(32, 1.36, 10000, 1);
figure
histogram(xray, 25,'FaceColor','k','EdgeAlpha',0,'FaceAlpha',1) 
xlim([0 50])
text(40, 810,'x-ray peak','FontSize',25)
hold on

lead = normrnd(90, 3.83, 10000, 1);
histogram(lead, 75,'FaceColor','k','EdgeAlpha',0,'FaceAlpha',1) 
xlim([0 200])

noiseul = 185;
noisell = 30;
noise = noisell + (noiseul-noisell).*rand(10000,1);
histogram(noise, 35,'FaceColor','k','EdgeAlpha',0,'FaceAlpha',1)
xlim([0 500])

backscatter = normrnd(184.3, 7.84, 10000, 1);
histogram(backscatter, 50,'FaceColor','k','EdgeAlpha',0,'FaceAlpha',1)
xlim([51 450])
text(200, 350,'backscatter peak', 'FontSize',25)

for theta = 0.5
    emax = (init_en)/(1+((init_en/rme)*(1-cos(theta)))); % compton equation to find scattered photon energy
end

for theta = pi
    emin = (init_en)/(1+((init_en/rme)*(1-cos(theta)))); % compton equation to find scattered photon energy
end

compton = emin + (emax-emin).*rand(10000,1);
histogram(compton, 100,'FaceColor','k','EdgeAlpha',0,'FaceAlpha',1)
text(400, 180,'compton edge','FontSize',25)
xlim([0 600])

gamma = normrnd(661.66, 28.2, 10000, 1);
histogram(gamma, 50,'FaceColor','k','EdgeAlpha',0,'FaceAlpha',1)
xlim([501 800])
text(700, 500,'gamma photopeak', 'FontSize',25)

allhist = [xray(:); backscatter(:); compton(:); gamma(:)];
xlim([0 1000])
ylim([0 1500])
title ('Cs-137 spectrum','FontSize',35);
set(gca,'FontSize',20)
xlabel("Energy (keV)",'FontSize',30);
ylabel("Counts",'FontSize',30);