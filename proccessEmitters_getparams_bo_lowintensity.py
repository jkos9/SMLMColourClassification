import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFilter
import skimage.io
from scipy.ndimage import gaussian_filter
from skimage.feature import peak_local_max
import tifffile


class EmitterMovie:
    '''
    This program creates single emitter files from Tiff movies. 
    GaussianFiltersigma specifies amount of blur in image used for detecting peaks in a movie frame. 
    Use GFS1 = 0.01 and GFS2 = 3 to get the most emitter peaks.
    ROIradius specifies area of ROI in a single movie frame. ROIarea = (ROIradius * 2 + 1)**2
    BorderRegion specifies the emitters to be ignored by their proximity to the edge of image.
    Emitter_List_Length specifies the amount of frames in the final single emitter movie file.
    Edge_peak_threshold_value specifies the multiplication of threshold value which determines amount of peaks in a single emitter frame.

    This program classifies emitter frames based on parameters: Mean intensity of a frame, 
    x,y inverse Fourier magnitude and ellipticity. It can either work with specified input values or infer them from a movie.
    Acceptance ranges are generated by getting the median of mean intensity, mean of x,y inverse Fourier magnitudes and mean of ellitpicities
    (from a single frame) and taking 1 standard deviation.

    Use use_input_parameter_vals set to False to infer acceptance ranges.
    Test_emitter_list_length set the amount of emitters used for inference.

    Create EmitterMovie object with desired parameters. 
    Use add_to_list to get single emitters from input file.
    use save_emitter_list to save single emitter movie.
    '''
    def __init__(self, colour, GaussianFiltersigma1, GaussianFiltersigma2, ROIradius, BorderRegion, emitter_list_length, test_emitter_list_length, 
                edge_peak_threshold_value, use_input_parameter_vals, xinvmag_mean, xinvmag_stddev, yinvmag_mean, yinvmag_stddev,
                ellipticity_mean, ellipticity_stddev, median_IntensityRange, stddev_IntensityRange):
        self.colour = colour
        self.movie_emitter_list = [] 
        self.GaussianFiltersigma1 = GaussianFiltersigma1 
        self.GaussianFiltersigma2 = GaussianFiltersigma2
        self.ROIradius = ROIradius
        self.BorderRegion = BorderRegion
        self.emitter_list_length = emitter_list_length
        self.edge_peak_threshold_value = edge_peak_threshold_value #default 3, use lower value to be more selective.
        self.total_emitters_processed = 0
        self.good_emitters_added = 0

        self.use_input_parameter_vals = use_input_parameter_vals
        self.xinvmag_mean = xinvmag_mean
        self.xinvmag_stddev = xinvmag_stddev
        self.yinvmag_mean = yinvmag_mean
        self.yinvmag_stddev = yinvmag_stddev
        self.ellipticity_mean = ellipticity_mean
        self.ellipticity_stddev = ellipticity_stddev
        self.IntensityRange_median = median_IntensityRange
        self.IntensityRange_stddev = stddev_IntensityRange

        self.test_emitter_list_length = test_emitter_list_length # Default 1000
        self.test_emitter_list = 0

    def get_parameters(self, path):
        # read image
        intensities = []
        xinvmags = []
        yinvmags = []
        ellipticities = []

        image = skimage.io.imread(path)
        for frame in range(0, image.shape[0]):
            if(self.test_emitter_list < self.test_emitter_list_length): # specific movie length
                # For each frame get location of peak intensity values.
                # Get minimum value for threshold intensity using gaussian filters.
                # Values above threshold will be classed as emitter locations.
                singleFrame = image[frame, :, :]
                Gauss1FilteredImage = gaussian_filter(
                    singleFrame, sigma=self.GaussianFiltersigma1).astype(float)
                Gauss2FilteredImage = gaussian_filter(
                    singleFrame, sigma=self.GaussianFiltersigma2).astype(float)
                DoGFilteredImage = Gauss1FilteredImage-Gauss2FilteredImage
                MinValueLocalMax = np.std(DoGFilteredImage)*2
                localpeaks = peak_local_max(
                        DoGFilteredImage, threshold_abs=MinValueLocalMax)

                # remove emitters close to edge region due to differing intensity values
                markForDeletion = []
                for i in range(0, localpeaks.shape[0]):
                    if (localpeaks[i][0] <= (self.BorderRegion+1)) \
                                or (localpeaks[i][0] >= singleFrame.shape[0]-(self.BorderRegion+1)) \
                                or (localpeaks[i][1] <= (self.BorderRegion+1)) \
                                or (localpeaks[i][1] >= singleFrame.shape[1]-(self.BorderRegion+1)):
                            markForDeletion = np.append(markForDeletion, i)

                markForDeletion = np.int_(markForDeletion)
                localpeaks = np.delete(localpeaks, markForDeletion, axis=0)

                # Extract the ROI - we know it is centered around the localpeaks[l,:] position, with radius ROIradius
                for l in range(0, len(localpeaks)):
                    ROI = singleFrame[localpeaks[l, 0]-self.ROIradius:localpeaks[l, 0]+self.ROIradius+1,
                                          localpeaks[l, 1]-self.ROIradius:localpeaks[l, 1]+self.ROIradius+1]
                    # Define image parameters, x,y inverse fourier magnitude, intensity.
                    ROI_F = np.fft.fft2(ROI)
                    xmagnitude = np.abs(ROI_F[0, 1])
                    xinvmag = 1/xmagnitude
                    ymagnitude = np.abs(ROI_F[1, 0])
                    yinvmag = 1/ymagnitude

                    # Check for ellipticity by comparing inverse Fourier magnitudes
                    # Resulting ellipticity should be less than ellipticity_cval
                    calculated_ellipticity = xinvmag - yinvmag
                    MinValueLocalMaxR = np.std(ROI)*self.edge_peak_threshold_value

                    # Check for multiple emitter peaks in single image and on edges with specific edgevalue. 
                    ROIpeaks = peak_local_max(ROI, threshold_abs = MinValueLocalMaxR)
                    edgeValue = MinValueLocalMaxR*2
                    meanIntensityvalue = np.sum(ROI)/((self.ROIradius*2 + 1)**2)

                    # Check image intensity parameters with ideal image parameters and desired tiff file length.
                    if(self.test_emitter_list < self.test_emitter_list_length): # specific movie length
                        if((np.all(ROI[:, 0] < edgeValue)) and (np.all(ROI[:, self.ROIradius*2] < edgeValue)) and (np.all(ROI[0, :] < edgeValue)) and (np.all(ROI[self.ROIradius*2, :] < edgeValue))):
                            if(len(ROIpeaks) == 1): #amount of emitter peaks in ROI    
                                # if correct parameters adds to list
                                intensities.append(meanIntensityvalue)
                                xinvmags.append(xinvmag)
                                yinvmags.append(yinvmag)
                                ellipticities.append(calculated_ellipticity)
                                self.test_emitter_list += 1
                                # Stop appending if list length is reached.
        print("Test movie length:", self.test_emitter_list, "\n")
        self.IntensityRange_median = np.median(intensities)
        self.IntensityRange_stddev = np.std(intensities)          
        self.xinvmag_mean = np.mean(xinvmags)            
        self.xinvmag_stddev = np.std(xinvmags)
        self.yinvmag_mean = np.mean(yinvmags)
        self.yinvmag_stddev = np.std(yinvmags)
        self.ellipticity_mean = np.mean(ellipticities)
        self.ellipticity_stddev = np.std(ellipticities)

    def add_to_list(self, path):
        if(self.use_input_parameter_vals == False):
            # If false updates parameters by 
            self.get_parameters(path)

        # read image
        image = skimage.io.imread(path)
        for frame in range(0, image.shape[0]):
            if(len(self.movie_emitter_list) < self.emitter_list_length): # specific movie length
                # For each frame get location of peak intensity values.
                # Get minimum value for threshold intensity using gaussian filters.
                # Values above threshold will be classed as emitter locations.
                singleFrame = image[frame, :, :]
                Gauss1FilteredImage = gaussian_filter(
                   singleFrame, sigma=self.GaussianFiltersigma1).astype(float)
                Gauss2FilteredImage = gaussian_filter(
                    singleFrame, sigma=self.GaussianFiltersigma2).astype(float)
                DoGFilteredImage = Gauss1FilteredImage-Gauss2FilteredImage
                MinValueLocalMax = np.std(DoGFilteredImage)*2
                localpeaks = peak_local_max(
                    DoGFilteredImage, threshold_abs=MinValueLocalMax)

                # remove emitters close to edge region due to differing intensity values
                markForDeletion = []
                for i in range(0, localpeaks.shape[0]):
                    if (localpeaks[i][0] <= (self.BorderRegion+1)) \
                        or (localpeaks[i][0] >= singleFrame.shape[0]-(self.BorderRegion+1)) \
                        or (localpeaks[i][1] <= (self.BorderRegion+1)) \
                        or (localpeaks[i][1] >= singleFrame.shape[1]-(self.BorderRegion+1)):
                            markForDeletion = np.append(markForDeletion, i)

                markForDeletion = np.int_(markForDeletion)
                localpeaks = np.delete(localpeaks, markForDeletion, axis=0)

                # Extract the ROI - we know it is centered around the localpeaks[l,:] position, with radius ROIradius
                for l in range(0, len(localpeaks)):
                    ROI = singleFrame[localpeaks[l, 0]-self.ROIradius:localpeaks[l, 0]+self.ROIradius+1,
                                      localpeaks[l, 1]-self.ROIradius:localpeaks[l, 1]+self.ROIradius+1]
                    # Define image parameters, x,y inverse fourier magnitude, intensity.
                    ROI_F = np.fft.fft2(ROI)
                    xmagnitude = np.abs(ROI_F[0, 1])
                    xmaginv = 1/xmagnitude
                    ymagnitude = np.abs(ROI_F[1, 0])
                    ymaginv = 1/ymagnitude
                    maxIntensityvalue = 0
 
                    # Check for ellipticity by comparing inverse Fourier magnitudes
                    # Resulting ellipticity should be less than ellipticity_cval
                    calculated_ellipticity = xmaginv - ymaginv

                    self.total_emitters_processed += 1
                    MinValueLocalMaxR = np.std(ROI)*self.edge_peak_threshold_value

                    # Check for multiple emitter peaks in single image and on edges with specific edgevalue. 
                    ROIpeaks = peak_local_max(ROI, threshold_abs = MinValueLocalMaxR)
                    edgeValue = MinValueLocalMaxR*2

                    maxIntensityvalue = np.sum(ROI)/((self.ROIradius*2 + 1)**2)

                    # Check image intensity parameters with ideal image parameters and desired tiff file length.
                    if(len(self.movie_emitter_list) < self.emitter_list_length): # specific movie length
                        if(self.IntensityRange_median - self.IntensityRange_stddev < maxIntensityvalue and maxIntensityvalue <  self.IntensityRange_median + self.IntensityRange_stddev): #within specific intensity range
                            if((np.all(ROI[:, 0] < edgeValue)) and (np.all(ROI[:, self.ROIradius*2] < edgeValue)) and (np.all(ROI[0, :] < edgeValue)) and (np.all(ROI[self.ROIradius*2, :] < edgeValue))):
                                if(len(ROIpeaks) == 1): #amount of emitter peaks in ROI    
                                    if(self.ellipticity_mean - self.ellipticity_stddev < calculated_ellipticity and calculated_ellipticity < self.ellipticity_mean + self.ellipticity_stddev):  
                                        if(self.xinvmag_mean - self.xinvmag_stddev < xmaginv and xmaginv < self.xinvmag_mean + self.xinvmag_stddev):
                                            if(self.yinvmag_mean - self.yinvmag_stddev < ymaginv and ymaginv < self.yinvmag_mean + self.yinvmag_stddev):
                                                # if correct parameters adds to list
                                                self.movie_emitter_list.append(ROI)
                                                self.good_emitters_added += 1
                                        #print(self.good_emitters_added)
                                        # Stop appending if list length is reached
        if(len(self.movie_emitter_list) == self.emitter_list_length):
                        print("Emitter list length reached!")

    def save_emitter_list(self, name):
        # Save numpy array as tiff file.
        # Saves in parent directory.
        print("\n Emitter list length: ",self.good_emitters_added)
        print("\n Acceptance ratio of emitters detected:", (self.good_emitters_added/self.total_emitters_processed)*100,"%")
        movie_emitters_array = np.asarray(self.movie_emitter_list)
        tifffile.imwrite(name, movie_emitters_array)
        print("\n Tiff file created! \n")


if __name__ == "__main__":

    # Acceptance data
    median_intensity = 2504.0123456790125
    std_dev_intensity = 882.0797299810998
    xinvmag_mean = 2.4878015175981878e-05
    xinvmag_std = 1.5717972575586092e-05
    yinvmag_mean = 2.4031295141239076e-05
    yinvmag_std = 1.5884859638799993e-05
    mean_ellipticity = 8.467200347428055e-07
    std_dev_ellipticity = 6.000592627336967e-06

    movie_length = 1000 # Final filtered movie size. 
    test_movie_length = 1000 # Test movie size from which acceptance values are calculated.
        # If file is bad or settings are wrong will generate movies of lesser size than specified. 

    GaussianFiltersigma1 = 0.01 # Gaussian blurring filter sigmas.
    GaussianFiltersigma2 = 3
    ROIradius = 4 # Generates ROI of (2*ROIradius + 1) ** 2.
    BorderRegion = 20 # Specify amount of distance from edges where emitters will be discarded. 
    edge_peak_threshold_value = 10 # Multiplier, specifies thresholf level in ROI to find secondary emitters.
                                # Use lower value to be more selective. 
    use_input_param_vals = False # If False, generates acceptance data from file, if True uses input data.

    E7051 = EmitterMovie("525", GaussianFiltersigma1, GaussianFiltersigma2, ROIradius, BorderRegion, movie_length, test_movie_length, 
                        edge_peak_threshold_value, use_input_param_vals, xinvmag_mean, xinvmag_std, yinvmag_mean, yinvmag_std, mean_ellipticity,
                        std_dev_ellipticity, median_intensity, std_dev_intensity)
    E7051.add_to_list("qdot_emitters/2022.06.08_wN2/Cheap_Objective_NA1.25/BO_525/BO_Qdots525nm_0.2nM_488nm_125mW_QuadFilter_50ms_f1000_1/BO_Qdots525nm_0.2nM_488nm_125mW_QuadFilter_50ms_f1000_1_MMStack_Default.ome.tif")
    E7051.save_emitter_list("e525_1_filtered_1k_9x9_lp10_bo")  


    E7052 = EmitterMovie("525", GaussianFiltersigma1, GaussianFiltersigma2, ROIradius, BorderRegion, movie_length, test_movie_length, 
                        edge_peak_threshold_value, use_input_param_vals, xinvmag_mean, xinvmag_std, yinvmag_mean, yinvmag_std, mean_ellipticity,
                        std_dev_ellipticity, median_intensity, std_dev_intensity)
    E7052.add_to_list("qdot_emitters/2022.06.08_wN2/Cheap_Objective_NA1.25/BO_705/BO_Qdot705nm_0.2nM_488nm_125mW_QuadFilter_50ms_f1000_1/BO_Qdot705nm_0.2nM_488nm_125mW_QuadFilter_50ms_f1000_1_MMStack_Default.ome.tif")
    E7052.save_emitter_list("e705_1_filtered_1k_9x9_lp10_bo")  

    '''
    E7053 = EmitterMovie("525", GaussianFiltersigma1, GaussianFiltersigma2, ROIradius, BorderRegion, movie_length, test_movie_length, 
                        edge_peak_threshold_value, use_input_param_vals, xinvmag_mean, xinvmag_std, yinvmag_mean, yinvmag_std, mean_ellipticity,
                        std_dev_ellipticity, median_intensity, std_dev_intensity)
    E7053.add_to_list("qdot_emitters/2022.06.08_wN2/Cheap_Objective_NA1.25/BO_705/BO_Qdot705nm_0.2nM_488nm_125mW_QuadFilter_50ms_f1000_3/BO_Qdot705nm_0.2nM_488nm_125mW_QuadFilter_50ms_f1000_3_MMStack_Default.ome.tif")
    E7053.save_emitter_list("e705_3_filtered_10k_9x9_lp10_bo")  
    '''



