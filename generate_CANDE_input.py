# -*- coding: utf-8 -*-
"""
Created on Thu May 23 17:39:24 2019

@author: arock
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np


fileName = 'Ellipses.csv' #input file for the culvert where the mesh details are input into the excel template

def getCross(seg1,seg2):  #get the cross product of the triangular element to orient it according to right hand system
    cross = np.cross(seg1,seg2)
    return cross

def getFoundation(x,y,slope,b,xmax,xmin,ymax,ymin):  # determine if the element is part of the concrete foundation (if applicable)
    #accomodoates a sloped foundation
    if x <= xmax and x>= xmin and y<ymax and y>ymin:
        ycheck = slope*x + b
        if y <= ycheck:
            return 2
        else: return 1
    else: return 1
    
def getFoundation2(x,y,xmax,xmin,ymax,ymin):  #same as above, but if the foundation is only rectangular rather than sloped
    if x <= xmax and x>= xmin and y<ymax and y>ymin:
        return 2
    else: return 1

def getCentroid(N1, N2, N3): #get the centroid of the triangular element for use in assigning material type
    """return the centroid of the (triangular) element given the nodes"""
    # nodes are one indexed but the data frame is zero indexed
    N1 = N1-1
    N2 = N2-1
    N3 = N3-1
    # get x and y coords
    N1x = geom.loc[N1,'NX']
    N1y = geom.loc[N1,'NY']
    
    N2x = geom.loc[N2,'NX']
    N2y = geom.loc[N2,'NY']
    
    N3x = geom.loc[N3,'NX']
    N3y = geom.loc[N3,'NY']
    
    x = (N1x+N2x+N3x)/3.0
    y = (N1y+N2y+N3y)/3.0
    return x,y

def getCentroid_Quad(N1, N2, N3, N4): #get the centroid of the quad element for use in assigning material type
    """return the centroid of the (quad) element given the nodes"""
    # nodes are one indexed but the data frame is zero indexed
    N1 = N1-1
    N2 = N2-1
    N3 = N3-1
    N4 = N4-1
    # get x and y coords
    N1x = geom.loc[N1,'NX']
    N1y = geom.loc[N1,'NY']
    
    N2x = geom.loc[N2,'NX']
    N2y = geom.loc[N2,'NY']
    
    N3x = geom.loc[N3,'NX']
    N3y = geom.loc[N3,'NY']
    
    N4x = geom.loc[N3,'NX']
    N4y = geom.loc[N3,'NY']    
    
    x = (N1x+N2x+N3x+N4x)/4.0
    y = (N1y+N2y+N3y+N4y)/4.0
    return x,y

INTF_flag=False #if using interface elements, do not use yet because the interface elements are very tricky to define

geom = pd.read_csv(fileName, engine='python')
Nodes = int(geom.loc[0,'Control'])
Elements = int(geom.loc[1,'Control'])
Interfaces = int(geom.loc[3,'Control'])
Boundaries = int(geom.loc[5,'Control'])
INTF_friction = (geom.loc[8,'Control'])
INTF_tension = int(geom.loc[9,'Control'])

# create the file structure
data = ET.Element('CANDEMeshGeom')
Control = ET.SubElement(data, 'Control')
nodeData = ET.SubElement(data, 'nodeData')
elementData = ET.SubElement(data, 'elementData')
boundaryData = ET.SubElement(data, 'boundaryData')
soilData = ET.SubElement(data, 'soilData')
if INTF_flag==True:
    interfaceData = ET.SubElement(data, 'interfaceData')


# create control subelement
numNodes = ET.SubElement(Control, 'numNodes')
numNodes.text = str(int(geom.loc[0,'Control']))
numElements = ET.SubElement(Control, 'numElements')
numElements.text = str(int(geom.loc[1,'Control']))
numSoilMaterials = ET.SubElement(Control, 'numSoilMaterials')
numSoilMaterials.text = str(int(geom.loc[2,'Control']))
if INTF_flag == True:
    numInterfaceMaterials = ET.SubElement(Control, 'numInterfaceMaterials')
    numInterfaceMaterials.text = str(int(geom.loc[3,'Control']))
else:
    numInterfaceMaterials = ET.SubElement(Control, 'numInterfaceMaterials')
    numInterfaceMaterials.text = str(int(0))
inputCheck = ET.SubElement(Control, 'inputCheck')
inputCheck.text = str(int(geom.loc[4,'Control']))
numBoundCond = ET.SubElement(Control, 'numBoundCond')
numBoundCond.text = str(int(geom.loc[5,'Control']))
numConstIncr = ET.SubElement(Control, 'numConstIncr')
numConstIncr.text = str(int(geom.loc[6,'Control']))
LevelNum = ET.SubElement(Control, 'LevelNum')
LevelNum.text = str(int(geom.loc[7,'Control']))
#Heading = ET.SubElement(Control, 'Heading')
meshTitle = ET.SubElement(Control, 'meshTitle')
meshTitle.text = 'Mesh from GMSH'


#put in node data
for i in range(Nodes):
    nodeCoord = ET.SubElement(nodeData,'nodeCoord')
    nodeNumber = ET.SubElement(nodeCoord,'nodeNumber')
    nodeNumber.text = str(i+1)
    nodeXCoord = ET.SubElement(nodeCoord,'nodeXCoord')
    nodeXCoord.text = str(geom.loc[i,'NX'])
    nodeYCoord = ET.SubElement(nodeCoord,'nodeYCoord')
    nodeYCoord.text = str(geom.loc[i,'NY'])
    
# put in element data
count = 1
for i in range(Elements):
    elemConn = ET.SubElement(elementData,'elemConn')
    elemNumber = ET.SubElement(elemConn,'elemNumber')
    elemNumber.text = str(i+1)
    elemNode1 = ET.SubElement(elemConn,'elemNode1')
    
    elemNode2 = ET.SubElement(elemConn,'elemNode2')
    
    elemNode3 = ET.SubElement(elemConn,'elemNode3')
    elemNode4 = ET.SubElement(elemConn,'elemNode4')
    elemMatNum = ET.SubElement(elemConn,'elemMatNum')
    elemConstrIncr = ET.SubElement(elemConn,'elemConstrIncr')
    elemType = ET.SubElement(elemConn,'elemType')
    type1 = str(geom.loc[i,'Type'])
    elemType.text = type1
    
    
    if type1 == 'BEAM':
        elemNode1.text = str(int(geom.loc[i,'N1']))
        elemNode2.text = str(int(geom.loc[i,'N2']))
        elemNode3.text = str(int(geom.loc[i,'N2']))
        elemNode4.text = str(int(geom.loc[i,'N2']))
        elemMatNum.text = '1'
        elemConstrIncr.text = '1'
        
    if type1 == "TRIA":
        p = [geom.loc[i,'Seg1x'],geom.loc[i,'Seg1y'],0]
        q = [geom.loc[i,'Seg2x'],geom.loc[i,'Seg2y'],0]
        cross = getCross(p,q)
        if(cross[2]>0):
            elemNode1.text = str(int(geom.loc[i,'N1']))
            elemNode2.text = str(int(geom.loc[i,'N2']))
            elemNode3.text = str(int(geom.loc[i,'N3']))
            elemNode4.text = str(int(geom.loc[i,'N3']))
        else:
            elemNode1.text = str(int(geom.loc[i,'N3']))
            elemNode2.text = str(int(geom.loc[i,'N2']))
            elemNode3.text = str(int(geom.loc[i,'N1']))
            elemNode4.text = str(int(geom.loc[i,'N1'])) 
        
#        x,y = getCentroid(int(geom.loc[i,'N1']),int(geom.loc[i,'N2']),int(geom.loc[i,'N3']))
#        rad_dist = np.sqrt(x*x+y*y)
#        if rad_dist < 206:
#            matNum = 2
#        else:
#            matNum = 1
        matNum = 1
        elemMatNum.text = str(matNum)
        elemConstrIncr.text = '1'
            
    if type1 == "QUAD":
        p = [geom.loc[i,'Seg1x'],geom.loc[i,'Seg1y'],0]
        q = [geom.loc[i,'Seg2x'],geom.loc[i,'Seg2y'],0]
        r = [geom.loc[i,'Seg3x'],geom.loc[i,'Seg3y'],0]
        cross = getCross(p,r)  #lets start by assuming they either do clockwise or ctcw instead of employing the general solution
        if(cross[2]>0):
            elemNode1.text = str(int(geom.loc[i,'N1']))
            elemNode2.text = str(int(geom.loc[i,'N2']))
            elemNode3.text = str(int(geom.loc[i,'N3']))
            elemNode4.text = str(int(geom.loc[i,'N4']))
        else:
            elemNode1.text = str(int(geom.loc[i,'N4']))
            elemNode2.text = str(int(geom.loc[i,'N3']))
            elemNode3.text = str(int(geom.loc[i,'N2']))
            elemNode4.text = str(int(geom.loc[i,'N1']))  

        matNum=1
        elemMatNum.text = str(matNum)
        elemConstrIncr.text = '1'
        
    if type1 == "INTF":
        elemNode1.text = str(int(geom.loc[i,'N2']))
        elemNode2.text = str(int(geom.loc[i,'N1']))
        elemNode3.text = str(int(geom.loc[i,'N2']-1))
        elemNode4.text = str(int(geom.loc[i,'N2']-1))
        elemMatNum.text = str(int(count))
        elemConstrIncr.text = '1'
        count = count + 1
        
#put in boundary data  
for i in range(Boundaries):
    boundary = ET.SubElement(boundaryData, 'boundary')
    boundNumber = ET.SubElement(boundary, 'boundNumber')
    boundNode = ET.SubElement(boundary, 'boundNode')
    boundConstrIncr = ET.SubElement(boundary, 'boundConstrIncr')
    boundXCode = ET.SubElement(boundary, 'boundXCode')
    boundYCode = ET.SubElement(boundary, 'boundYCode')
    boundXForce = ET.SubElement(boundary, 'boundXForce')
    boundYForce = ET.SubElement(boundary, 'boundYForce')
    boundRotAngle = ET.SubElement(boundary, 'boundRotAngle')
    
    boundNumber.text = str(i+1)
    boundNode.text = str(int(geom.loc[i,'BN']))
    boundConstrIncr.text = '1'
    boundXCode.text = str(int(geom.loc[i,'BXC']))
    boundYCode.text = str(int(geom.loc[i,'BYC']))
    boundXForce.text = str(geom.loc[i,'BXF'])
    boundYForce.text = str(geom.loc[i,'BYF'])
    boundRotAngle.text = '0.0'
    
# put in soil data 
soil = ET.SubElement(soilData,'soil')
matID = ET.SubElement(soil,'matID')
matID.text = "1"
iTYP = ET.SubElement(soil, 'iTYP')
iTYP.text = "1"
density = ET.SubElement(soil,'density')
density.text = "0.0694"
matName = ET.SubElement(soil,'matName')
matName.text = "Soil # 1"

#put in soil # 2 in case we want to add foundation
soil = ET.SubElement(soilData,'soil')
matID = ET.SubElement(soil,'matID')
matID.text = "2"
iTYP = ET.SubElement(soil, 'iTYP')
iTYP.text = "1"
density = ET.SubElement(soil,'density')
density.text = "0.0694"
matName = ET.SubElement(soil,'matName')
matName.text = "Soil # 2"

#put in interface material data
if INTF_flag == True:
    for i in range(Interfaces):
        interface = ET.SubElement(interfaceData, 'interface')
        matID = ET.SubElement(interface,'matID')
        matName = ET.SubElement(interface,'matName')
        angle = ET.SubElement(interface,'angle')
        coeffFriction = ET.SubElement(interface,'coeffFriction')
        tensileForce = ET.SubElement(interface,'tensileForce')
        matID.text = str(i+1)
        matName.text = 'Inter # ' + str(i+1)
        angle.text = str(geom.loc[i,'Interface'])
        coeffFriction.text = str(INTF_friction)
        tensileForce.text = str(INTF_tension)
    



myFile = open('Ellipses2_MeshGeom.xml', 'w') #this is the proper file name nomenclature, otherwise CANDE will not read

et = ET.ElementTree(data)

et.write(myFile,encoding="UTF-8",xml_declaration=True) #this ensures CANDE can read the text encoding


myFile.close()

