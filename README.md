# Description

This project provides a simple API service with three endpoints. It requires **minikube**, **docker**, **kubectl**, and **helm** for deployment.

## Deployment

```bash
cd deployment
./deploy_all.sh
```

Once deployed, the script will return a service URL. To access the interactive Swagger documentation, append `/docs` to the returned URL.

Example:

```
http://<service-url>/docs
```

⚠️ **Important:** Wait for the **worker chart** to be fully deployed before submitting a new job.
* **Note:** The worker takes a couple of minutes during the **first run** to initialize the data.

## API Endpoints

### 1. **Submit a Job**

* **Endpoint:** `/submit`
* **Method:** `POST`
* **Request Body:**

  ```json
  {
    "fasta": "fasta value"
  }
  ```
* **Description:** Submits a new **MMseqs2 search job** for processing.


### 2. **Check Job Status**

* **Endpoint:** `/status/{job_id}`
* **Method:** `GET`
* **Description:** Retrieves the current status of a job.
* **Possible Status Values:**

  * `QUEUED`
  * `RUNNING`
  * `FINISHED`

### 3. **Get Job Results**

* **Endpoint:** `/results/{job_id}`
* **Method:** `GET`
* **Description:** Retrieves the results of a job **once it is FINISHED**.

### Authors(sorted by first name)

* Aurélien Luciani
* Daniel Rice
* Minjoon Kim
* Shadab Ahmad
* Simone Weyand
* Supun Wijerathne
* Swaathi Kandasaamy
* Szymon Szyszkowski