#!/bin/sh

#changing spark.driver.host 
#mv /usr/local/spark-2.3.0-bin-hadoop2.7/conf/spark-defaults.conf.template /usr/local/spark-2.3.0-bin-hadoop2.7/conf/spark-defaults.conf
HOST=$(hostname -i)
echo "spark.driver.host $HOST" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf 
echo "spark.driver.cores 2" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf 
echo "spark.driver.memory 4G" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf 
echo "spark.executor.cores 4" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf 
echo "spark.executor.memory 7G" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf 
echo "spark.executor.memoryOverhead 800" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf 
echo "spark.driver.memoryOverhead 500" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-defaults.conf
#Python3 env setup
#cho "PYSPARK_PYTHON=/usr/bin/python3.5" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-env.sh
#cho "PYTHONHASHSEED=0" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-env.sh
#echo "SPARK_YARN_USER_ENV=PYTHONHASHSEED=0" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-env.sh



#ls /tmp/spark.conf
#if [ $? = 0 ]; then
#        value=`cat /tmp/spark.conf`
#        echo "$value\n"

#        if [ "$value" = "master" ]; then
                sh /usr/local/spark-2.4.0-bin-hadoop2.7/sbin/start-master.sh
                #celery worker -A config.celery -l info -Q $QUEUE_NAME
		celery worker -A config.celery --beat --scheduler 'django_celery_beat.schedulers:DatabaseScheduler' -l info -Q $QUEUE_NAME &
		sh lock.sh &
                tail -f /dev/null
#        else
#                for word in $value
#                do
#                        if [ "$word" != "slave" ]; then
#                                echo "./sbin/start-slave.sh spark://${word}:7077"
#                                ./sbin/start-slave.sh spark://${word}:7077
#                                tail -f /dev/null
#                        fi
#                done
#        fi
#fi
#Python3 env setup
echo "PYSPARK_PYTHON=/usr/bin/python3.5" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-env.sh
echo "PYTHONHASHSEED=0" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-env.sh
echo "SPARK_YARN_USER_ENV=PYTHONHASHSEED=0" >> /usr/local/spark-2.4.0-bin-hadoop2.7/conf/spark-env.sh
