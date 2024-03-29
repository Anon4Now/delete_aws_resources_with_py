FROM ubuntu:focal-20220426

RUN apt-get update -y
RUN apt-get install -y ca-certificates software-properties-common gcc

#Use this to create a trust .crt file for Ubuntu
#COPY <CERTNAME>.crt /usr/local/share/ca-certificates/
RUN dpkg-reconfigure ca-certificates

RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update

RUN apt install -y python3.8
RUN apt install -y python3-pip python3-distutils python3-apt

RUN pip install boto3

WORKDIR /usr/app/src
COPY delete_aws_resources_with_py/* ./

CMD [ "python3", "-m", "delete_aws_resources_with_py.main", "-o", "<ADD OPTION HERE> (i.e. modify or delete) ]
