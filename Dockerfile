FROM jenkins:latest
MAINTAINER Estevao Oliveira
ADD ./teste_jenkins.py /var/
USER root
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y vim 
RUN apt-get install -y nano



