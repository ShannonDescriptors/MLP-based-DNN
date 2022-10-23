### This script could run MLP only model for pchembl/MW prediction (of IC50 of Tissue Factor Pathway Inhibitor) using combination of Shannon entropies (SMILES Shannon, SMARTS Shannon, InChiKey Shannon and SMILES partial/ fractional Shannon) and MW as descriptors


# import the necessary packages
from imutils import paths
import random
import os
import numpy as np
import pandas as pd


from KiNet_mlp import KiNet_mlp

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import SGD
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Model

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

import scipy
from sklearn.metrics import mean_absolute_percentage_error,mean_absolute_error,mean_squared_error

from rdkit import Chem
import re
import math



# Getting the list of molecules from csv file obtained from ChEMBL database
df = pd.read_csv('Tissue_Factor_Pathway_Inhibitors_IC50_only_equal_values_with_SMILES.csv', encoding='cp1252') 
df_MW = df['Molecular Weight'].values ## The MW for ach molecule
df_target = df['pChEMBL Value'].values
print(df_target)

### Calculating MW normalized df_target
df_target_norm = df['pChEMBL Value'].values ## Defining normalized df_target
for i in range(0,len(df_target)):
    df_target_norm[i] = df_target[i]/df_MW[i] 
df['pChEMBL Value'] = df_target_norm
print("Shape of the pChEMBL Value/MW labels array", df_target.shape)

    
#  Grab the maximum/ minimum in the label column
maxPrice = df_target_norm.max() 
minPrice = df_target_norm.min()




###------------------------------------------------------Shannon Entropy Generation: SMILES/ SMARTS/ InChiKey--------------------------------------------------------------------------------------------------

### comment this below section if SMILES Shannon is not used
###---------------------------------------------------------------------SMILES Shannon-------------------------------------------------------------------------------------------------------------------------
# Generate a new column with title 'shannon_smiles'. Evaluate the Shannon entropy for each smile string and store into 'shannon_smiles' column of df table

### Inserting the new column as the 2nd column in df
df.insert(1, "shannon_smiles", 0.0)

# smiles
SMI_REGEX_PATTERN = r"""(\[[^\]]+]|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\(|\)|\.|=|#|-|\+|\\|\/|:|~|@|\?|>>?|\*|\$|\%[0-9]{2}|[0-9])"""
regex = re.compile(SMI_REGEX_PATTERN)

shannon_arr = []
for p in range(0,len(df['shannon_smiles'])):
    
    molecule = df['Smiles'][p]
    tokens = regex.findall(molecule)
    
    ### Frequency of each token generated
    L = len(tokens)
    L_copy = L
    tokens_copy = tokens
    
    num_token = []
    
    
    for i in range(0,L_copy):
        
        token_search = tokens_copy[0]
        num_token_search = 0
        
        if len(tokens_copy) > 0:
            for j in range(0,L_copy):
                if token_search == tokens_copy[j]:
                    # print(token_search)
                    num_token_search += 1
            # print(tokens_copy)        
                    
            num_token.append(num_token_search)   
                
            while token_search in tokens_copy:
                    
                tokens_copy.remove(token_search)
                    
            L_copy = L_copy - num_token_search
            
            if L_copy == 0:
                break
        else:
            pass
        
    # print(num_token)
    
    ### Calculation of Shannon entropy
    total_tokens = sum(num_token)
    
    shannon = 0
    
    for k in range(0,len(num_token)):
        
        pi = num_token[k]/total_tokens
        
        # print(num_token[k])
        # print(math.log2(pi))
        
        shannon = shannon - pi * math.log2(pi)
        
    print("shannon entropy: ", shannon)
    shannon_arr.append(shannon)
        
    
# print(shannon)     
df['shannon_smiles']= shannon_arr

###-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### comment this below section if SMARTS Shannon is not used
###---------------------------------------------------------------------SMARTS Shannon-------------------------------------------------------------------------------------------------------------------------
### Generate a new column with title 'shannon_smarts'. Evaluate the Shannon entropy for each smile string and store into 'shannon_smarts' column of df table


### Inserting the new column as the 2nd column in df
df.insert(2, "shannon_smarts", 0.0)


### smarts
smarts_REGEX_PATTERN =  r"""(\[[^\]]+]|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\(|\)|\.|=|#|-|\+|\\|\/|:|~|@|\?|>>?|\*|\$|\%[0-9]{2}|[0-9])"""
regex = re.compile(smarts_REGEX_PATTERN)


shannon_arr = []
for p in range(0,len(df['shannon_smarts'])):
    
    smiles = df['Smiles'][p]
    mol = Chem.MolFromSmiles(smiles)
    # mol = Chem.AddHs(mol)
    m_smarts = Chem.MolToSmarts(mol)
    
    molecule = m_smarts
    tokens = regex.findall(molecule)
    # print(tokens)
    
    ### Frequency of each token generated
    L = len(tokens)
    L_copy = L
    tokens_copy = tokens
    
    num_token = []
    
    
    for i in range(0,L_copy):
        
        token_search = tokens_copy[0]
        num_token_search = 0
        
        if len(tokens_copy) > 0:
            for j in range(0,L_copy):
                if token_search == tokens_copy[j]:
                    # print(token_search)
                    num_token_search += 1
            # print(tokens_copy)        
                    
            num_token.append(num_token_search)   
                
            while token_search in tokens_copy:
                    
                tokens_copy.remove(token_search)
                    
            L_copy = L_copy - num_token_search
            
            if L_copy == 0:
                break
        else:
            pass
        
    # print(num_token)
    
    ### Calculation of Shannon entropy
    total_tokens = sum(num_token)
    
    shannon = 0
    
    for k in range(0,len(num_token)):
        
        pi = num_token[k]/total_tokens
        
        # print(num_token[k])
        # print(math.log2(pi))
        
        shannon = shannon - pi * math.log2(pi)
    
    # shannon = math.exp(-shannon)    
        
    print("shannon entropy on smarts: ", shannon)
    shannon_arr.append(shannon)  
    
df['shannon_smarts']= shannon_arr  
###-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### comment this below section if InChiKey Shannon is not used
###---------------------------------------------------------------------InChiKey Shannon-------------------------------------------------------------------------------------------------------------------------
### Generate a new column with title 'shannon_inchikey'. Evaluate the Shannon entropy for each smile string and store into 'shannon_inchikey' column of df table

### InChiKey: reading all letters except special characters
df.insert(3, "shannon_inchikey", 0.0)

# InChiKey regex definition
InChiKey_REGEX_PATTERN = r"""([A-Z])"""
regex = re.compile(InChiKey_REGEX_PATTERN)


def shannon_entropy_inch(ik):
    
    molecule = ik
    tokens = regex.findall(molecule)
    # print(tokens)
    # tokens = kmer_tokenizer(molecule, ngram=10)
    
    ### Frequency of each token generated
    L = len(tokens)
    L_copy = L
    tokens_copy = tokens
    
    num_token = []
    
    
    for i in range(0,L_copy):
        
        token_search = tokens_copy[0]
        num_token_search = 0
        
        if len(tokens_copy) > 0:
            for j in range(0,L_copy):
                if token_search == tokens_copy[j]:
                    # print(token_search)
                    num_token_search += 1
            # print(tokens_copy)        
                    
            num_token.append(num_token_search)   
                
            while token_search in tokens_copy:
                    
                tokens_copy.remove(token_search)
                    
            L_copy = L_copy - num_token_search
            
            if L_copy == 0:
                break
        else:
            pass
        
    # print(num_token)
    
    ### Calculation of Shannon entropy
    total_tokens = sum(num_token)
    
    shannon = 0
    
    for k in range(0,len(num_token)):
        
        pi = num_token[k]/total_tokens
        
        # print(num_token[k])
        # print(math.log2(pi))
        
        shannon = shannon - pi * math.log2(pi)
    
    # shannon = math.exp(-shannon)    
        
    return shannon  


shannon_arr = []
for p in range(0,len(df['shannon_inchikey'])):

    smiles = df['Smiles'][p]
    mol = Chem.MolFromSmiles(smiles)
    # mol = Chem.AddHs(mol)
    m_inchkey = Chem.MolToInchiKey(mol)
    ik = m_inchkey.split("-")
    # print("InchiKey splitted", ik)
    # print("\n")

    shannon_entropy = 0
    for i in range(len(ik)):
    
        if i<=1:
            shannon_entropy_by_parts = shannon_entropy_inch(ik[i])
            shannon_entropy = shannon_entropy + shannon_entropy_by_parts  
            # print(shannon_entropy_by_parts)
        else:
            freq = 1/25 ### Inchikey contains total 25 characters, apart from 2 hyphens
            shannon_entropy_by_parts = - freq * math.log2(freq)
            shannon_entropy = shannon_entropy + shannon_entropy_by_parts  
            # print(shannon_entropy_by_parts)
        
        
    print("shannon entropy on inchikey: ", shannon_entropy)
    shannon_arr.append(shannon_entropy) 
    
df['shannon_inchikey']= shannon_arr      

###------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------      

###---------------------------------------------------------------------padding for partial/ fractional Shannon-------------------------------------------------------------------------------------------------------------------------

## Constructing the padded array of partial shannon per molecule
def ps_padding(ps, max_len_smiles):
    
    len_ps = len(ps)
    
    len_forward_padding = int((max_len_smiles - len_ps)/2)
    len_back_padding = max_len_smiles - len_forward_padding - len_ps
    
    ps_padded = list(np.zeros(len_forward_padding))  + list(ps) + list(np.zeros(len_back_padding))
    
    return ps_padded 
###-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


### generating a dictionary of atom occurrence frequencies with the following atoms in the database: 'H', 'B', 'C', 'Si', 'N', 'P', 'O', 'S', 'F', 'Cl', 'Se', 'Br', 'I'
def freq_atom_list(atom_list_input_mol):
    
    atom_list = ['H', 'B', 'C', 'Si', 'N', 'P', 'O', 'S', 'F', 'Cl', 'Se', 'Br', 'I'] 
    dict_freq = {}
    
    ### adding keys
    for i in range(len(atom_list)):
        dict_freq[atom_list[i]] = 0  ### The values are all set 0 initially
    # print(dict_freq)
    
    ### update the value by 1 when a key in encountered in the string
    for i in range(len(atom_list_input_mol)):
        dict_freq[ atom_list_input_mol[i] ] = dict_freq[ atom_list_input_mol[i] ] + 1
    
    ### The dictionary values as frequency array
    freq_atom_list =  list(dict_freq.values())/ (  sum(  np.asarray (list(dict_freq.values()))  )    )
    
    # print(list(dict_freq.values()))
    # print(freq_atom_list )
    
    ### Getting the final frequency dictionary
    ### adding values to keys
    for i in range(len(atom_list)):
        dict_freq[atom_list[i]] = freq_atom_list[i]  
        
    # print(dict_freq)
    freq_atom_list = dict_freq
    
        
    return freq_atom_list


### generating a dictionary of bond occurrence frequencies with the following bond types: 'SINGLE', 'DOUBLE', 'TRIPLE', 'QUADRUPLE', 'AROMATIC', 'HYDROGEN', 'IONIC'
def freq_bond_list(bond_list_input_mol):
    
    bond_list = ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUADRUPLE', 'AROMATIC', 'HYDROGEN', 'IONIC'] 
    dict_freq = {}
    
    ### adding keys
    for i in range(len(bond_list)):
        dict_freq[bond_list[i]] = 0  ### The values are all set 0 initially
    # print(dict_freq)
    
    ### update the value by 1 when a key in encountered in the string
    for i in range(len(bond_list_input_mol)):
        dict_freq[ bond_list_input_mol[i] ] = dict_freq[ bond_list_input_mol[i] ] + 1
    
    ### The dictionary values as frequency array
    freq_bond_list =  list(dict_freq.values())/ (  sum(  np.asarray (list(dict_freq.values()))  )    )
    
    # print(list(dict_freq.values()))
    # print(freq_bond_list )
    
    ### Getting the final frequency dictionary
    ### adding values to keys
    for i in range(len(bond_list)):
        dict_freq[bond_list[i]] = freq_bond_list[i]  
        
    # print(dict_freq)
    freq_bond_list = dict_freq
    
        
    return freq_bond_list

### estimating the maximum length of SMILES strings in the database
len_smiles = []
for j in range(0,len( df['Smiles'])):
    
    mol = Chem.MolFromSmiles( df['Smiles'][j])
    # mol = Chem.AddHs(mol)
    
    k=0
    for atom in mol.GetAtoms():
        k = k +1 
    len_smiles.append(k)
    
max_len_smiles = max(len_smiles)



### collecting the features to use as descriptor array

shannon_arr = []
fp_combined = []
MW_list = []

for i in range(0,len( df['Smiles'])):  
     
    
    mol_smiles =  df['Smiles'][i]
  
    # getting the rdkit mol from the SMILES string
    mol = Chem.MolFromSmiles(mol_smiles)
    # mol = Chem.AddHs(mol)
  
    ### estimating the partial or fractional shannon for an atom type => the current node
    
    # getting the total Shannon entropy
    total_shannon = df['shannon_smiles'][i]
    shannon_arr.append( total_shannon )
  
    # The atom list as per rdkit in string form
    atom_list_input_mol = []
    for atom_rdkit in mol.GetAtoms():
        atom_list_input_mol.append(str(atom_rdkit.GetSymbol()))     
        
    # getting the atom frequency dictionary   
    freq_list_input_mol = freq_atom_list(atom_list_input_mol)
  
  # ### The bond list as per rdkit in string form
  # bond_list_input_mol = []
  # for i in range(len(mol.GetBonds())):
  #   bond_list_input_mol.append(str(mol.GetBonds() [i].GetBondType()))
    
  # ### bond frequency dictionary  
  # freq_list_input_mol_bond = freq_bond_list(bond_list_input_mol)  
  
    ps = [] # partial Shannon or fractional Shannon empty array
    for atom_rdkit in mol.GetAtoms():
        atom_symbol = atom_rdkit.GetSymbol()
        atom_type = atom_symbol ### atom symbol in atom type
      
        partial_shannon = freq_list_input_mol[atom_type] * total_shannon
        ps.append( partial_shannon )
      
      # # ### atom frequency mapping
      # ps.append( freq_list_input_mol[atom_type] )
  
    # applying padding of the partial Shannon array
    ps_arr = ps_padding(ps, max_len_smiles)     
    fp_combined.append(ps_arr)

  # ### Adding the bond frequency to the padded atom frequency list
  # fp_combined =  list(ps_arr) + list(freq_list_input_mol_bond.values())

# partial shannon_entropy as feature or descriptor column
fp_mol = pd.DataFrame(fp_combined)


### constructing a new df column containng only MW, Shannon entropy values ana targets or labels
df_1 = pd.DataFrame( df['Molecular Weight'].values)
df_2 = pd.DataFrame(df['shannon_smiles'].values)
df_3 = pd.DataFrame(df['shannon_smarts'].values)
df_4 = pd.DataFrame(df['shannon_inchikey'].values)
df_5 = pd.DataFrame(df['pChEMBL Value'].values)

# Getting the max & min of the target column
maxPrice = df.iloc[:,-1].max()
minPrice = df.iloc[:,-1].min() 

# Concatenated data table with descriptor and target columns
df_new = pd.concat([ df_1, df_2, df_3, df_4 ,fp_mol, df_5], axis = 1)

# df_new = pd.concat([ df_1, df_2, df_3 ], axis = 1)
# df_new = pd.concat([ df_1, df_2, fp_mol, df_5], axis = 1)
# df_new = pd.concat([ df_1, df_2, fp_mol, df_5], axis = 1)
# df_new = pd.concat([ df_1, fp_mol, df_5], axis = 1)


    
print("[INFO] constructing training/ testing split")
split = train_test_split(df_new, test_size = 0.2, random_state = 42) 

# Distribute the input data columns in train & test splits
(XtrainTotalData, XtestTotalData) = split  # split format always is in (data_train, data_test, label_train, label_test)

# Normalizing the target column: The last column is the labels for this training
XtrainLabels  = XtrainTotalData.iloc[:,-1]/ (maxPrice)
XtestLabels  = XtestTotalData.iloc[:,-1]/ (maxPrice)   

 
# defining the 1st column (mol. wt.) & 2nd col (shannon entropy) & 3rd column (smarts entropy) & 4th column (inchikey entropy) & 5th column (partial Shannon entropy) as X data
XtrainData = (XtrainTotalData.iloc[:,0:-1])
XtestData = (XtestTotalData.iloc[:,0:-1])
print("XtrainData shape",XtrainData.shape)
print("XtestData shape",XtestData.shape)


# perform min-max scaling each continuous feature column to the range [0 1]
cs = MinMaxScaler()
trainContinuous = cs.fit_transform(XtrainTotalData.iloc[:,0:-1])
testContinuous = cs.transform(XtestTotalData.iloc[:,0:-1])


print("[INFO] processing input data after normalization....")
XtrainData, XtestData = trainContinuous,testContinuous ## Feeding single array as XtrainData and XtestData

#create the MLP model
mlp = KiNet_mlp.create_mlp(XtrainData.shape[1], regress = False) # the input dimension to mlp would be shape[1] of the matrix i.e. column features
print("shape of mlp", mlp.output.shape)



# Processing output of MLP model
combinedInput = mlp.output
print("shape of combinedInput",combinedInput.shape)

# Defining the final FC layers 
x = Dense(100, activation = "relu") (combinedInput)
x = Dense(10, activation = "relu") (combinedInput)
x = Dense(1, activation = "linear") (x)
print("shape of x", x.shape)


# Defining final model as 'model'
model = Model(inputs = mlp.input, outputs = x)
print("shape of mlp input", mlp.input.shape)



# initialize the optimizer and compile the model
print("[INFO] compiling model...")
opt = SGD(lr= 1.05e-6, decay = 0)
model.compile(loss = "mean_absolute_percentage_error", optimizer = opt)

#train the network
print("[INFO] training network...")
trainY = XtrainLabels
testY = XtestLabels

epoch_number = 500
BS = 5;

# Defining the early stop to monitor the validation loss to avoid overfitting.
early_stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=1000, verbose=1, mode='auto')


# Model fitting across epochs
# shuffle = False to reduce randomness and increase reproducibility
H = model.fit( x = XtrainData , y = trainY, validation_data = ( XtestData, testY), batch_size = BS, epochs = epoch_number, verbose=1, shuffle=False, callbacks = [early_stop]) 


# evaluate the network
print("[INFO] evaluating network...")
preds = model.predict(XtestData,batch_size=BS)

# compute the difference between the predicted and actual values and then compute the % difference and absolute % difference
diff = preds.flatten() - testY
PercentDiff = (diff/testY)*100
absPercentDiff = (np.abs(PercentDiff)).values

# compute the mean and standard deviation of absolute percentage difference
mean = np.mean(absPercentDiff)
std = np.std(absPercentDiff)
print("[INF0] mean {: .2f},  std {: .2f}".format(mean, std) )


## Plotting Predicted  vs Actual values
N = len(testY)
colors = np.random.rand(N)
x = testY * maxPrice
y =  (preds.flatten()) * maxPrice
plt.scatter(x, y, c=colors)
plt.plot( [0,maxPrice],[0,maxPrice] )
plt.xlabel('Actual pchembl/MW', fontsize=18)
plt.ylabel('Predicted pchembl/MW', fontsize=18)
plt.savefig('pChEMBL_MW_with_shannon_partial_shannon.png')
plt.show()


####-------------------------------------------------------------------------------------------------------Evaluating standard statistics of model performance--------------------------------------------------------------------

# ### MAE as a function
# def mae(y_true, predictions):
#     y_true, predictions = np.array(y_true), np.array(predictions)
#     return np.mean(np.abs(y_true - predictions))

# ### The MAE estimated
# print("The mean absolute error estimated: {}".format( mae(x, y) )) 

### The MAPE
print("The mean absolute percentage error: {}".format( mean_absolute_percentage_error(x, y) ) )   

### The MAE
print("The mean absolute error: {}".format( mean_absolute_error(x, y) ))    
    
### The MSE
print("The mean squared error: {}".format( mean_squared_error(x, y) ))  

### The RMSE
print("The root mean squared error: {}".format( mean_squared_error(x, y, squared= False) ) )    

### General stats
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
print("The R^2 value between actual and predicted target:", r_value**2)


# plot the training loss and validation loss
plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, epoch_number ), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, epoch_number ), H.history["val_loss"], label="val_loss")
plt.title("Training loss and Validation loss")
plt.xlabel("Epoch #")
plt.ylabel("Loss")
plt.legend()
plt.savefig('loss@epochs_pChEMBL_MW_with_shannon_partial_shannon')

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------