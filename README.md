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

The application uses the pyIGRF package to calculate IGRF variations. If you have custom versions of the following files, you can include them in your repository and they will be automatically copied to the pyIGRF site-packages folder during deployment:

- `custom_loadCoeffs.py`: A custom version of the loadCoeffs.py file from the pyIGRF package
- `custom_igrf14coeffs.txt`: A custom version of the igrf14coeffs.txt file from the pyIGRF package

To use custom files:

1. Place your custom files in the root directory of your repository with the names `custom_loadCoeffs.py` and/or `custom_igrf14coeffs.txt`
2. The predeploy script will automatically detect these files and copy them to the appropriate locations in the pyIGRF site-packages folder during deployment

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
   - If you're using custom files for pyIGRF:
     - Check that the custom files are correctly named (`custom_loadCoeffs.py` and/or `custom_igrf14coeffs.txt`)
     - Verify that the predeploy script has execute permissions (`chmod +x predeploy.sh`)
     - Check the build logs for any errors related to the predeploy script
     - If the predeploy script fails, you can manually copy the custom files to the pyIGRF site-packages folder after deployment

### Testing the Deployed API

You can test the deployed API using curl or any API client:

```bash
curl -X POST "https://your-service-name.onrender.com/pyigrf" \
  -H "Content-Type: application/json" \
  -d '{"points_json":"{\"points_json\":[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"}]}"}'
```

### Input and Output Formats

#### POST /pyigrf Input Format

The input to the POST /pyigrf endpoint should be a JSON object with a `points_json` field containing a stringified JSON string. The stringified JSON should be an object with a `points_json` field containing an array of points. Each point should be an object with the following fields:

- `latitude`: Latitude in degrees (string)
- `longitude`: Longitude in degrees (string)
- `altitude`: Altitude in kilometers (string)
- `year`: Year (string)

Example input:

```json
{
  "points_json": "{\"points_json\":[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"},{\"latitude\":\"13.9375\",\"longitude\":\"4.1875\",\"altitude\":\"255.7499\",\"year\":\"2024.9\"}]}"
}
```

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
