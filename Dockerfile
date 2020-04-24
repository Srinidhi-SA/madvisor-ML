FROM ubuntu:16.04 
LABEL project="apache-spark"
RUN useradd -u 404 spark 
MAINTAINER marlabs

RUN groupadd -r marlabs && useradd -r -s /bin/false -g marlabs marlabs

#installing the required packages
RUN apt-get update && apt-get upgrade -y
RUN apt-get install openjdk-8-jdk vim net-tools telnet iputils-ping -y
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre
#RUN apt-get install python3-pip virtualenv enchant -y
RUN apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

#adding madvisor code 
RUN mkdir /home/mAdvisor/
WORKDIR /home/mAdvisor/
ADD requirements.tgz /home/mAdvisor/
RUN gzip -d /home/mAdvisor/requirements.tgz
RUN ls -la /home/mAdvisor
#RUN virtualenv --python=python3 myenv
#RUN . myenv/bin/activate && 
RUN pip3 install pywebhdfs==0.4.1
#Adding new command here for python-sjsclient
RUN apt-get update && apt-get install enchant libssl-dev libmysqlclient-dev -y
#RUN pip3 install --upgrade pip

RUN pip3 install pbr
RUN pip3 install pywebhdfs==0.4.1

RUN pip3 install python-sjsclient
#RUN rm -rf myenv/

RUN apt-get install -y locales locales-all
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN apt-get install libmysqlclient-dev postgresql-server-dev-all -y
#RUN . myenv/bin/activate &&
RUN pip3 install -U setuptools
RUN pip3 install pyspark==2.4.0
RUN pip3 install pyenchant && pip3 install sklearn2pmml && pip3 install -r requirements.txt

#copy api code
ADD code.tgz /home/mAdvisor
RUN ls -al /home/mAdvisor
WORKDIR /home/mAdvisor/mAdvisor-api/
RUN mkdir hadoop_conf/
ENV HADOOP_CONF_DIR=/home/mAdvisor/mAdvisor-api/hadoop_conf/
#Virtual Env

#setting the env
ENV SPARK_HOME=/usr/local/spark-2.4.0-bin-hadoop2.7/
ENV PATH=${SPARK_HOME}/bin:$PATH

#copy spark code inside and untar it
RUN apt-get install wget -y
RUN wget -O /tmp/spark.tgz https://archive.apache.org/dist/spark/spark-2.4.0/spark-2.4.0-bin-hadoop2.7.tgz && \
	tar -xzf /tmp/spark.tgz -C /usr/local && \
	ln -sf /usr/local/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /usr/local/spark && \
	rm -rf /tmp/spark.tgz
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.41/mysql-connector-java-5.1.41.jar --no-check-certificate 
RUN mv mysql-connector-java-5.1.41.jar /usr/local/spark-2.4.0-bin-hadoop2.7/jars/ && mv $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh && echo "SPARK_CLASSPATH=/usr/local/spark-2.4.0-bin-hadoop2.7/jars/mysql-connector-java-5.1.41.jar" >> $SPARK_HOME/conf/spark-env.sh

#copy spark startup script, conf file and egg file
COPY startup.sh $SPARK_HOME/
RUN apt-get install docker.io -y 
WORKDIR /home/mAdvisor/mAdvisor-api/scripts
COPY marlabs_bi_jobs-0.0.0-py3.6.egg .
RUN ls -l  /home/mAdvisor/mAdvisor-api/scripts
WORKDIR /home/mAdvisor/mAdvisor-api
RUN chmod +x $SPARK_HOME/startup.sh && chmod +x /home/mAdvisor/mAdvisor-api/scripts/marlabs_bi_jobs-0.0.0-py3.6.egg
EXPOSE 8080 4040 6379
WORKDIR /home/mAdvisor/mAdvisor-api/
RUN mkdir server_log
COPY lock.sh /home/mAdvisor/mAdvisor-api/
COPY hadoop_conf/ /home/mAdvisor/mAdvisor-api/hadoop_conf/
RUN chmod +x /home/mAdvisor/mAdvisor-api/lock.sh

#RUN chown marlabs:marlabs /home/mAdvisor/mAdvisor-api
#RUN chown marlabs:marlabs /usr/local/spark-2.3.0-bin-hadoop2.7/startup.sh
#RUN chown marlabs:marlabs /home/mAdvisor/mAdvisor-api/server_log
RUN mkdir /usr/local/spark-2.4.0-bin-hadoop2.7//logs
#RUN chown marlabs:marlabs /usr/local/spark-2.3.0-bin-hadoop2.7//logs
RUN mv /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf.template /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf
#RUN chown marlabs:marlabs /usr/local/spark-2.3.0-bin-hadoop2.7/conf/spark-defaults.conf
#RUN chown marlabs:marlabs /home/mAdvisor/mAdvisor-api/scripts
#RUN chown marlabs:marlabs $HADOOP_CONF_DIR
#RUN mkdir /home/marlabs/ && mkdir /home/marlabs/nltk_data && chown marlabs:marlabs /home/marlabs/nltk_data
#RUN chown marlabs:marlabs /tmp
RUN pip3 install -U scikit-learn 
#fabric==1.14.1
RUN pip install fabric3
RUN apt-get install curl -y
RUN apt-get install python3-tk -y
RUN pip3 install scipy==1.2.3
COPY celery_reload.sh /home/mAdvisor/mAdvisor-api/
RUN chmod +x /home/mAdvisor/mAdvisor-api/celery_reload.sh
RUN pip3 install json2xml
RUN pip3 install Shapely
RUN apt-get -y install poppler-utils && apt-get clean
#USER marlabs
ENTRYPOINT ["/usr/local/spark-2.4.0-bin-hadoop2.7/startup.sh"]
