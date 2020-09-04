# aws-elb-access-log2csv

- command usage
```bash
python log2csv.py -i [input aws-elb-access-log-file] -o [output csv-file]
```
> Ex) python log2csv.py -i sample/elb.log -o result.csv

```bash
./scripts/make_csv.sh -p [prefix yyyyMMdd or yyyyMMddThh formate date string]
```
> Ex) ./scripts/make_csv.sh -p 20200901 (log2csv about all of 2020-09-01 aws-elblogs per hour)

> Ex) ./scripts/make_csv.sh -p 20200901T00 (log2csv about 2020-09-01T00 aws-elblogs
