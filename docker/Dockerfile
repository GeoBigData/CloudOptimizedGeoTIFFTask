FROM ubuntu:16.04
MAINTAINER Jon Duckworth <Jon.Duckworth@digitalglobe.com>

RUN apt-get update -y \
    && apt-get install software-properties-common -y \
    && add-apt-repository ppa:ubuntugis/ubuntugis-unstable \
    && apt-get update -y \
    && apt-get install gdal-bin jq -y

COPY src /usr/src/app
RUN chmod +x /usr/src/app/create-cloud-optimized-geotiffs.sh

WORKDIR /usr/src/app

ENV INDIR /mnt/work/input/data
ENV OUTDIR /mnt/work/output/data

CMD sh -e "/usr/src/app/create-cloud-optimized-geotiffs.sh"