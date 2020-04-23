#!/bin/sh
flag='True'
while [ $flag != 'False' ];
do
        if [ -e '/home/mAdvisor/mAdvisor-api/metastore_db/db.lck' ]
        then
                echo "exist"
                rm -f /home/mAdvisor/mAdvisor-api/metastore_db/db.lck
        fi
        if [ -e "/home/mAdvisor/mAdvisor-api/metastore_db/dbex.lck" ]
        then
                echo "exist"
                rm -f /home/mAdvisor/mAdvisor-api/metastore_db/dbex.lck
        fi
done

