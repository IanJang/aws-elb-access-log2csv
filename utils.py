import csv
from collections import Iterable

from io import StringIO
from pandas import DataFrame


class AwsElbAccessLog(object):
    # reference:
    # https://docs.aws.amazon.com/ko_kr/elasticloadbalancing/latest/application/load-balancer-access-logs.html#access-log-entry-format
    __raw_field_names = [
        "type", "timestamp", "elb", "client:port", "target:port", "request_processing_time",
        "target_processing_time", "response_processing_time", "elb_status_code", "target_status_code", "received_bytes",
        "sent_bytes", "request", "user_agent", "ssl_cipher", "ssl_protocol", "target_group_arn", "trace_id",
        "domain_name", "chosen_cert_arn", "matched_rule_priority", "request_creation_time", "actions_executed",
        "redirect_url", "error_reason"
    ]

    __custom_field_names = [
        "client_ip", "client_port", "target_ip", "target_port", "request_verb", "request_url", "request_proto"
    ]

    def __init__(self, single_line):
        self.data = {}
        if type(single_line) is str:
            buff = StringIO(single_line)
            single_line = next(csv.reader(buff, delimiter=' '))
        if isinstance(single_line, Iterable):
            self.data = dict(zip(self.__raw_field_names, single_line))

    def __getitem__(self, item):
        if item in self.data:
            return self.data[item]
        else:  # access to custom fields by property
            r = getattr(self, item, None)
            if type(r) is callable:
                return None
            return r

    def to_dict(self, keys=None):
        ret = {}
        if keys is None:
            keys = self.__raw_field_names + self.__custom_field_names
        for key in keys:
            if self[key]:
                ret.update({str(key): self[key]})
        return ret

    @property
    def client_ip(self):
        try:
            return self.data["client:port"].split(":")[0]
        except:
            return None

    @property
    def client_port(self):
        try:
            return self.data["client:port"].split(":")[1]
        except:
            return None

    @property
    def target_ip(self):
        try:
            return self.data["target:port"].split(":")[0]
        except:
            return None

    @property
    def target_port(self):
        try:
            return self.data["target:port"].split(":")[1]
        except:
            return None

    @property
    def request_verb(self):
        try:
            return self.data["request"].split()[0]
        except:
            return None

    @property
    def request_url(self):
        try:
            return self.data["request"].split()[1]
        except:
            return None

    @property
    def request_proto(self):
        try:
            return self.data["request"].split()[2]
        except:
            return None


def aws_elb_access_log2csv(elb_log_file_path, output_csv_file_path, columns=None):
    if not columns:
        columns = [
            "type", "timestamp", "elb", "client_ip", "client_port", "target_ip", "target_port",
            "request_processing_time", "target_processing_time", "response_processing_time", "elb_status_code",
            "target_status_code", "received_bytes", "sent_bytes", "request_verb", "request_url", "request_proto",
            "user_agent", "ssl_cipher", "ssl_protocol", "target_group_arn", "trace_id", "domain_name",
            "chosen_cert_arn", "matched_rule_priority", "request_creation_time", "actions_executed", "redirect_url",
            "error_reason"
        ]
    rows = []
    with open(elb_log_file_path) as f:
        for row in csv.reader(f, delimiter=' '):
            rows.append(AwsElbAccessLog(row).to_dict(keys=columns))

    df = DataFrame(rows)
    df.to_csv(output_csv_file_path, index=False, columns=columns, header=columns,
              encoding='utf-8')
