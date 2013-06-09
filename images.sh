#!/bin/bash
siteno=6888ff
site='http://hesperidesfloristry.wix.com/take-3'

base="${site}?_escaped_fragment_="
pages=`curl -s "${base}"|grep "<a.*${site}"|sed 's/.*#!\([^ ]*\) .*/\1/'|sort|uniq`

for i in $pages; do
    echo $i
    curl -Ls "${base}$i"|grep "<img.*/${siteno}_"|cut -d\" -f2| \
        sed 's/^/- /'| \
        sed 's/- \(.*01badb849f311a1b34bee4cc26d8baf0\)/  \1/' |\
        sed 's/- \(.*63454b3fef4bd771a1877f083c4a6078\)/  \1/'
done

