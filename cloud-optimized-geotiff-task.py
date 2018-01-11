import subprocess
from subprocess import check_output, CalledProcessError
from os import path, mkdir
import string
from validate import validate as validate_geotiff, ValidateCloudOptimizedGeoTIFFException
import json
from glob import glob
from gbdx_task_interface import GbdxTaskInterface


class CloudOptimizedGeoTIFFTask(GbdxTaskInterface):

    @staticmethod
    def get_band_count(img):
        cmd = 'gdalinfo {img} | grep "Band \d" | wc -l'.format(img=img)
        response = check_output(cmd, shell=True)
        return int(response.strip())

    def invoke(self):
        input_images = glob(path.join(self.input_path, '**.tif'))
        input_images += glob(path.join(self.input_path, '**.TIF'))

        for img_fp in input_images:
            band_count = self.get_band_count(img_fp)
            basename = path.basename(img_fp)

            try:

                # Check for existence of file
                if not path.exists(img_fp):
                    raise IOError('File %s does not exist in input directory' % basename)

                # Construct the filepath for the output optimized GeoTIFF
                out_fp = path.join(self.output_path, basename)

                # Create the raster overview
                overview_cmd = 'gdaladdo -r average %s 2 4 8 16 32' % img_fp

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
                            %s' % (img_fp, out_fp, ' '.join(options))

                # Run both commands to create the final Cloud Optimized GeoTIFF
                full_cmd = string.join([overview_cmd, optimize_cmd], sep='; ')
                check_output(
                    full_cmd,
                    stderr=subprocess.STDOUT,
                    shell=True
                )

                # Validate the GeoTIFF
                validate_geotiff(out_fp)

            except IOError as e:
                raise Exception(e.message)

            except CalledProcessError as e:
                message = 'Failed to create Cloud Optimized GeoTIFF from %s: %s' % (basename, e.output)
                raise Exception(message)

            except ValidateCloudOptimizedGeoTIFFException as e:
                message = '%s is not a valid Cloud Optimized GeoTIFF: %s' % (basename, e.message)
                raise Exception(message)


if __name__ == '__main__':
    with CloudOptimizedGeoTIFFTask() as task:
        task.invoke()
