# Mini Device Fleet Monitor

## 1. What the project does
This is a lightweight API application that monitors a fleet of simulated devices. It allows devices to register themselves and send periodic heartbeats. The core feature is that any device that has not sent a heartbeat within the last **30 seconds** is automatically flagged as **OFFLINE**. 

## 2. Design / Architecture
The project is built using **Python** and **FastAPI**. It is divided into three layers to ensure separation of concerns:
* **Models (src/models.py)**: Pydantic models for strict request validation and schema definition.
* **Storage (src/store.py)**: A thread-safe, in-memory data store using Python 	hreading.Lock. This prevents race conditions when hundreds of devices ping the API simultaneously. The 30-second logic is computed dynamically upon read requests.
* **API (src/api.py & src/main.py)**: FastAPI REST controllers routing HTTP requests to the storage layer.

## 3. Prerequisites
* Python 3.9 or higher
* Git

## 4. How to build the application
Clone the repository and set up a virtual environment:
`ash
git clone https://github.com/choudharyamitkumar39/Project.git
cd Project
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
`

## 5. How to run the application
Start the FastAPI server using Uvicorn:
`ash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
`
*The API documentation will be automatically available at http://localhost:8000/docs*

## 6. How to run the simulator
In a **new terminal window** (with the virtual environment activated), run:
`ash
python simulator/sim.py
`
This script simulates 5 devices pinging the API every 5 seconds. device-05 is specifically programmed to stop sending heartbeats after 20 seconds, allowing you to observe its status switch from ONLINE to OFFLINE.

## 7. How to run the tests
The project includes a suite of automated unit/integration tests using pytest.
Run them via:
`ash
pytest tests/
`

## 8. Example API requests

**Register a device:**
`ash
curl -X POST http://localhost:8000/devices \
     -H "Content-Type: application/json" \
     -d '{"id": "dev-99", "name": "Lab Device 99"}'
`

**Send a heartbeat:**
`ash
curl -X POST http://localhost:8000/devices/dev-99/heartbeat \
     -H "Content-Type: application/json" \
     -d '{"timestamp": "2026-09-24T10:30:00Z", "status": "OK", "cpu_usage": 45.2}'
`

**Get fleet summary:**
`ash
curl http://localhost:8000/summary
`

## 9. Assumptions Made
* **Device Registration First**: Devices must be registered via POST /devices before they can send a heartbeat.
* **UTC Timestamps**: Clients send timestamps in ISO 8601 format. The server normalizes all naive datetimes to UTC.
* **Ephemeral Data**: Data is stored in memory to meet the 3-hour constraint elegantly. It resets on application restart.

## 10. Known Limitations
* **Scalability**: Because the store is in-memory and uses 	hreading.Lock, the application cannot be horizontally scaled across multiple worker processes (e.g., gunicorn workers) without losing state synchronization.
* **Security**: No authentication or API keys are implemented for devices.

## 11. Future Improvements (With 1 Additional Day)
* **Persistent Storage**: Swap the in-memory store for a PostgreSQL or SQLite database using an ORM like SQLAlchemy.
* **Dockerization**: Add a Dockerfile and docker-compose.yml for zero-setup deployments.
* **Asynchronous Storage**: Make the store layer strictly async (e.g., using Redis) for much higher throughput.

---

## AI Usage
* **Which AI tools used**: Google Gemini / Antigravity Agent.
* **What it was used for**: Generating the boilerplate FastAPI scaffolding, generating the HTTP client requests for the simulator, drafting the pytest test suite, and scaffolding this README.
* **Code Changed/Rejected**: The AI initially suggested checking the 30-second timeout via a background cron-job that periodically sweeps and updates statuses. I rejected this and changed it to evaluate the timeout *dynamically* at read-time (e.g., when GET /devices is called) to avoid unnecessary CPU cycles and synchronization bugs. Furthermore, I enforced adding timezone awareness (	zinfo=timezone.utc) to naive datetime objects provided by the AI.
* **Personally Verified**: I personally verified the thread-safety locks in store.py to ensure concurrent heartbeats do not corrupt the device dictionary, and verified that all 5 pytest tests pass successfully in a clean environment.

