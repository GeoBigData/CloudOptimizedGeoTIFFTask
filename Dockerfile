FROM pedros007/debian-gdal:2.2.0
MAINTAINER Jon Duckworth <Jon.Duckworth@digitalglobe.com>

# Install Python dependencies
WORKDIR /tmp
RUN yes | pip install gdal

# Create the input and output directories
RUN mkdir /mnt/work && \
    mkdir /mnt/work/input && \
    mkdir /mnt/work/output

# Copy source code
COPY /*.py /src/

WORKDIR /src

CMD 'python cloud-optimized-geotiff-task.py'