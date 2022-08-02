import matplotlib.pyplot as plt
import numpy as np
import skimage.io

def visualise_emitter_parameters(ROIradius, path):
    folder_path = path
    imageset = skimage.io.imread(folder_path)

    meanintensities = []
    maxintensities = []
    ellipticites = []
    xinvmags = []
    yinvmags = []

    for i in range(len(imageset)):  # change number to open desired amount of emitters
        singleFrame = imageset[i, :, :]
        ROI_F = np.fft.fft2(singleFrame)
        xmagnitude = np.abs(ROI_F[0, 1])
        xinvmag = 1/xmagnitude
        ymagnitude = np.abs(ROI_F[1, 0])
        yinvmag = 1/ymagnitude
        calculated_ellipticity = xinvmag - yinvmag
        calculated_ellipticity = (calculated_ellipticity)
        meanintensity = np.sum(singleFrame)/((ROIradius*2 + 1)**2)

        maxIntensityvalue = 0
        # Check image intensity parameters with ideal image parameters.
        for row in range(len(singleFrame)):
            a = max(singleFrame[row])
            if(a > maxIntensityvalue):
                maxIntensityvalue = a

        meanintensities.append(meanintensity)
        maxintensities.append(maxIntensityvalue)
        ellipticites.append(calculated_ellipticity)
        xinvmags.append(xinvmag)
        yinvmags.append(yinvmag)

    figure, axis = plt.subplots(1, 4)


    axis[0].set_title("x inverse F. mag")
    #axis[0].hist(xinvmags, bins=55)
    axis[0].vlines(np.mean(xinvmags) - np.std(xinvmags), 0, 120, color='r', label='mean', colors="r",linewidth=1.5)
    axis[0].vlines(np.mean(xinvmags) + np.std(xinvmags), 0, 120, color='r', label='mean', colors="r",linewidth=1.5)

    below0, good0, above0 = [], [], []
    for x in xinvmags:
        if(x < np.mean(xinvmags) - np.std(xinvmags)):
            below0.append(x)
        if(x > np.mean(xinvmags) + np.std(xinvmags)):
            above0.append(x)
        if(x < np.mean(xinvmags) + np.std(xinvmags) and  x > np.mean(xinvmags) - np.std(xinvmags)):
            good0.append(x)

    #axis[0].hist(below0, bins=10, color='gray') 
    axis[0].hist(good0, bins=9, color='blue') 
    axis[0].hist(above0, bins=9, color='gray') 
    axis[0].set_ylabel("Counts")



    axis[1].set_title("y inverse F. mag")
    #axis[1].hist(yinvmags, bins=55)
    axis[1].vlines(np.mean(yinvmags) - np.std(yinvmags), 0, 180, color='r', label='mean', colors="r",linewidth=1.5)
    axis[1].vlines(np.mean(yinvmags) + np.std(yinvmags), 0, 180, color='r', label='mean', colors="r",linewidth=1.5)

    below, good, above = [], [], []
    for x in yinvmags:
        if(x < np.mean(yinvmags) - np.std(yinvmags)):
            below.append(x)
        if(x > np.mean(yinvmags) + np.std(yinvmags)):
            above.append(x)
        if(x < np.mean(yinvmags) + np.std(yinvmags) and  x > np.mean(yinvmags) - np.std(yinvmags)):
            good.append(x)

    axis[1].hist(below, bins=4, color='gray') 
    axis[1].hist(good, bins=6, color='blue') 
    axis[1].hist(above, bins=8, color='gray') 
    axis[1].set_ylabel("Counts")




    axis[2].set_title("ellipticity")
    #axis[2].hist(ellipticites, bins=55)
    axis[2].vlines(np.mean(ellipticites) - np.std(ellipticites), 0, 220, color='r', label='mean', colors="r",linewidth=1.5)
    axis[2].vlines(np.mean(ellipticites) + np.std(ellipticites), 0, 220, color='r', label='mean', colors="r",linewidth=1.5)

    below2, good2, above2 = [], [], []
    for x in ellipticites:
        if(x < np.mean(ellipticites) - np.std(ellipticites)):
            below2.append(x)
        if(x > np.mean(ellipticites) + np.std(ellipticites)):
            above2.append(x)
        if(x < np.mean(ellipticites) + np.std(ellipticites) and  x > np.mean(ellipticites) - np.std(ellipticites)):
            good2.append(x)

    axis[2].hist(below2, bins=8, color='gray') 
    axis[2].hist(good2, bins=6, color='blue') 
    axis[2].hist(above2, bins=8, color='gray') 
    axis[2].set_ylabel("Counts")



    axis[3].set_title("mean intensity counts")
    #axis[3].hist(meanintensities, bins=55) 
    axis[3].vlines(np.median(meanintensities) - np.std(meanintensities), 0, 100, color='r', label='mean', colors="r",linewidth=1.5)
    axis[3].vlines(np.median(meanintensities) + np.std(meanintensities), 0, 100, color='r', label='mean', colors="r",linewidth=1.5)

    below3, good3, above3 = [], [], []
    for x in meanintensities:
        if(x < np.median(meanintensities) - np.std(meanintensities)):
            below3.append(x)
        if(x > np.median(meanintensities) + np.std(meanintensities)):
            above3.append(x)
        if(x < np.median(meanintensities) + np.std(meanintensities) and  x > np.median(meanintensities) - np.std(meanintensities)):
            good3.append(x)

    axis[3].hist(below3, bins=4, color='gray') 
    axis[3].hist(good3, bins=8, color='blue') 
    axis[3].hist(above3, bins=6, color='gray') 
    #axis[3].hist(meanintensities, bins=18, color='gray') 
    axis[3].set_ylabel("Counts")

    print("Amount of emitter frames in file:", len(meanintensities))
    print("\n")
    print("mean intensity", np.mean(meanintensities))
    print("\n")    
    print("std dev intensities", np.std(meanintensities))
    print("mean max int 0:", np.mean(maxintensities))

    print("\n mean ellipticities : ", np.mean(ellipticites))
    print("std dev ellipticities", np.std(ellipticites))
    print("\n")

    print("mean x inv mag 0:", np.mean(xinvmags))
    print("mean y inv mag 0:", np.mean(yinvmags))


    
    plt.show()


if __name__ == "__main__":
    #visualise_emitter_parameters(4, "QdotParameterEstimation/goQdots/e525_1_filtered_1k_9x9_lp3_go.tiff")
    #visualise_emitter_parameters(4, "QdotParameterEstimation/goQdots/e605_1_filtered_1k_9x9_lp3_go.tiff")
    visualise_emitter_parameters(4, "QdotParameterEstimation/goQdots/e655_1_filtered_1k_9x9_lp3_go.tiff")
    #visualise_emitter_parameters(4, "QdotParameterEstimation/goQdots/e705_1_filtered_1k_9x9_lp3_go.tiff")


