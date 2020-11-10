#docker build -t crawler . && docker run -p 5050:5050 -p 5051:5051 -p 40000:40000 -v C:\Temp:/home/mlib/crawler/data -v C:\Temp:/home/mlib/crawler/log --name crawler crawler  
FROM crawl:latest
WORKDIR .
USER root
COPY . /home/mlib/crawler
RUN chown -R etl /home/mlib/crawler
RUN chgrp -R etl /home/mlib/crawler
USER etl
#RUN pip3 install --user -r /home/mlib/crawler/requirements.txt
WORKDIR /home/mlib/crawler
ENV PATH $PATH:$HOME/.local/bin:$HOME/bin:/usr/bin:/usr/sbin:/usr/local/bin:$HOME/bin:$HOME/mlib/Mobigen/bin
ENV PYATHONPATH $HOME/mlib:$HOME/mlib/iris:$HOME/mlib/Mobigen:$HOME/mlib/iris/API
ENV IRIS_LIBRARY $HOME/mlib/iris/API/M6
CMD bash -c "source ~/.bash_profile && /home/etl/mlib/Mobigen/bin/SIOEF2 0.0.0.0 40000 /home/mlib/crawler/conf/SIOEF.conf"
