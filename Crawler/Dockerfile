FROM crawler_crawler:latest
WORKDIR .
COPY . /home/mlib/crawler
RUN chown -R etl /home/mlib/crawler
RUN chgrp -R etl /home/mlib/crawler
USER etl
#RUN pip3 install --user -r /home/mlib/crawler/requirements.txt
WORKDIR /home/mlib/crawler
ENV PATH $PATH:$HOME/.local/bin:$HOME/bin:/usr/bin:/usr/sbin:/usr/local/bin:$HOME/bin:$HOME/mlib/Mobigen/bin
ENV PYATHONPATH $HOME/mlib:$HOME/mlib/iris:$HOME/mlib/Mobigen:$HOME/mlib/iris/API
ENV IRIS_LIBRARY $HOME/mlib/iris/API/M6