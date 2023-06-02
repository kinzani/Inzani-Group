# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 20:50:57 2022

@author: rated
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

def Article():
    universalFontSize = 18.0
    mpl.rcParams["font.sans-serif"] = ["Arial"]
    mpl.rcParams["xtick.direction"] = "in"
    mpl.rcParams["ytick.direction"] = "in"
    mpl.rcParams["legend.frameon"] = False
    mpl.rcParams["font.size"] = universalFontSize
    plt.rc("lines", markersize=10)
    plt.rc("axes", labelsize=universalFontSize)
    plt.rc("axes", titlesize=universalFontSize)
    plt.rc("figure", figsize=(7,7))
    plt.rc("figure", titlesize=universalFontSize)
    plt.rc("savefig", bbox="tight")
    plt.rc("figure", titlesize=universalFontSize)
    plt.rc("axes", titlesize=universalFontSize)
    mpl.rcParams["xtick.labelsize"] = universalFontSize
    mpl.rcParams["ytick.labelsize"] = universalFontSize
    
    #alternative colours - Tol muted
    #colours = ['#332288','#117733', '#882255', '#88ccee', '#44aa99', '#ddcc77', '#999933', '#cc6677', '#aa4499', '#dddddd']
    #lineType = ["-", "--", ":", "-.", "-", "--", ":", "-.", "-", "--"]
    
    #now using Tol high-contrast
    colours = ["#bb5566", "#004488", "#ddaa33", "#000000"]
    lineType = ["-", "--", "-.", ":"]
    
    articleCycler = (cycler(color=colours) + cycler(linestyle=lineType))
    plt.rc("axes", prop_cycle = articleCycler)
    plt.rc("lines", linewidth=2)
    #mpl.rcParams["savefig.dpi"] = 1000


#Article()
#import numpy as np
#x = np.linspace(0, 2 * np.pi, 50)
#offsets = np.linspace(0, 2 * np.pi, 4, endpoint=False)
#yy = np.transpose([np.sin(x + phi) for phi in offsets])
#plt.plot(yy)
