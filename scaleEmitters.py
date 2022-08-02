import matplotlib.pyplot as plt
import numpy as np
import skimage.io
from sympy import imageset
import tifffile

class scaledEmitterMovie:
    '''
    This program splices and scales tiff single emitter files to one movie of desired length for input to a neural network.
    It scales by centering each emitter to have mean 0 and taking the euclidian 2 norm.
    Create scaledEmitterMovie object with desired length and use add_to_movie to add emitter files.
    Use save_movie to save file.
    '''
    def __init__(self, MovieLength):
        self.MovieLength = MovieLength
        self.imageset = []
        self.imageset = np.array(self.imageset)
        self.Movie = []

    def add_to_movie(self, folder_path):
        if(len(self.imageset) == 0 ): 
            imagesetFile = skimage.io.imread(folder_path)
            imagesetFile = np.array(imagesetFile)
            self.imageset = imagesetFile
        else:
            imagesetFileNew = skimage.io.imread(folder_path) 
            imagesetFileNew = np.array(imagesetFileNew)
            self.imageset = np.vstack((self.imageset, imagesetFileNew))
    
    def normalize_2d(self, matrix):
        # Only this is changed to use 2-norm put 2 instead of 1
        norm = np.linalg.norm(matrix, 2)
        # normalized matrix
        matrix = matrix/norm  
        return matrix

    def save_movie(self, name):
        for i in range(self.MovieLength): # change number to open desired amount of emitters   
            singleFrame = self.imageset[i,:,:]
            #create function to center data
            center_function = lambda x: x - x.mean()
            #apply function to original NumPy array
            singleFrame = center_function(singleFrame)
            singleFrame = self.normalize_2d(singleFrame)
            self.Movie.append(singleFrame)     
        frames = np.array(self.Movie)
        tifffile.imwrite(name, frames)
        print("tiff file created!")


if __name__ == "__main__":
    e605 = scaledEmitterMovie(10000)
    e605.add_to_movie("e655_1_filtered_10k_9x9_lp3_bo.tiff")
    e605.add_to_movie("e655_2_filtered_10k_9x9_lp3_bo.tiff")    
    e605.add_to_movie("e655_3_filtered_10k_9x9_lp3_bo.tiff")
    e605.add_to_movie("e655_4_filtered_10k_9x9_lp3_bo.tiff")
    e605.add_to_movie("e655_5_filtered_10k_9x9_lp3_bo.tiff")
    e605.add_to_movie("e655_6_filtered_10k_9x9_lp3_bo.tiff")


    e605.save_movie("e655lp3_bo")
