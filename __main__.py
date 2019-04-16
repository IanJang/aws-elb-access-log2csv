from utils import aws_elb_access_log2csv

if __name__ == "__main__":
    aws_elb_access_log2csv("sample/elb.log", "sample/result.csv")
