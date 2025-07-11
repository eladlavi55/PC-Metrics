# PC MetricsX - Real-Time Gaming PC Monitoring Dashboard with AWS

This project is a real-time dashboard for monitoring your gaming PC's key components like CPU, GPU, SSD, and motherboard. It shows live temperatures, fan speeds, and even uses AI to suggest the best fan curves for your setup. You can also connect it to AWS IoT for cloud features, but it works fine locally too.

Demo Video: youtu.be/t5dDW7nQ_fE
 
Main Features
- Live monitoring of PC hardware (CPU, GPU, SSD, motherboard)
- Real-time dashboard with charts and stats
- AI-powered fan curve recommendations (Claude AI)
- Optional AWS IoT integration
- Simulated sensor data for easy testing

## How to Run
1. **Generate sensor data:**
   - Run the simulation script:
     ```
     python simulate_pc_metrics.py
     ```
   - This will create a file called `sensor_data_log.json` with fake PC data.

2. **Start the dashboard:**
   - Launch the dashboard with:
     ```
     python start_dashboard.py
     ```
   - Open your browser and go to [http://localhost:5000](http://localhost:5000)

3. **(Optional) AWS IoT:**
   - If you want to use AWS IoT, put your certificates in the `certificates/` folder and update `config.py`.

## Important Files
- `app.py` - Main dashboard backend
- `simulate_pc_metrics.py` - Generates sensor data
- `start_dashboard.py` - Launches the dashboard
- `config.py` - Configuration for simulation and AWS
- `claude_ai.py` - Handles AI recommendations
- `templates/dashboard.html` - Dashboard UI
- `sensor_data_log.json` - Stores sensor data
