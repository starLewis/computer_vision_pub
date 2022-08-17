# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 23:33:57 2019

@author: lewisliu
"""

import os

#upload the API token
def get_kaggle_credentials():
    token_dir = os.path.join(os.path.expanduser("~"), ".kaggle")
    token_file = os.path.join(token_dir, "kaggle.json")
    
    if not os.path.isdir(token_dir):
        os.mkdir(token_dir)
        
    try:
        with open(token_file,"r") as f:
            pass
    except IOError as no_file:
        try:
            from google.colab import files
        except ImportError:
            raise no_file
            
        uploaded = files.upload()
        
        if "kaggle.json" not in uploaded:
            raise ValueError("You need an API key!")
            
        with open(token_file, "wb") as f:
            f.write(uploaded["kaggle.json"])
            
        os.chmod(token_file, 600)
        
get_kaggle_credentials()