
#!/bin/bash
set -euo pipefail

DB="jdbc:mysql://127.0.0.1:3306/convenience_retail"
HDFS="/user/minhnhat/convenience_retail/raw"

for table in products transactions transaction_items
do
    echo "===== Import $table ====="

    sqoop import \
        --connect "$DB" \
        --username sqoopuser \
        -P \
        --table "$table" \
        --target-dir "$HDFS/$table" \
        --delete-target-dir \
        --as-textfile \
        --fields-terminated-by '\001' \
        --num-mappers 1

    hdfs dfs -test -e "$HDFS/$table/_SUCCESS"
    count=$(hdfs dfs -cat "$HDFS/$table/part-m-*" | wc -l)

    echo "$table: $count dong"
done

echo "IMPORT HOAN THANH!"
