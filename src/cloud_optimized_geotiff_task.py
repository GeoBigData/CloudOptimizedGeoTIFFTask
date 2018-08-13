import subprocess
from subprocess import check_output, CalledProcessError
from os import path, mkdir, makedirs
import string
from validate import validate as validate_geotiff, ValidateCloudOptimizedGeoTIFFException
import json
import re

STATUS_FAIL = 'fail'
STATUS_SUCCESS = 'success'

VALID_STATUS = [STATUS_SUCCESS, STATUS_FAIL]

# Define input directories
in_mnt = '/mnt/work/input'
in_path = path.join(in_mnt, 'data')

# Define/create output directories
out_mnt = '/mnt/work/output'
out_path = path.join(out_mnt, 'data')
if not path.exists(out_path):
    mkdir(out_path)

# Parse the input ports
with open(path.join(in_mnt, 'ports.json'), 'r') as ports_json:
    input_ports = json.load(ports_json)

# DEPRECATED
# # If "images" input is present, filter to only those images
# if 'images' in input_ports.keys() and input_ports['images'] != '':
#     images_filter = input_ports['images'].split(',')
#     input_images = [im for im in input_images if path.basename(im) in images_filter]


def write_status(status, reason):
    """
    Writes the given error message to the status file in the outputs directory.
    :param status: One of VALID_STATUS
    :param reason: The string status message
    :return: None
    """
    status_path = path.join(out_mnt, 'status.json')
    with open(status_path, 'w') as status_file:
        json.dump({
            'status': status,
            'reason': reason,
        }, status_file)


def get_band_count(img):
    """
    Gets the band count for the image at the given path.
    :param img: Full path to image.
    :return: Number of bands
    """
    cmd = 'gdalinfo {img} | grep "Band \d" | wc -l'.format(img=img)
    bands = check_output(cmd, shell=True)
    return int(bands.strip())


def write_log_file(images):
    with open(path.join(out_path, 'log.json'), 'w') as log_file:
        json.dump(images, log_file)


def add_image(images, dirname, names):
    tif_pattern = re.compile('([\w\d-]+\.[tT][iI][fF])$'.format(root=in_path))

    for n in names:
        if path.isfile(path.join(dirname, n)) and tif_pattern.match(n) is not None:
            images.append(
                path.join(dirname, tif_pattern.match(n).group(1))
            )


def main():
    messages = []
    image_status = {}

    # Get list of all GeoTIFFs in input directory
    input_images = []
    path.walk(in_path, add_image, input_images)

    basename_pattern = re.compile('{in_path}/(.*)$'.format(in_path=in_path))

    for image in input_images:
        band_count = get_band_count(image)
        basename = basename_pattern.match(image).group(1)
        filename = path.basename(basename)
        image_dir = path.join(out_path, path.dirname(basename))

        if not path.exists(image_dir):
            makedirs(image_dir)

        try:

            # Construct the filepath for the output optimized GeoTIFF
            out_fp = path.join(image_dir, filename)

            # Create the raster overview
            overview_cmd = 'gdaladdo -r average %s 2 4 8 16 32' % image

            # Create the cloud-optimized GeoTIFF
            options = [
                '-co TILED=YES',
                '-co COMPRESS=JPEG',
                '-co COPY_SRC_OVERVIEWS=YES'
            ]
            if band_count == 3:
                options.append('-co PHOTOMETRIC=YCBCR')
            optimize_cmd = 'gdal_translate %s \
                        %s \
                        %s' % (image, out_fp, ' '.join(options))

            # Run both commands to create the final Cloud Optimized GeoTIFF
            full_cmd = string.join([overview_cmd, optimize_cmd], sep='; ')

            print(full_cmd)

            check_output(
                full_cmd,
                stderr=subprocess.STDOUT,
                shell=True
            )

            # Validate the GeoTIFF
            validate_geotiff(out_fp)

            image_status[filename] = 'success'

        except ValidateCloudOptimizedGeoTIFFException as e:
            messages.append('%s is not a valid Cloud Optimized GeoTIFF: %s' % (basename, e.message))
            image_status[basename] = 'invalid'
            continue

        except Exception as e:
            write_status(STATUS_FAIL, str(e))
            image_status[basename] = 'fail'
            break

    write_status(STATUS_SUCCESS, '\n'.join(messages))
    write_log_file(image_status)


if __name__ == '__main__':
    main()
