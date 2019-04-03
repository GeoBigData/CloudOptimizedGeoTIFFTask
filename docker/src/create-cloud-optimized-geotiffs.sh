#!/usr/bin/env bash -ex

############################################
# Script: create-cloud-optimized-geotiffs.sh
# Author: Jon Duckworth <jon.duckworth@digitalglobe.com>
#
# Created: 2018-03-19
# Last Updated:
#
# Description:
# Bash script to be used in the 'cloudoptimizedgeotiff' GBDX task to create Cloud Optimized GeoTIFFs from a
# directory of input tifs. The script will find all .tif or .TIF files in all subdirectories of the GBDX
# task input mount and attempt to convert to Cloud-Optimized GeoTIFFs.
#
# If any Cloud-Optimized GeoTIFFs are
# successfully created, the task succeeds.
############################################

# Set up a staging directory for intermediate TIFFs
staging_dir="/mnt/work/staging";
mkdir -p ${staging_dir};


get_band_count() {
    ############################################
    # Gets the number of bands in a given TIFF
    #  using gdalinfo.
    #
    # $band_count: number of bands in the image
    ############################################
    local temp_tif=$1;

    local band_count=$(gdalinfo ${temp_tif} | grep "^Band [[:digit:]]\+" | wc -l);

    echo ${local};
}

# List tif files in input data directory
all_tifs=$(find ${INDIR} -type f | grep "\.[tT][iI][fF]$");

# Create Cloud Optimized GeoTIFF for each input TIFF
for tif in ${all_tifs};
do
    # Get number of bands
    band_count=$(get_band_count ${tif});

    # Parse the basename (filename without the input data directory prefix
    # (e.g. /mnt/work/input/data/subdirectory/my.tif -> subdirectory/my.tif)
    basename=$(echo ${tif} | sed "s~${INDIR}/\(.*\.[tT][iI][fF]\)$~\1~");
    prefix=$(echo ${tif} | sed "s~${INDIR}/\(.*\)/.*\.[tT][iI][fF]$~\1~");

    # Set up the GDAL GeoTIFF creation options
    if [ ${band_count} -eq 3 ]; then
        # If image is 3-band, use JPEG compression with the YCBCR color space for maximum compression
        photometric_option="-co PHOTOMETRIC=YCBCR";
        compress_option="-co COMPRESS=JPEG";
    else
        # If image is not 3-band, use less optimal LZW compression (better interoperability than DEFLATE)
        compress_option="-co COMPRESS=LZW";
    fi

    # Create the initial tiled image
    mkdir -p ${staging_dir}/${prefix};
    gdal_translate ${tif} ${staging_dir}/${basename} \
    -co TILED=YES \
    ${photometric_option} \
    ${compress_option} \
    -co BIGTIFF=IF_SAFER && \
    # Add overviews
    gdaladdo -r average ${staging_dir}/${basename} 2 4 8 16 32 && \
    # Create the final compressed image
    mkdir -p ${OUTDIR}/${prefix};
    gdal_translate ${staging_dir}/${basename} ${OUTDIR}/${basename} \
    -co COPY_SRC_OVERVIEWS=YES \
    -co TILED=YES \
    ${photometric_option} \
    ${compress_option} \
    -co BIGTIFF=IF_SAFER;
done

# Write the GBDX status file. Succeeds if ANY Cloud Optimized GeoTIFFs were created.
n_results=$(find ${OUTDIR} -type f | grep ".*\.[tT][iI][fF]$" | wc -l);
if [ ${n_results} -eq 0 ]; then
    cat /usr/src/app/status.json | jq ".status |= \"failed\"" | jq ".reason |= \"Failed to create any Cloud Optimized GeoTIFFs.\"" > ${OUTDIR}/status.json;
else
    cat /usr/src/app/status.json | jq ".status |= \"success\"" | jq ".reason |= \"Created ${n_results} Cloud Optimized GeoTIFFs.\"" > ${OUTDIR}/status.json;
fi
