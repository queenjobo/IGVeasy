'''
@queenjobo July 2017

Script that looks at IGV plots in a given file with a specific image type (jpg/png) and takes user input 
to create new file with filename and user given comment y/n/m (yes/no/maybe)

SCRIPT USAGE:

python IGVviewer.py --dir /lustre/scratch115/projects/ddd/users/jk18/mutatpheno/DNG/IGV/missed_exome/ --filenameinfo

'''
USAGE_STRING = "USAGE: \n To annotate plot type: y/n/m \n To go forwards or back a plot type: f/b \n To exit program before end of files type: q"
#-----------------------IMPORTS------------------------

import argparse
import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

#---------------------FUNCTIONS-----------------------

def get_options():
    '''parse options'''
    parser = argparse.ArgumentParser(description = USAGE_STRING)
    parser.add_argument('--dir',type = str,help = 'directory for IGV images',required = True)
    parser.add_argument('--ext', type = str, help = "file extension, default is .png", required = False, default = ".png")
    parser.add_argument('--filenameinfo', action = 'store_true', default = False, help = "bool whether the filename info can be parsed for more info eg in format DDDP103048s118__chr6_27416026_27416126.png", required = False)
    args = parser.parse_args()
    return(args)

def get_files(path,ext):
    '''get files given path and extension'''
    myfiles = [path + each for each in os.listdir(path) if each.endswith(ext)]
    return(myfiles)

def move_position(ann,i):
    '''if user wants to move forward or back'''
    if ann == "b":
        if i-1 < 0:
            print("cant go back! staying here!")
        else:
            i = i-1
            print("moving back!")
    elif ann == "f":
        i = i+1
        print("moving forward!")
    return(i)

def annotate(ann,i,annlist):
    '''annotate with approp annotation'''
    annlist[i] = ann[0]
    i += 1
    return(i,annlist)

def parse_filename(filename):
    ''' extract info from filename if in format DDDP103048s118__chr6_27416026_27416126.png
    returns string id\tchr\tpos'''
    fields = filename.split("/")[-1].split(".")[0].split("_")
    id = fields[0]
    chrm = fields[2][3:]
    mut = (int(fields[4])-int(fields[3]))/2 + int(fields[3])
    info = "\t".join([id,chrm,str(int(mut))])
    return(info)
    
def exit_program(igvfiles,annlist,filenameinfo):
    '''exit program and save annotations'''
    tosave = input("Save annotations? y or n: ")
    while tosave not in ("y","n"):
        tosave = input("Save annotations? please type y or n: ")
    if tosave == "y":
        filename = input("Filename to save annotations: ")
        mylines = []
        with open(filename,'w') as f:
            for ann,igvfile in zip(annlist,igvfiles):
                if ann is None:
                    continue
                if filenameinfo:
                    info = parse_filename(igvfile)
                    mylines.append("\t".join([igvfile,ann,info]))
                else:
                    mylines.append("\t".join([igvfile,ann]))
            f.write("\n".join(mylines))
        print("Written to file.")
    else:
        print("Not saving.")  

def assess_plots(igvfiles,filenameinfo):
    '''goes through list of igvfiles and displays image and saves user annotation'''
    tot = len(igvfiles)
    annlist = [None] * tot
    i = 0
    while i < tot:
        viewer = subprocess.Popen(['feh','--scale-down','--auto-zoom',igvfiles[i]])
        ann = input("Does this look real? ")
        viewer.terminate()
        viewer.kill()
        #save annotation
        if ann in ("yes","y","no","n","maybe","m"):
            i,annlist = annotate(ann,i,annlist)
        #move forwards or backwards
        elif ann in ("b","f"):
            i = move_position(ann,i)
        #exit program
        elif ann == "q":
            break
        #handle wrong user input, stay on same image
        else:
            print("I dont understand...\n" + USAGE_STRING)
    exit_program(igvfiles,annlist,filenameinfo)
            

def main():
    print(USAGE_STRING)
    args = get_options()
    igvfiles = get_files(args.dir,args.ext)
    assess_plots(igvfiles,args.filenameinfo)

#------------------SCRIPT-------------------------------

if __name__ == "__main__":
    main()