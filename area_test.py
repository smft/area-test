# -*- coding: utf-8 -*-

"""
calculate field similarity
@author: qzhang
"""

"""
data is an array that contains : lat (Column 0),lon (Column1)
forecast quantity precipitation (Column2),observation quantity
precipitaiton (Column3),forecast precipitaion level(Column4),
observation precipitation level(Column5)
"""

import numpy as np
import scipy.cluster as cluster
import scipy.stats as stats
from profilehooks import profile

"""judge preciptation level"""
@profile
def precip_level(data):
	record=np.shape(data)
	data_output=np.empty([record[0],record[1]+2])
	count=0
	for cell in data:
		if cell[2]==0:
			data_output[count,4]=0
		if cell[2]<=10 and cell[2]>0:
			data_output[count,4]=1
		if cell[2]<=25 and cell[2]>10:
			data_output[count,4]=2
		if cell[2]<=50 and cell[2]>25:
			data_output[count,4]=3
		if cell[2]>50:
			data_output[count,4]=4
		if cell[3]==0:
			data_output[count,5]=0
		if cell[3]<=10 and cell[3]>0:
			data_output[count,5]=1
		if cell[3]<=25 and cell[3]>10:
			data_output[count,5]=2
		if cell[3]<=50 and cell[3]>25:
			data_output[count,5]=3
		if cell[3]>50:
			data_output[count,5]=4
		count+=1
	data_output[:,0]=data[:,0]
	data_output[:,1]=data[:,1]
	data_output[:,2]=data[:,2]
	data_output[:,3]=data[:,3]
	return data_output
			
"""calculate field similarity variables"""
@profile
def field_sim(data,precip_level):
	rslt={}
	#calculate corrcoef 
	corrcoef_matrix=np.corrcoef(data[:,2],data[:,3])
	rslt["corrcoef"]=corrcoef_matrix[0,1]
	#calculate area overlap ratio
	count_fore=0
	count_obs=0
	count_bingo=0
	for cell in data[:,:]:
		if cell[4]==precip_level:
			count_fore+=1
		if cell[5]==precip_level:
			count_obs+=1
		if (cell[5]==precip_level)and(cell[4]==precip_level):
			count_bingo+=1
	rslt["area_overlap_ratio"]=count_bingo/float(count_obs)
	#center location error &&  strength error
	loc_fore=np.zeros([count_fore,3])
	loc_obs=np.zeros([count_obs,3])
	count_fore=0
	count_obs=0
	for cell in data[:,:]:
		if cell[4]==precip_level:
			loc_fore[count_fore,0]=cell[0]
			loc_fore[count_fore,1]=cell[1]
			loc_fore[count_fore,2]=cell[2]
			count_fore+=1
		if cell[5]==precip_level:
			loc_obs[count_obs,0]=cell[0]
			loc_obs[count_obs,1]=cell[1]
			loc_obs[count_obs,2]=cell[3]
			count_obs+=1
	centroid_fore,label_fore=cluster.vq.kmeans2(loc_fore,1,iter=20,thresh=1e-05,\
																minit='points',missing='warn')
	centroid_obs,label_obs=cluster.vq.kmeans2(loc_obs,1,iter=20,thresh=1e-05,\
																minit='points',missing='warn')
	centroid_err=centroid_fore-centroid_obs
	rslt["center_location_error"]=np.sqrt(centroid_err[0,0]**2+centroid_err[0,1]**2)
	rslt["strength_error"]=np.abs(centroid_err[0,2])
	return rslt

"""
self test case
"""
import string
# read data
aws_file_name="/media/qzhang/UUI/20110718/11071812.AWS"
aws_flag=open(aws_file_name,"r")
data_raw=aws_flag.read().split("\n")
file_record=data_raw[1].split(" ")
data_main_str=[]
data_main_str=[cell.split(" ") for cell in data_raw[2:]][:-1]
data_main=np.empty([int(string.atof(file_record[-1])),4])
count=0
for cell in data_main_str:
	data_main[count,0]=string.atof(cell[1])
	data_main[count,1]=string.atof(cell[2])
	if string.atof(cell[12])!=9999:
		data_main[count,2]=string.atof(cell[12])
	else:
		data_main[count,2]=0
	if string.atof(cell[12])!=9999:
		data_main[count,3]=string.atof(cell[12])
	else:
		data_main[count,3]=0
	count+=1
aws_flag.close()
#calculate
input_data=precip_level(data_main)
print field_sim(input_data,1)
