import subprocess
import os

from gbdx_task_interface import GbdxTaskInterface
import rasterio

SUPPORTED_RASTER_EXTENSIONS = (
    '.tif',
    '.vrt',
)


class CreateCOG(GbdxTaskInterface):

    def determine_profile(self, bands, dtype):
        port_profile = self.get_input_string_port('profile')
        if port_profile:
            print(f'Using user provided profile "{port_profile}"')
            return port_profile
        if bands == 3 and dtype == 'uint8':
            return 'jpeg'
        return 'deflate'

    def create_cog(self, fp):
        print(f'Processing image {fp}')

        out_data_path = self.get_output_data_port('data')

        with rasterio.open(fp) as src:
            band_count = src.count
            data_type = src.dtypes[0]

        cog_profile = self.determine_profile(band_count, data_type)
        print(f'(bands: {band_count}, dtype: {data_type}) => profile: {cog_profile}')

        file_basename = os.path.basename(fp)
        out_file = os.path.join(out_data_path, file_basename)

        os.environ['CHECK_DISK_FREE_SPACE'] = 'FALSE'
        subprocess.run(
            f'rio cogeo create {fp} {out_file} --cog-profile {cog_profile} --add-mask --overview-resampling bilinear --resampling bilinear --threads 16',
            shell=True,
        )

    def invoke(self):

        out_data_path = self.get_output_data_port('data')
        os.makedirs(out_data_path, exist_ok=True)

        # Grab all rasters in the input directory
        in_data_path = self.get_input_data_port('data')
        input_filepaths = [
            os.path.join(in_data_path, filename)
            for filename in os.listdir(in_data_path)
            if os.path.splitext(filename)[1].lower() in SUPPORTED_RASTER_EXTENSIONS
        ]

        for input_path in input_filepaths:
            self.create_cog(input_path)


if __name__ == '__main__':
    with CreateCOG() as task:
        task.invoke()
