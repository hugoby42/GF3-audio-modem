# Header file for OFDM, add libraries and functions here


import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd

class CamG:
    def __init__(self, K, cp, modulation, P=0):
        self.K = K                  # number of OFDM subcarriers i.e. DFT size
        self.cp = cp                # length of cyclic prefix: default 25% of block
        self.P = P                  # number of pilot carriers per block
        self.pilot_value = None     # Know value that pilot transmits

        
        self.all_carriers = np.arange(self.K)                                   # indicies of all subcarriers [0... K-1]
        try: self.pilot_carriers = self.all_carriers[::self.K//self.P]          # Pilot carriers every K/Pth carrier
        except: self.pilot_carriers = np.array([])                              # Exception for no pilot carriers
        self.data_carriers = np.delete(self.all_carriers, self.pilot_carriers)  # Remaining carriers are data carriers
        
        
        
        self.modulation = modulation    # Modulation method
        
        if(self.modulation == "QPSK"):
            self.mapping_table = {      # Mapping table
                (0,0) : (1+1j)/np.sqrt(2),
                (1,0) : (1-1j)/np.sqrt(2),
                (1,1) : (-1-1j)/np.sqrt(2),
                (0,1) : (-1+1j)/np.sqrt(2),
            }
            self.mu = 2     # Bits per symbol
        
        elif(self.modulation == "QAM"):
            self.mapping_table = {      # Mapping table
                (0,0) : (1+0j),
                (0,1) : (0+1j),
                (1,1) : (-1-0j),
                (1,0) : (0-1j),
            }
            self.mu = 2     # Bits per symbol
            
        else:
            raise ValueError("Invalid Modulation Type")
            
        
        self.bits_per_symbol = len(self.data_carriers) * self.mu            # Bits per OFDM symbol = number of carriers x modulation index


    # Shapes serial bits into parallel stream for OFDM -- needs adjusting for multiple OFDM symbols
    def SP(self, bits):
        return bits.reshape(len(self.data_carriers), self.mu)
        
    # Shapes parallel bits back into serial stream
    def PS(self, bits):
        return bits.reshape((-1,))
    
    
    # Maps the bits to symbols -- needs adjusting for multiple OFDM symbols
    def map(self, bits):
        if(type(bits) != np.ndarray): raise ValueError("Bits must be numpy array")
        return np.array([self.mapping_table[tuple(b)] for b in bits])
    
    
    # De-maps symbols to bits using min distance
    def demap(self, symbols):
        if(type(symbols) != np.ndarray): raise ValueError("Symbols must be numpy array")
        
        demapping_table = {v : k for k, v in self.mapping_table.items()}
        # Array of possible constellation points
        constellation = np.array([x for x in demapping_table.keys()])
        
        # Calulate distance of each received symbol to each point in the constellation
        dists = np.array([abs(y.reshape((-1,1)) - constellation.reshape((1,-1))) for y in symbols])

        # For each received symbol choose the nearest constellation point
        const_index = dists.argmin(axis=2)
        hardDecision = constellation[const_index]
        
        # Transform constellation points into bit groups
        return np.array([np.vstack([demapping_table[C] for C in hardDecision[i,:]]) for i in range(hardDecision.shape[0]) ]), hardDecision
    
    
    # Allocates symbols and pilots to OFDM symbol -- needs adjusting for multiple OFDM symbols
    def OFDM_symbol(self, payload):
        symbol = np.zeros(self.K, dtype=complex) # overall K subcarriers
        try: symbol[self.pilot_carriers] = self.pilot_value     # Allocate pilot subcarriers
        except: None
        symbol[self.data_carriers] = payload          # Allocate data carriers
        return symbol
    
    
    # Add the cyclic prefix -- needs adjusting for multiple OFDM symbols
    def add_cp(self, time_data):
        cyclic_prefix = time_data[-self.cp:]            # take the last cp samples
        return np.hstack([cyclic_prefix, time_data])    # add them to the beginning
    
    
    # Remove the cyclic prefix
    def remove_cp(self, signal):
        return np.array([signal[i,self.cp:(self.cp+self.K)] for i in range(signal.shape[0])])         # Only taking indicies of the data we want
    
    
    # Calculate channel estimate from pilot carriers
    def channel_est(self, data):
        # Not yet implemented
        return
        
    # Extract data carriers from all carriers -- needs adjusting for multiple OFDM symbols
    def get_data(self, equalised): 
        return equalised[self.data_carriers]
    
    
    # Prints out key OFDM attributes
    def __repr__(self):
        return  'Number of Sub Carriers: {:.0f} \nCyclic prefix length: {:.0f} \nModulation method: {}'.format(self.K, self.cp, self.modulation)





# IFFT
def IFFT(data):
    return np.array([np.fft.ifft(data[i,:]) for i in range(data.shape[0])])


# FFT
def FFT(data):
    return np.array([np.fft.fft(data[i,:]) for i in range(data.shape[0])])
    
# Equalise the received OFDM signal using the estimated channel coefficients
def equalise(data, h_est):
    return np.array([data[i,:] / h_est for i in range(data.shape[0])])
        
        
 
 


        

