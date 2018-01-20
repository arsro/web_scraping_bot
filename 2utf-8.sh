#!/usr/bin/bash

# see 
# http://d.hatena.ne.jp/shu223/20111201/1328334689
# http://taka-say.hateblo.jp/entry/2015/06/25/010000


cat > /usr/lib/python2.7/site-packages/sitecustomize.py << "EOF"
import sys
sys.setdefaultencoding('utf-8')
EOF

