FROM hmai:pybase_v2
MAINTAINER wudongsheng "wudongsheng@haima.me"
# hmai:g7_server_v7
RUN pip install jieba
COPY ./source /ai_g7
WORKDIR /ai_g7
EXPOSE 5000
RUN chmod u=rwx -R /ai_g7
RUN pip install -U cherry
CMD python ai_g7.py
#sudo docker run --runtime=nvidia -it -p 5000:5000 hmai:g7_server_v7
