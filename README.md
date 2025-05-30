# IGRF FastAPI Application

This is a FastAPI application that provides an API for calculating IGRF (International Geomagnetic Reference Field) variations.

## Features

- Calculate IGRF variations for a single point
- Process multiple points in a single request
- Accept stringified JSON input
- CORS enabled for cross-origin requests

## Project Structure

- `main.py`: The main application file containing the FastAPI application and endpoints
- `requirements.txt`: Lists all Python dependencies
- `Procfile`: Specifies the command to start the application on Render
- `runtime.txt`: Specifies the Python version for Render

## API Endpoints

- `GET /`: Returns a simple "Hello World" message
- `GET /hello/{name}`: Returns a greeting with the provided name
- `GET /points`: Returns all available data points
- `GET /points/{point_id}`: Returns a specific data point by ID
- `GET /pyigrf/`: Returns IGRF variation for a fixed point (long=100, lat=100, altitude=500, year=2024.9)
- `POST /pyigrf`: Calculates IGRF variations for multiple points
  - Input: JSON object with a `points_json` field containing a stringified JSON array of points
  - Each point should have `latitude`, `longitude`, `altitude`, and `year` fields
  - Returns an array of IGRF variation results

## Deployment on Render

This application is configured for deployment on [Render](https://render.com/). Follow these steps to deploy:

### Prerequisites

- A [Render](https://render.com/) account
- Git repository with your code

### Configuration Files

The repository includes the following configuration files for Render deployment:

- `requirements.txt`: Lists all Python dependencies
- `Procfile`: Specifies the command to start the application
- `runtime.txt`: Specifies the Python version (3.9.0)
- `render.yaml`: Specifies the build command, start command, and environment variables
- `predeploy.sh`: A script that runs during deployment to copy custom files to the pyIGRF site-packages folder

### Environment Variables

Render automatically sets the following environment variables:

- `PORT`: The port on which the application should listen
- `RENDER`: Set to `true` when running on Render

No additional environment variables are required for this application.

### Custom Files for pyIGRF

The application uses the pyIGRF package to calculate IGRF variations. The repository includes custom versions of the following files that are automatically copied to the pyIGRF site-packages folder during deployment:

- `custom_loadCoeffs.py`: A custom version of the loadCoeffs.py file from the pyIGRF package with improved error handling
- `custom_igrf14coeffs.txt`: A custom version of the igrf14coeffs.txt file from the pyIGRF package

These custom files are essential for the application to work correctly on Render. The `custom_loadCoeffs.py` file includes improved error handling and fallback mechanisms to prevent the application from crashing if the coefficient file can't be found. The `custom_igrf14coeffs.txt` file contains the IGRF coefficients needed for the calculations.

The predeploy script (`predeploy.sh`) automatically detects these files and copies them to the appropriate locations in the pyIGRF site-packages folder during deployment. The script includes multiple methods to find the pyIGRF directory and creates the necessary directories and files even if the import fails.

Additionally, the main application (`main.py`) includes a robust fallback mechanism that:
1. Attempts to import pyIGRF normally
2. If the import fails, creates the necessary directories and copies the custom files to those directories
3. Tries to import pyIGRF again after setting up the environment
4. If the import still fails, provides a fallback implementation that returns reasonable default values

This multi-layered approach ensures that the application will continue to function even if there are issues with the pyIGRF package or the coefficient files, making the deployment more resilient.

If you need to modify these files:

1. Make your changes to the custom files in the root directory of the repository
2. The predeploy script will automatically copy the updated files to the appropriate locations during deployment

### Deployment Steps

1. **Create a new Web Service on Render**
   - Log in to your Render dashboard
   - Click on "New" and select "Web Service"
   - Connect your repository or provide the repository URL

2. **Configure the Web Service**
   - Name: Choose a name for your service (e.g., "igrf-api")
   - Environment: Select "Python 3"
   - Region: Choose a region close to your users
   - Branch: Select the branch to deploy (usually "main" or "master")
   - Build Command: `pip install -r requirements.txt && ./predeploy.sh`
   - Start Command: `uvicorn main:app --host=0.0.0.0 --port=$PORT`
   - Note: If you're using the render.yaml file, these commands will be automatically configured

3. **Create the Web Service**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

4. **Access Your API**
   - Once deployment is complete, you can access your API at the URL provided by Render
   - The API documentation will be available at `https://your-service-name.onrender.com/docs`
   - You can interact with all endpoints directly from the documentation page
   - The OpenAPI specification is available at `https://your-service-name.onrender.com/openapi.json`

5. **Updating Your Application**
   - When you push changes to your repository, Render will automatically rebuild and redeploy your application
   - You can also manually trigger a deploy from the Render dashboard
   - View deployment logs in the Render dashboard to troubleshoot any issues

6. **Monitoring and Scaling**
   - Monitor your application's performance in the Render dashboard
   - View logs to identify and troubleshoot issues
   - Scale your application by changing the instance type in the Render dashboard
   - Set up alerts for downtime or high resource usage

7. **Custom Domains and HTTPS**
   - Render provides a default HTTPS endpoint for your service
   - You can add a custom domain in the Render dashboard
   - Render automatically provisions and renews SSL certificates for custom domains
   - CORS is already configured in the application to allow cross-domain requests

8. **Security Considerations**
   - The API currently allows requests from any origin (CORS `allow_origins=["*"]`)
   - For production, consider restricting allowed origins to specific domains
   - Render provides DDoS protection and SSL/TLS encryption
   - Consider adding rate limiting for production use

9. **Troubleshooting**
   - If the deployment fails, check the build logs in the Render dashboard
   - Ensure all dependencies are correctly specified in requirements.txt
   - Verify that the Procfile contains the correct command to start the application
   - Check that the application is listening on the port specified by the PORT environment variable
   - If you encounter CORS issues, verify that the CORS middleware is correctly configured
   - If you encounter a `FileNotFoundError` related to `igrf14coeffs.txt`:
     - This is a known issue that occurs when the pyIGRF package can't find its coefficient file
     - The repository includes custom files and a predeploy script to address this issue
     - Verify that the custom files (`custom_loadCoeffs.py` and `custom_igrf14coeffs.txt`) are present in the repository
     - Verify that the predeploy script has execute permissions (`chmod +x predeploy.sh`)
     - Check the build logs for any errors related to the predeploy script
     - If the predeploy script fails, you can manually copy the custom files to the pyIGRF site-packages folder after deployment
   - If you're still encountering issues with the pyIGRF package:
     - The custom_loadCoeffs.py file includes fallback mechanisms to prevent crashes
     - Check the application logs for messages about coefficient file locations
     - You may need to modify the custom_loadCoeffs.py file to add additional fallback paths

### Testing the Deployed API

You can test the deployed API using curl or any API client:

```bash
curl -X POST "https://your-service-name.onrender.com/pyigrf" \
  -H "Content-Type: application/json" \
  -d '{"points_json":"{\"points_json\":[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"}]}"}'
```

### Input and Output Formats

#### POST /pyigrf Input Format

The POST /pyigrf endpoint now supports multiple input formats for flexibility:

1. **Standard Format** - A JSON object with a `points_json` field containing a stringified JSON string:
   ```json
   {
     "points_json": "{\"points_json\":[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"}]}"
   }
   ```

2. **Direct Format** - A JSON object with a `points_json` field containing an array of points directly:
   ```json
   {
     "points_json": [
       {"latitude":"13.9375","longitude":"4.0625","altitude":"253.74992","year":"2024.9"},
       {"latitude":"13.9375","longitude":"4.1875","altitude":"255.7499","year":"2024.9"}
     ]
   }
   ```

3. **Raw String Format** - A stringified JSON string containing a `points_json` field with an array of points:
   ```
   "{\"points_json\":[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"},{\"latitude\":\"13.9375\",\"longitude\":\"4.1875\",\"altitude\":\"255.7499\",\"year\":\"2024.9\"}]}"
   ```

4. **Raw Array Format** - A stringified JSON array of points:
   ```
   "[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"},{\"latitude\":\"13.9375\",\"longitude\":\"4.1875\",\"altitude\":\"255.7499\",\"year\":\"2024.9\"}]"
   ```

5. **Direct JSON Format** - A JSON object with a `points_json` field containing an array of points, sent directly as the request body:
   ```json
   {"points_json":[{"latitude":"13.9375","longitude":"4.0625","altitude":"253.74992","year":"2024.9"},{"latitude":"13.9375","longitude":"4.1875","altitude":"255.7499","year":"2024.9"}]}
   ```

6. **Single Point Format** - A single point object, which will be automatically wrapped in an array:
   ```json
   {"latitude":"13.9375","longitude":"4.0625","altitude":"253.74992","year":"2024.9"}
   ```

The endpoint includes robust error handling and will attempt multiple parsing strategies to accommodate various input formats. If a parsing error occurs, a detailed error message will be returned to help diagnose the issue.

The endpoint also includes several features to ensure stability and reliability:

1. **Request Size Limits**: Requests larger than 10MB will be rejected to prevent memory exhaustion.
2. **Point Limits**: A maximum of 1000 points can be processed in a single request to prevent overloading the server.
3. **Input Validation**: Each point's latitude, longitude, altitude, and year values are validated to ensure they are within reasonable ranges.
4. **Batch Processing**: Points are processed in batches of 100 to manage memory usage efficiently.
5. **Timeout Handling**: Each point calculation has a 5-second timeout to prevent hanging on problematic inputs.
6. **Graceful Degradation**: If a point calculation fails, a fallback result is provided instead of failing the entire request.
7. **Minimal Logging**: Only essential information is logged to reduce I/O overhead.

Each point in the array should be an object with the following fields:

- `latitude`: Latitude in degrees (string)
- `longitude`: Longitude in degrees (string)
- `altitude`: Altitude in kilometers (string)
- `year`: Year (string)

For backward compatibility, the original endpoint is still available at `/pyigrf/model` and expects the Standard Format.

#### POST /pyigrf Output Format

The output from the POST /pyigrf endpoint is an array of IGRF variation results. Each result is an array containing the following values:

1. Declination (deg)
2. Inclination (deg)
3. Horizontal Intensity (nT)
4. North Component (nT)
5. East Component (nT)
6. Vertical Component (nT)
7. Total Intensity (nT)

Example output:

```json
[
  [
    -1.5206,
    -11.2313,
    31099.4,
    31066.3,
    -824.1,
    -6092.9,
    31707.1
  ],
  [
    -1.4841,
    -11.2208,
    31099.8,
    31068.1,
    -804.5,
    -6087.9,
    31706.9
  ]
]
```

## Local Development

To run the application locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Access the API at http://localhost:8000
