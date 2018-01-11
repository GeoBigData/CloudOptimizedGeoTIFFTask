import subprocess
from subprocess import check_output, CalledProcessError
from os import path, mkdir
import string
from validate import validate as validate_geotiff, ValidateCloudOptimizedGeoTIFFException
import json
from glob import glob

# Define input/output directories
in_mnt = '/mnt/work/input'
in_path = path.join(in_mnt, 'data')
out_mnt = '/mnt/work/output'
out_path = path.join(out_mnt, 'data')

if not path.exists(out_path):
    mkdir(out_path)

# Parse the input ports
with open(path.join(in_mnt, 'ports.json'), 'r') as ports_json:
    input_ports = json.load(ports_json)

# Get list of all GeoTIFFs in input directory
input_images = glob(path.join(in_path, '*.tif'))

# If "images" input is present, filter to only those images
if 'images' in input_ports.keys() and input_ports['images'] != '':
    images_filter = input_ports['images'].split(',')
    input_images = [im for im in input_images if path.basename(im) in images_filter]


def write_error_log(image, message):
    """
    Writes the given error message to a log file in the outputs directory for the specified image.
    :param image: The ID (no file extension) of the image
    :param message: The string error message
    :return: None
    """
    log_path = path.join(out_path, '%s.error.log' % path.splitext(image)[0])
    mode = 'w' if not path.exists(log_path) else 'a'
    with open(log_path, mode) as error_log:
        if mode == 'a':
            error_log.write('\n')
        error_log.write(message)

for in_fp in input_images:

    basename = path.basename(in_fp)

    try:

        # Check for existence of file
        if not path.exists(in_fp):
            raise IOError('File %s does not exist in input directory' % basename)

        # Construct the filepath for the output optimized GeoTIFF
        out_fp = path.join(out_path, basename)

        # Create the raster overview
        overview_cmd = 'gdaladdo -r average %s 2 4 8 16 32' % in_fp

        # Create the cloud-optimized GeoTIFF
        optimize_cmd = 'gdal_translate %s \
                    %s \
                    -co TILED=YES \
                    -co COMPRESS=JPEG \
                    -co PHOTOMETRIC=YCBCR \
                    -co COPY_SRC_OVERVIEWS=YES' % (in_fp, out_fp)

        # Run both commands to create the final Cloud Optimized GeoTIFF
        full_cmd = string.join([overview_cmd, optimize_cmd], sep='; ')
        response = check_output(
            full_cmd,
            stderr=subprocess.STDOUT,
            shell=True
        )

        # Validate the GeoTIFF
        validate_geotiff(out_fp)

    except IOError as e:
        message = e.message
        write_error_log(basename, message)
        continue

    except CalledProcessError as e:
        message = 'Failed to create Cloud Optimized GeoTIFF from %s: %s' % (basename, e.output)
        write_error_log(basename, message)
        continue

    except ValidateCloudOptimizedGeoTIFFException as e:
        message = '%s is not a valid Cloud Optimized GeoTIFF: %s' % (basename, e.message)
        write_error_log(basename, message)
        continue
