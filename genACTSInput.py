from RTW import RTW
import pickle

def main(actsInputFile):
    fp = open("shared.rtw", "rb")
    rtw = pickle.load(fp)
    fp.close()
    rtw.generateACTSInputFile(actsInputFile)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Create ACTS Input File')
    parser.add_argument('-a', metavar='acts_input_file', required=True, help='ACTS input file name')
    args = parser.parse_args()
    main(actsInputFile=args.a)