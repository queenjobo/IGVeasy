
'''
@queenjobo
29/06/2017

When given a tab delimited file that has the following columnns: ID, BAMFILE , CHR, POS
sorted wrt to ID then creates IGV plots for each given variant with a default window size of 50bp
outputs pngs into current directory

EXAMPLE:
cd directory_for_plots
bsub -R"select[mem>1500] rusage[mem=1500]" -M1500 -o igvit.out 'python /nfs/users/nfs_j/jk18/PhD/IGVplotter/IGVplotter.py --tabfile /lustre/scratch115/projects/ddd/users/jk18/mutatpheno/DNG/exome_dnms_remaining_IGV.tab --window 20 --header no --iscram no --makebam no'
python /nfs/users/nfs_j/jk18/PhD/IGVplotter/IGVplotter.py --tabfile /lustre/scratch115/projects/ddd/users/jk18/mutatpheno/DNG/exome_dnms_remaining_IGV_bams.tab --window 50 --header no --iscram no --makebam no

'''
#--------------------------IMPORT PACKAGES-----------------------------------------------
import os
import sys
import argparse
from subprocess import call

#---------------------STABLE-PATHS-------------------------------------------------------

REF_FILE = '/nfs/users/nfs_j/jk18/igv/genomes/hs37d5.genome'
IGV_PATH = '/software/hgi/pkglocal/IGV-2.3.90/bin/lib/igv.jar' 

#---------------------FUNCTIONS----------------------------------------------------------
def get_options():
    '''parse input options'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--tabfile',type = str,help = 'file with info',required = True)
    parser.add_argument('--window',type = int, help = 'window to look around',required = False,default = 50)
    parser.add_argument('--header',type = bool,help = 'does tabfile have header',required = False, default = False)
    parser.add_argument('--iscram',type = bool, help = "if cram files?",required = False, default = False)
    parser.add_argument('--makebam',type = bool, help = "make bams if crams",required = False, default = False)
    args = parser.parse_args()
    return(args.tabfile,args.window,args.header,args.iscram,args.makebam)

def make_bams(tabfile,interval,header):
    '''make bam files if crams '''
    print("is cram, making bams!")
    d = get_bam_positions(tabfile,interval,header)
    for i,cramfile in enumerate(d.keys()):
        bamfile = cramfile.strip(".cram") + "_forIGV"
        extc = "samtools view -b " + cramfile + " " + d[cramfile] + " > "+ bamfile + ".bam"
        call(extc,shell = True) 
        sortc = "samtools sort " + bamfile  + ".bam -o " + bamfile + "_sorted.bam"
        call(sortc,shell = True)
        indexc = "samtools index " + bamfile + "_sorted.bam"
        call(indexc,shell = True)
    print("made " + str(i) + "bams!")
        
def get_bam_positions(tabfile,interval,header):
    '''create dictionary of cram file and positions to feed to make bams '''
    d = {}
    with open(tabfile,'r') as f:
        if header:
            h = f.readline()
        for line in f:
            fields = line.strip("\n").split("\t")
            cramfiles = fields[1].split(",")
            chrm = fields[2]
            pos = int(fields[3])
            for cramfile in cramfiles:
                if cramfile in d:
                    d[cramfile] = d[cramfile] + chrm + ":" + str(pos-1000) + "-" + str(pos+interval+1000) + " "
                else:
                    d[cramfile] = chrm + ":" + str(pos-interval-1000) + "-" + str(pos+interval+1000) + " "
    return(d)
            

def get_IGV_plots(tabfile,interval,header,iscram):
    '''go through tab file and get IGV plots'''
    print("getting IGV plots!")
    pid = ""
    dnms = ""
    with open(tabfile,'r') as f:
        if header:
            h = f.readline()
        for line in f:
            fields = line.strip("\n").split("\t")
            cid = fields[0]
            if pid != cid and pid != "":
                print("submitting "+ pid)
                submit_IGV(pid,bamfile,dnms)
                dnms = ""
                pid = cid
            if pid == "":
                pid = cid
            bamfile = " ".join(fields[1].split(",")) 
            if iscram:
                bamfile = ""
                for file in fields[1].split(","):
                    bamfile = bamfile + " " + file.strip(".cram") + "_forIGV_sorted.bam"
            chrm = fields[2]
            pos = int(fields[3])
            dnms = dnms + "chr" + chrm + ":" + str(pos-interval) + "-" + str(pos+interval) + " "
        print("submitting "+ cid)
        submit_IGV(cid,bamfile,dnms)
    print("done!")
            
def submit_IGV(pid,bamfile,dnms):
    '''submit IGV'''
    myc='bsub -R"select[mem>1500] rusage[mem=1500]" -M1500 -o '+pid+".out 'igv_plotter --width 2000 --height 2000 -g "+ REF_FILE + ' --igv-jar-path ' + IGV_PATH + " -o "
    #print(myc+pid+" "+bamfile+" "+dnms)
    os.system(myc+pid+" " + bamfile + " " + dnms + "'")

def main():
    tabfile,window,header,iscram,makebam = get_options()
    print(tabfile,window,header,iscram,makebam)
    if iscram and makebam:
        make_bams(tabfile,window,header)
    elif iscram and not makebam:
        print("is cram but bam files already made")
    else:
        print("input is bam files!")
    get_IGV_plots(tabfile,window,header,iscram)
    

#-----------------------------SCRIPT------------------------------------------------------
if __name__=='__main__':
    main()