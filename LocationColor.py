import cv2
import numpy as np
import webcolors
import random
import re
import string
import itertools
import math
from pathlib import Path

def detect_closed_shapes(image_path):
    print("Opening image...")
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("Creating greyscale...")
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    print("Generating Black/White Binary...")
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.erode(thresh, kernel, iterations=1)
    print("Thickening Lnies...")
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    print("Finding Location Contours...")
    out_img = np.zeros(shape=img.shape, dtype=np.uint8)

    locations = list()
    
    print("Eliminating Locations under 100px Area (Usually Artifacts, or result of messy lines)...")
    for i in range(0,len(contours)):
        if(cv2.contourArea(contours[i]) > 100):
            locations.append(contours[i])

    print("Generating 00_default.txt...")
    outputDict = make_file("output/00_default.txt", len(locations))
    colors = list(outputDict.values())
    locationNames = list(outputDict.keys())

    mask = cv2.inRange(img, np.array([255,0,0]), np.array([255,0,0]))
    x, y = np.where(mask == 255)
    oceanCoords = np.ascontiguousarray(np.column_stack((y, x)).astype(np.float32))
    oceans = list()

    mask = cv2.inRange(img, np.array([0,0,255]), np.array([0,0,255]))
    x, y = np.where(mask == 255)
    wastelandCoords = np.ascontiguousarray(np.column_stack((y, x)).astype(np.float32))
    wastelands = list()

    mask = cv2.inRange(img, np.array([0,255,0]), np.array([0,255,0]))
    x, y = np.where(mask == 255)
    harbourCoords = np.ascontiguousarray(np.column_stack((y, x)).astype(np.float32))
    harbours = list()
    

    print("Filling Locations with Color...")
    for i in range(0,len(locations)):
        print("Progress:",str(round((i/len(locations))*100,2)) + "%","/","100%")
        location = locations[i]
        for point in oceanCoords:
            if(cv2.pointPolygonTest(location,point,False) == 1):
                oceans.append(locationNames[i])
                break;
        for point in wastelandCoords:
            if(cv2.pointPolygonTest(location,point,False) == 1):
                wastelands.append(locationNames[i])
                break;
        for point in harbourCoords:
            if(cv2.pointPolygonTest(location,point,False) == 1):
                harbours.append(locationNames[i])
                break;
        
        color = webcolors.hex_to_rgb(colors[i])
        color = color[2],color[1],color[0]
        
        cv2.drawContours(out_img, location, -1, color, 5)
        cv2.fillPoly(out_img, pts=[location], color=color)
    
    print("Generating location_templates.txt...")
    location_templates(locationNames, oceans, harbours, wastelands)
    print("Generating  08_institutions.txt...")
    institutions(locationNames, oceans, wastelands)
    print("Generating 06_pops.txt...")
    pops(locationNames, oceans, wastelands)
    print("Generating definitions.txt...")
    definitions(locationNames, oceans, wastelands)
    print("Generating default.map...")
    default(oceans, wastelands)

    print("Converting Output to Greyscale...")
    gray = cv2.cvtColor(out_img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)
    print("Generating Inverted Black/White Binary...")
    #cv2.imshow("window",mask)
    #cv2.waitKey(0)
    
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    print("Finding Contours of Locations Below 100px Area...")
    #cv2.destroyAllWindows()

    print("Filling Empty Pixels with Nearby Location Colors...")
    count = 0
    for c in contours:
        count += 1
        print("Progress:",str(round((count/len(contours))*100,2)) + "%","/","100%")
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

    

    print("Complete, Exporting Image to locations.png")       
    #cv2.imshow("window",out_img)
    #cv2.waitKey(0)
    cv2.imwrite('output/locations.png', out_img)
    cv2.destroyAllWindows()
    

def make_file(output_directory, amount):
    existing = input("Enter the directory to your current 00_default.txt file, to exclude already existing names and colors\n(Leave blank if it does not exist):\n")
    existingDict = dict()
    if(existing != ""):
        with open(existing, 'r') as file:
            for line in file:
                info = re.sub(r"[\s]","",line).split("=")
                existingDict[info[0]] = info[1]
            
    Path("output").mkdir(parents=True, exist_ok=True)
    with open(output_directory, 'w') as file:
        file.write("")
    outputDict = dict()
    locations = []
    size = math.ceil(math.log(amount)/math.log(26))
    count = 0 
    exclude = ["no","or","nor","nand","not","and","yes","FFFFFF","000000"]
    
    print("Generating Location Names...") 
    for length in range(0,size+1):
        print("Progress:",str(round((count/amount)*100,2)) + "%","/","100%")
        if(count>amount):
            break
        location = itertools.product(string.ascii_lowercase, repeat=length)
        for item in location:
            if(count>amount):
                break
            if("".join(item) not in exclude and "".join(item) not in list(existingDict.keys())):
                locations.append("".join(item))
                count = count+1
    locations = locations[1:]
    count = 0

    for location in locations:
        print("Progress:",str(round((count/amount)*100,2)) + "%","/","100%")
        color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        while color in list(outputDict.values()) and color not in exclude and color not in list(existingDict.values()):
            color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        outputDict[location] = color
        count = count+1
    outstr = str(outputDict)
    outstr = re.sub(r"[\{\}\"'#]","",outstr)
    outstr = re.sub(r"\:"," =",outstr)
    outstr = re.sub(r"\,","\n",outstr)
    outstr = re.sub(r"\n\s","\n",outstr)
    
    with open("output/"+output_directory, 'w') as f:
        f.write(outstr)
    return outputDict

def location_templates(locations, oceans, harbours, wastelands):
    with open("output/location_templates.txt", 'w') as file:
        for location in locations:
            if(location in oceans):
                file.write(location + " = { topography = narrows climate = subtropical}\n")
            elif(location in wastelands):
                file.write(location + " = { topography = flatland_wasteland vegetation = woods climate = arctic}\n")
            elif(location in harbours):
                file.write(location + "  = { topography = wetlands vegetation = grasslands climate = subtropical religion = catholic culture = danube_bavarian raw_material = wheat natural_harbor_suitability=1.00}\n")
            else:
                file.write(location + "  = { topography = wetlands vegetation = grasslands climate = subtropical religion = catholic culture = danube_bavarian raw_material = wheat}\n")

def institutions(locations, oceans, wastelands):
    with open("output/08_institutions.txt", 'w') as file:
        file.write("locations={\n")
        for location in locations:
            if(location not in oceans and location not in wastelands):
                file.write(location + " = { feudalism = yes legalism = yes }\n")
        file.write("}")

def pops(locations, oceans, wastelands):
    with open("output/06_pops.txt", 'w') as file:
        file.write("locations={\n")
        for location in locations:
            if(location not in oceans and location not in wastelands):
                file.write(location + " = {   define_pop = { type = nobles size = 0.012 culture = danube_bavarian religion = catholic }   define_pop = { type = clergy size = 0.057 culture = danube_bavarian religion = catholic }   define_pop = { type = burghers size = 1.776 culture = danube_bavarian religion = catholic }   define_pop = { type = peasants size = 35.598 culture = danube_bavarian religion = catholic }  }\n")
        file.write("}")

def definitions(locations, oceans, wastelands):
    with open("output/definitions.txt", 'w') as file:
        file.write("custom_continent = {\n    custom_subcontintent = {\n        custom_region = {\n            my_land_area = {\n                my_land_province = {\n")
        for location in locations:
            if(location not in oceans and location not in wastelands):
                file.write("                    " + location + "\n")
        file.write("                }\n            }\n            my_sea_area = {\n                my_sea_province = {\n")
        for ocean in oceans:
            file.write("                    " + ocean + "\n")
        file.write("            }\n            }\n")
        file.write("            wasteland_area = {\n                wasteland_province = {\n")
        for wasteland in wastelands:
            file.write("                    " + wasteland + "\n")
        file.write("                }\n            }\n\n            dummy1_area = {\n")
        file.write("            }\n            dummy2_area = {\n            }\n            dummy3_area = {\n            }\n")
        file.write("            dummy4_area = {\n            }\n            dummy5_area = {\n            }\n            dummy6_area = {\n            }\n\n        }\n    }\n}")

def default(oceans, wastelands):
    with open("output/default.map", 'w') as file:
        file.write("provinces = \"locations.png\"\n")
        file.write("rivers = \"rivers.png\"\n")
        file.write("topology = \"heightmap.heightmap\"\n")
        file.write("adjacencies = \"adjacencies.csv\"\n")
        file.write("setup = \"definitions.txt\"\n")
        file.write("ports = \"ports.csv\"\n")
        file.write("location_templates = \"location_templates.txt\"\n")
        file.write("\n")
        file.write("equator_y = 3340\n")
        file.write("wrap_x = yes\n")
        file.write("\n")
        file.write("#############\n")
        file.write("# VOLCANOES\n")
        file.write("#############\n")
        file.write("volcanoes = {\n")
        file.write("}\n")
        file.write("\n")
        file.write("###################################\n")
        file.write("# All possible earthquake zones\n")
        file.write("###################################\n")
        file.write("earthquakes = {\n")
        file.write("}\n")
        file.write("\n")
        file.write("#############\n")
        file.write("# SEA ZONES\n")
        file.write("#############\n")
        file.write("# European Seas\n")
        file.write("sea_zones = {\n")
        for ocean in oceans:
            file.write("    " + ocean + "\n")
        file.write("}\n")
        file.write("\n")
        file.write("###############\n")
        file.write("# MAJOR RIVERS\n")
        file.write("###############\n")
        file.write("#river_provinces = { 628 630 } #Thames\n")
        file.write("\n")
        file.write("########\n")
        file.write("# LAKES\n")
        file.write("########\n")
        file.write("lakes = {\n")
        file.write("}\n")
        file.write("\n")
        file.write("#####################\n")
        file.write("# IMPASSABLE TERRAIN\n")
        file.write("#####################\n")
        file.write("# Can be colored by whoever owns the most of the province's neighbors.\n")
        file.write("# Blocks unit movement.\n")
        file.write("\n")
        file.write("impassable_mountains = {\n")
        for wasteland in wastelands:
            file.write("    " + wasteland + "\n")
        file.write("}\n")
        file.write("\n")
        file.write("non_ownable = {\n")
        file.write("}\n")

filename = input("Input PNG File Path:\n")
detect_closed_shapes(filename)
