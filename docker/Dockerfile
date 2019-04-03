FROM python:3.6
MAINTAINER Jon Duckworth <Jon.Duckworth@digitalglobe.com>

RUN pip install --upgrade pip && \
	pip install rio-cogeo

COPY src /src

CMD ["python", "/src/create_cog.py"]