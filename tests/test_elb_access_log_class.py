from utils import AwsElbAccessLog


def test_data_convert_to_dict_by_default_or_wrong():
    log1 = AwsElbAccessLog(single_line=None)
    log2 = AwsElbAccessLog(single_line=2)
    assert log1.to_dict() == {}
    assert log2.to_dict() == {}


def test_data_convert_to_dict_by_list():
    log1 = AwsElbAccessLog(single_line=["http"])
    log2 = AwsElbAccessLog(single_line=["http", "2018-07-02T22:23:00.186641Z"])
    log3 = AwsElbAccessLog(single_line=[
        "http", "2018-07-02T22:23:00.186641Z", "app/my-loadbalancer/50dc6c495c0c9188", "192.168.131.39:2817"])

    assert log1.to_dict() == {"type": "http"}
    assert log2.to_dict() == {
        "type": "http",
        "timestamp": "2018-07-02T22:23:00.186641Z"
    }

    assert log3.to_dict() == {
        "type": "http",
        "timestamp": "2018-07-02T22:23:00.186641Z",
        "elb": "app/my-loadbalancer/50dc6c495c0c9188",
        "client:port": "192.168.131.39:2817",
        "client_ip": "192.168.131.39",
        "client_port": "2817"
    }


def test_data_convert_to_dict_by_str():
    log = AwsElbAccessLog(
        single_line='https 2018-07-02T22:23:00.186641Z app/my-loadbalancer/50dc6c495c0c9188 192.168.131.39:2817'
        ' 10.0.0.1:80 0.086 0.048 0.037 200 200 0 57 "GET https://www.example.com:443/ HTTP/1.1"'
        ' "curl/7.46.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-2:12345678'
        '9012:targetgroup/my-targets/73e2d6bc24d8a067 "Root=1-58337281-1d84f3d73c47ec4e58577259"'
        ' "www.example.com" "arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-12345678'
        '9012" 1 2018-07-02T22:22:48.364000Z "authenticate,forward" "-" "-"')

    assert log.to_dict() == {
        'type': 'https', 'timestamp': '2018-07-02T22:23:00.186641Z', 'elb': 'app/my-loadbalancer/50dc6c495c0c9188',
        'client:port': '192.168.131.39:2817', 'target:port': '10.0.0.1:80', 'request_processing_time': '0.086',
        'target_processing_time': '0.048', 'response_processing_time': '0.037', 'elb_status_code': '200',
        'target_status_code': '200', 'received_bytes': '0', 'sent_bytes': '57',
        'request': 'GET https://www.example.com:443/ HTTP/1.1', 'user_agent': 'curl/7.46.0',
        'ssl_cipher': 'ECDHE-RSA-AES128-GCM-SHA256', 'ssl_protocol': 'TLSv1.2',
        'target_group_arn':
            'arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067',
        'trace_id': 'Root=1-58337281-1d84f3d73c47ec4e58577259', 'domain_name': 'www.example.com',
        'chosen_cert_arn': 'arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012',
        'matched_rule_priority': '1', 'request_creation_time': '2018-07-02T22:22:48.364000Z',
        'actions_executed': 'authenticate,forward', 'redirect_url': '-', 'error_reason': '-',
        'client_ip': '192.168.131.39', 'client_port': '2817', 'target_ip': '10.0.0.1', 'target_port': '80',
        'request_verb': 'GET', 'request_url': 'https://www.example.com:443/', 'request_proto': 'HTTP/1.1'
    }
