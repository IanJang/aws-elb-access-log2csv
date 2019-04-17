import csv
import os
import unittest
import pandas as pd
from utils import aws_elb_access_log2csv, AwsElbAccessLog


class Test(unittest.TestCase):
    def setUp(self):
        # reference:
        # https://docs.aws.amazon.com/ko_kr/elasticloadbalancing/latest/application/load-balancer-access-logs.html#access-log-entry-examples
        self.elb_log_lines = [
            # HTTP example
            ('http 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817'
             ' 10.0.0.1:80 0.000 0.001 0.000 200 200 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0"'
             ' - - arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'
             ' "Root=1-58337262-36d228ad5d99923122bbe354" "-" "-" 0 2018-07-02T22:22:48.364000Z "forward" "-" "-"'),
            # HTTPS example
            ('https 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 10.0.0.1:80'
             ' 0.086 0.048 0.037 200 200 0 57 "GET https://www.example.com:443/ HTTP/1.1" "curl/7.46.0"'
             ' ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/'
             'my-targets/73e2d6bc24d8a067 "Root=1-58337281-1d84f3d73c47ec4e58577259" "www.example.com"'
             ' "arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012"'
             ' 1 2018-07-02T22:22:48.364000Z "authenticate,forward" "-" "-"'),
            # HTTP/2 example
            ('h2 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 10.0.1.252:48160 10.0.0.66:9000'
             ' 0.000 0.002 0.000 200 200 5 257 "GET https://10.0.2.105:773/ HTTP/2.0" "curl/7.46.0"'
             ' ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/'
             'my-targets/73e2d6bc24d8a067 "Root=1-58337327-72bd00b0343d75b906739c42" "-" "-" 1 2018-07-02T22:22:48.'
             '364000Z "redirect" "https://example.com:80/" "-"'),
            # WebSockets example
            ('ws 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 10.0.0.140:40914 10.0.1.192:8010'
             ' 0.001 0.003 0.000 101 101 218 587 "GET http://10.0.0.30:80/ HTTP/1.1" "-" - - arn:aws:elasticloadbalan'
             'cing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965'
             'a2ef7629b185e3" "-" "-" 1 2018-07-02T22:22:48.364000Z "forward" "-" "-"'),
            # Security WebSockets example
            ('wss 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 10.0.0.140:44244 10.0.0.171:8010'
             ' 0.000 0.001 0.000 101 101 218 786 "GET https://10.0.0.30:443/ HTTP/1.1" "-" ECDHE-RSA-AES128-GCM-SHA256'
             ' TLSv1.2 arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'
             ' "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 1 2018-07-02T22:22:48.364000Z "forward" "-" "-"'),
            # Lambda function success example
            ('http 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001'
             ' 0.000 200 200 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:elasticloadb'
             'alancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337364-23a8c76965a2ef'
             '7629b185e3" "-" "-" 0 2018-11-30T22:22:48.364000Z "forward" "-" "-"'),
            # Lambda function fail example
            ('http 2018-11-30T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817 - 0.000 0.001'
             ' 0.000 502 - 34 366 "GET http://www.example.com:80/ HTTP/1.1" "curl/7.46.0" - - arn:aws:'
             'elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067'
             ' "Root=1-58337364-23a8c76965a2ef7629b185e3" "-" "-" 0 2018-11-30T22:22:48.364000Z "forward" "-"'
             ' "LambdaInvalidResponse"')
        ]
        self.elb_log_file_path = "sample/test_elb_log.log"
        self.output_csv_file_path = "sample/test_result.csv"
        try:
            os.remove(self.elb_log_file_path)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.output_csv_file_path)
        except FileNotFoundError:
            pass

    def tearDown(self):
        try:
            os.remove(self.elb_log_file_path)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.output_csv_file_path)
        except FileNotFoundError:
            pass

    def test_elb_access_log2csv(self):
        # elb log write to file
        with open(self.elb_log_file_path, "w") as f:
            f.write("\n".join(self.elb_log_lines))

        assert os.path.isfile(self.elb_log_file_path)
        assert not os.path.isfile(self.output_csv_file_path)

        # TC: "elb_access_log2csv" function
        aws_elb_access_log2csv(
            self.elb_log_file_path, self.output_csv_file_path, field_names=AwsElbAccessLog.raw_field_names)

        assert os.path.isfile(self.output_csv_file_path)

        data_row_count = 0
        data_row_list = []
        with open(self.output_csv_file_path, "r") as f:
            rdr = csv.reader(f)
            for row in rdr:
                data_row_list.append(row)
                data_row_count += 1

        assert data_row_count == len(self.elb_log_lines) + 1

        # TC: DataFrame from csv and ElbAccessLog items
        lines = []
        for line in self.elb_log_lines:
            lines.append(AwsElbAccessLog(line).to_dict(field_names=AwsElbAccessLog.raw_field_names))

        df1 = pd.DataFrame(data_row_list[1:], columns=data_row_list[0])
        df1_dict = df1.to_dict()  # from csv

        df2 = pd.DataFrame(lines)  # from setup data
        df2_dict = df2.to_dict()

        for k, v in df2_dict.items():
            assert df1_dict[k] == v
