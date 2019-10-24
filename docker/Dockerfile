FROM python:3.6
MAINTAINER Jon Duckworth <Jon.Duckworth@digitalglobe.com>

RUN apt-get update && \
	apt-get -y upgrade && \
	apt install -y gdal-bin

RUN pip install --upgrade pip && \
	pip install rio-cogeo git+https://github.com/GeoBigData/gbdx-task-interface.git

COPY src /src

CMD ["python", "/src/create_cog.py"]