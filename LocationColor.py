import cv2
import numpy as np
import webcolors
import random
import re
import os.path
import string
import itertools
import math

def detect_closed_shapes(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return
    cv2.namedWindow("window",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("window",1920,1080)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.erode(thresh, kernel, iterations=1)
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out_img = np.zeros(shape=img.shape, dtype=np.uint8)

    locations = list()
    bad = list()
    
    for i in range(0,len(contours)):
        if(cv2.contourArea(contours[i]) > 100):
            locations.append(contours[i])
    
    colors = make_file("output.txt", len(locations))
        
    for i in range(0,len(locations)):
        location = locations[i]
        
        color = webcolors.hex_to_rgb(colors[i])
        color = color[2],color[1],color[0]
        
        cv2.drawContours(out_img, location, -1, color, 5)
        cv2.fillPoly(out_img, pts=[location], color=color)
 
    gray = cv2.cvtColor(out_img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("window",mask)
    cv2.waitKey(0)
    
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.destroyAllWindows()
    print(len(contours))
    count = 0
    for c in contours:
        count += 1
        print(count)
        for b in c:
            flag = False
            for a in b:
                target_col, target_row = a
                pxl = out_img[target_row,target_col]
                black = [0,0,0]
                if(np.all(pxl == black)):
                    distance_type = cv2.DIST_L1
                    mask_size = 5
                    dists, labels = cv2.distanceTransformWithLabels(
                        mask, 
                        distance_type, 
                        mask_size, 
                        labelType=cv2.DIST_LABEL_PIXEL
                    )
                    
                    target_label = labels[target_row, target_col]
                    match_rows, match_cols = np.where(labels == target_label)
                    color = ( int (out_img[match_rows[0],match_cols[0]] [ 0 ]), int (out_img[match_rows[0],match_cols[0]] [ 1 ]), int (out_img[match_rows[0],match_cols[0]] [ 2 ])) 
                    cv2.drawContours(out_img, c, -1, color, 5)
                    cv2.drawContours(out_img, c, -1, color, -1)
                    flag = True
                    break;

            if(flag == True):
                flag = False
                break;
                
    
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)          
                
    cv2.imshow("window",out_img)
    cv2.waitKey(0)
    cv2.imwrite('output_image.png', out_img)
    cv2.destroyAllWindows()
    

def make_file(output_directory, amount):
    with open(output_directory, 'w') as file:
        file.write("")
    outputDict = dict()
    locations = []
    size = math.ceil(math.log(amount)/math.log(26))
    count = 0
    exclude = ["no","or","and","yes","FFFFFF","000000"]
    
    for length in range(0,size+1):
        if(count>amount):
            break
        location = itertools.product(string.ascii_lowercase, repeat=length)
        for item in location:
            if(count>amount):
                break
            if(item in exclude):
                continue
            locations.append("".join(item))
            count = count+1
    locations = locations[1:]
    for location in locations:
        color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        while color in outputDict.values() and color not in exclude:
            color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        outputDict[location] = color
    outstr = str(outputDict)
    outstr = re.sub(r"[\{\}\"'#]","",outstr)
    outstr = re.sub(r"\:"," =",outstr)
    outstr = re.sub(r"\,","\n",outstr)
    outstr = re.sub(r"\n\s","\n",outstr)
    
    with open(output_directory, 'w') as f:
        f.write(outstr)
    return list(outputDict.values())

filename = input("Input file directory:\n")
detect_closed_shapes(filename)
