#!/bin/sh

pdebuild --debbuildopts "-I.svn -I.empty -I*.pyc -I.zim*" --logfile ../build.log

sudo dpkg -i /var/cache/pbuilder/result/xetex-ptxplus_0.2-2.3_all.deb /var/cache/pbuilder/result/xetex-ptxplus-examples_0.2-2.3_all.deb
