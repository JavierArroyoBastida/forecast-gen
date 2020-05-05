from __future__ import division
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt


class Error_Generator(object):
    
    def __init__(self, phi=0.6, n=100, mae=-3., err_bou=6.):
        
        self.phi     = phi
        self.n       = n
        self.mae     = mae
        self.err_bou = err_bou
        # Define A_ub matrix. All rows are to define that the error values
        # should be between a threshold range from the value defined by 
        # the AR model but the last one that computes the mae error
        A = np.identity(n)
        np.fill_diagonal(A[1:,:], -phi)
        A = np.concatenate((A, np.zeros((n,1)) ), axis=1)
        self.A_ub = np.concatenate((A,-A), axis=0)
        
        # Define the MAE equation
        self.A_eq = np.ones((1,n+1))
        self.A_eq[0,:n] = 1/float(n)
        self.b_eq = np.asarray(mae) 
        
        # Only penalize the difference between the given mae and the actual mae
        self.c = np.zeros(n+1)
        self.c[n] = 1
        
        # Fix bounds
        l = np.ones(n+1)*(-err_bou)
        l[n] = 0.
        u = np.ones(n+1)*err_bou
        self.bounds = np.column_stack((l,u))
        

    def generate_error(self):
        """
        Generates a random error vector of length `n`, that results
        in the mean AVERAGE error (mae) equal to `mae` using optimization.
        The error vector is based on the AR(1) model. The autocorrelation is
        controlled by the parameter `phi`. The first element of the output
        vector is 0 (no error). The higher `phi`, the higher chance of
        getting a vector with some bias. `mae` serves to drive the desired
        bias towards a desired value
    
        :parameter phi: float from 0 to 1, autocorrelation coefficient
        :parameter n: int, output vector length
        :parameter mae: float, mean AVERAGE error
        :parameter err_bou: float, absolute bound of the resulting error
        :return: 1D numpy array or a tuple (1D numpy array, list) if hist is True
        
        """
        
        if self.mae == 0:
            return np.zeros(self.n)
    
        
        # Define b_ub vector with the values of the threshold range
        b = np.abs(np.random.normal(loc=0, scale=2., size=self.n))
        self.b_ub = np.concatenate((b,b), axis=0)
        
        res = linprog(self.c, A_ub=self.A_ub, b_ub=self.b_ub, A_eq=self.A_eq, b_eq=self.b_eq,
                      bounds=tuple(map(tuple, self.bounds)))
        
        return res['x'][:-1]


if __name__ == "__main__":

    e = Error_Generator()
    pd.DataFrame(e.generate_error()).plot()
    plt.show()
