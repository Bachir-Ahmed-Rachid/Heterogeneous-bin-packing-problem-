#Import the libraries
import pyomo.environ as pyo
from pyomo.environ import *
#importer le pakage qui permet d'utiliser les solver 
from pyomo.opt import SolverFactory
#importer pandas pour utiliser sheets
import pandas as pd

#__________________________________________________________________

#Inputs
data_wights=pd.read_excel('DATA _HBPP.xlsx',sheet_name='inputs')#importe Items from sheet

data_wights['bins']=["bin_"+str(i+1) for i in range(len(data_wights.Items))]#creat upper bound for the number of bin used(number of bins used =number of items)

data_capacity=pd.read_excel('DATA _HBPP.xlsx',sheet_name='capacity')#importe Items from sheet

bins_Type={"bin_Type"+str(i+1):data_capacity.Bin_Capacity[i] for i in range(len(data_capacity.Bin_Capacity))}#list of bins Type

items_wights={data_wights.Items[i]:data_wights.Wights[i] for i in range(len(data_wights.Items))}#Object that present every items with it's wight
data_capacity=pd.read_excel('DATA _HBPP.xlsx',sheet_name='capacity')#importe Items from sheet
Capacity=data_capacity['Bin_Capacity']
items_lenght=len(data_wights)#nomber of items

#__________________________________________________________________


#model creation
model=pyo.ConcreteModel()

#__________________________________________________________________


# Variables creation
# x[i, j,t] = 1 if item i is packed in bin j of capacity t.
# y[j,t] = 1 if bin j of type t is used.

Items=[data_wights.Items[i] for i in range(len(data_wights.Items))]#Items variation
Bins=[data_wights.bins[i] for i in range(len(data_wights.bins))]#Bins variation
model.x =pyo.Var(Items,Bins,bins_Type.keys(),within = Binary)
model.y =pyo.Var(Bins,bins_Type.keys(),within = Binary)
x=model.x
y=model.y


#__________________________________________________________________


# Constraints formuation
# Each item must be in exactly one bin.
model.unicity = ConstraintList()
for i in data_wights['Items']:
    model.unicity.add(sum(x[i,j,t] for j in data_wights['bins'] for t in bins_Type.keys()) == 1)
# The amount packed in each bin cannot exceed its capacity.
model.capacity = ConstraintList()
for j in data_wights['bins']:
    for t in bins_Type.keys():
        model.capacity.add(expr = sum( items_wights[i]*x[i,j,t] for i in Items ) <= bins_Type[t]*y[j,t] )


#__________________________________________________________________


#Define the objective
model.obj = Objective(expr = sum( [y[j,t]*bins_Type[t] for j in data_wights['bins'] for t in bins_Type.keys()]) , sense = minimize )



opt=SolverFactory('gurobi')#gurobi
results=opt.solve(model,tee=True)
num_bins = 0.
for j in data_wights['bins']:
    for t in bins_Type.keys():
        Type=t
        if pyo.value(y[j,t]) == 1:
            bin_items = []
            bin_weight = 0
            for i in data_wights['Items']:
                for t in bins_Type.keys():
                   if pyo.value(x[(i,j,t)]) > 0:
                        bin_items.append(i)
                        bin_weight += items_wights[i]
            if bin_weight > 0:
                num_bins += 1
                print('Bin of Type :', Type)
                print('  Items packed:', bin_items)
                print('  Total weight:', bin_weight)
                print()
  
print('Number of bins used:', num_bins)








