Cloud Optimized GeoTIFF Task
============================

This task creates a Cloud Optimized GeoTIFF from a standard GeoTIFF input image.

# Dependencies

* GDAL v2.2.0

# Build Docker Image

```bash
docker build -t cloud-optimized-geotiff:<version> -f ./src/Dockerfile ./src
```

# Publish Docker Image

```bash
# Push versioned image
docker tag cloud-optimized-geotiff:0.2.1 jonduckworthdg/cloudoptimizedgeotiff:0.2.1
docker push jonduckworthdg/cloudoptimizedgeotiff:0.2.1

# Push latest image
docker tag cloud-optimized-geotiff:0.2.1 jonduckworthdg/cloudoptimizedgeotiff:latest
docker push jonduckworthdg/cloudoptimizedgeotiff:latest
```

# Testing

1. Create a `test/data` folder with the following subfolders:
    * `input`
    * `output`
2. Place a standard GeoTIFF file in `test-data/input`
3. Create a `test-data/input/ports.json` file with the following format:

    ```json
    {
      "images": "my_image_id.tif"
    }
    ```
4. Run `docker-compose up geotiff-test` from this directory to mount all of the proper data directories and run the task.

Note: This will also mount all python code in the current directory to `/src/*.py` in the container so you can make changes to the source code and re-run without rebuilding the image. **Be sure to re-build the image after completing your changes and before you re-deploy the task.**

# Register Task

Make any necessary changes to [register-task.json](./register-task.json) and run [register_task.py](./register_task.py) to register the task on the GBDX platform.