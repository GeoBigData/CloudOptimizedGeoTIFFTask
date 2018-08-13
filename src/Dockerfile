FROM ubuntu:16.04
MAINTAINER Jon Duckworth <Jon.Duckworth@digitalglobe.com>

# Install Python dependencies
WORKDIR /tmp
RUN apt-get -qq update && \
    apt-get install -y -qq wget build-essential python python-dev pkg-config git python-pip

RUN wget http://download.osgeo.org/gdal/2.2.3/gdal-2.2.3.tar.gz && \
    tar -xvf gdal-2.2.3.tar.gz

WORKDIR /tmp/gdal-2.2.3

RUN ./configure \
    --prefix=${PREFIX} \
    --with-geos \
    --with-geotiff=internal \
    --with-hide-internal-symbols \
    --with-libtiff=internal \
    --with-libz=internal \
    --with-threads \
    --without-bsb \
    --without-cfitsio \
    --without-cryptopp \
    --without-curl \
    --without-dwgdirect \
    --without-ecw \
    --without-expat \
    --without-fme \
    --without-freexl \
    --without-gif \
    --without-gif \
    --without-gnm \
    --without-grass \
    --without-grib \
    --without-hdf4 \
    --without-hdf5 \
    --without-idb \
    --without-ingres \
    --without-jasper \
    --without-jp2mrsid \
    --with-jpeg \
    --without-kakadu \
    --without-libgrass \
    --without-libkml \
    --without-libtool \
    --without-mrf \
    --without-mrsid \
    --without-mysql \
    --without-netcdf \
    --without-odbc \
    --without-ogdi \
    --without-openjpeg \
    --without-pcidsk \
    --without-pcraster \
    --without-pcre \
    --without-perl \
    --without-pg \
    --without-php \
    --without-png \
    --with-python \
    --without-qhull \
    --without-sde \
    --without-sqlite3 \
    --without-webp \
    --without-xerces \
    --without-xml2 && \
    make && \
    make install

# Create the input and output directories
RUN mkdir /mnt/work && \
    mkdir /mnt/work/input && \
    mkdir /mnt/work/output

# Copy source code
COPY /*.py /src/
COPY task-definition.json /src/task-definition.json

WORKDIR /src

CMD 'python cloud_optimized_geotiff_task.py'