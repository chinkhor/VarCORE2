from RTW import RTW
import pickle

def main(rtwFile, mapFile=None):
    rtw = RTW(rtwFile, mapFile)
    fp = open("shared.rtw","wb")
    pickle.dump(rtw, fp)
    fp.close()
    
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Create Feature Model from RTW')
    parser.add_argument('-i', metavar='RTW input file', required=True, help='RTW input file name')
    parser.add_argument('-m', metavar='feature map file', help='Feature to code mapping file')
    args = parser.parse_args()
    main(rtwFile=args.i, mapFile=args.m)
