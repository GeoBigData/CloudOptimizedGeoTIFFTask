import subprocess
import os

import rasterio

SUPPORTED_RASTER_EXTENSIONS = (
    '.tif',
    '.vrt',
)

# specify input paths
in_path = '/mnt/work/input'
out_path = '/mnt/work/output'

in_data_path = os.path.join(in_path, 'data')
out_data_path = os.path.join(out_path, 'data')

if __name__ == '__main__':

    if not os.path.exists(out_data_path):
        os.makedirs(out_data_path)

    # Grab all rasters in the input directory
    input_filepaths = [
        os.path.join(in_data_path, filename)
        for filename in os.listdir(in_data_path)
        if os.path.splitext(filename)[1].lower() in SUPPORTED_RASTER_EXTENSIONS
    ]

    for input_path in input_filepaths:
        with rasterio.open(input_path) as src:
            band_count = src.count
            data_type = src.dtypes[0]

        file_basename = os.path.basename(input_path)
        out_file = os.path.join(out_data_path, file_basename)

        # Determine the profile
        if band_count == 3 and data_type == 'uint8':
            profile = 'jpeg'
        elif band_count in [3, 4] and data_type == 'uint8':
            profile = 'webp'
        else:
            profile = 'lzw'

        os.environ['CHECK_DISK_FREE_SPACE'] = 'FALSE'
        subprocess.run(
            'rio cogeo create {input_path} {out_file} --cog-profile {profile}'.format(
                out_file=out_file,
                input_path=input_path,
                profile=profile,
            ),
            shell=True,
        )
