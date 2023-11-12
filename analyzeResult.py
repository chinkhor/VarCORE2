from RTW import RTW
import pickle

def main(resultFile):
    fp = open("shared.rtw", "rb")
    rtw = pickle.load(fp)
    fp.close()
    rtw.analyzeTestResult(resultFile)
    
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Analyze Build Test Result')
    parser.add_argument('-r', metavar='result_file', required=True, help='Build Test result')
    args = parser.parse_args()
    main(resultFile=args.r)
