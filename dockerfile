FROM ubuntu:22.04

WORKDIR /app/backend

RUN apt-get update && \
    apt-get install -y wget vim curl python3-pip python3-dev sox libsndfile1 portaudio19-dev && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY ./backend /app/backend
RUN ls -la /app/backend

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 15000

RUN chmod +x boot-entrypoint.sh && \
  echo '------Python libs are ready-----------------------'

ENTRYPOINT [ "/app/backend/boot-entrypoint.sh" ]
