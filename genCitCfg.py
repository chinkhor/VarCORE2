from RTW import RTW
import pickle

def main(actsOutputFile, systemComponent):
    fp = open("shared.rtw", "rb")
    rtw = pickle.load(fp)
    fp.close()
    rtw.generateCitCfgFiles(actsOutputFile, systemComponent)
    fp = open("shared.rtw", "wb")
    rtw = pickle.dump(rtw,fp)
    fp.close()
    
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Create CIT Configuration Files')
    parser.add_argument('-a', metavar='acts output file', required=True, help='ACTS output file name')
    parser.add_argument('-c', metavar='system component name', required=True, help='System component name')
    args = parser.parse_args()
    main(actsOutputFile=args.a, systemComponent=args.c)
