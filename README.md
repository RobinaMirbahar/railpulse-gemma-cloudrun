# 🚆 RailPulse AI — Building & Deploying Open-Source AI Agents with Gemma and Google Cloud Run (DevFest Baku 2026)

![RailPulse AI Cover](assets/railpulse_cover.jpg)

> **Accepted 45-Minute Hands-On Workshop — DevFest Baku 2026**  
> **Speaker:** [Robina Mirbahar](https://github.com/RobinaMirbahar) (Google Developer Expert in Cloud & AI)  
> **Topic:** Building, containerizing, and deploying a production-ready railway dispatch and tracking AI agent powered by open-weights Gemma, Google ADK, and Google Cloud Run with zero idle costs.

---

## 🎯 Why I Created This Documentation (Purpose & Real-World Value)

Most generative AI tutorials showcase toy chatbots, creative writing prompts, or basic customer service bots. **RailPulse AI addresses a fundamentally different and much higher-stakes engineering challenge: how to build AI agents for safety-critical physical infrastructure.**

Here is why this documentation and architecture are essential:

### 1. 🛡️ Moving Beyond "Toy Demos" to Safety-Critical AI
In passenger rail systems (like Azerbaijan Railways), a single hallucinated route or ignored signal can cause catastrophe. This documentation demonstrates how to wrap open-weights models (Gemma) inside **deterministic, non-negotiable software interlocks** (`guardrails.py`) so physical safety rules always take precedence over AI suggestions.

### 2. 💰 Privacy, Data Sovereignty & $0 Idle Serverless Economics
Many enterprise organizations cannot stream sensitive internal operational telemetry, crew rosters, or signal logs to closed third-party cloud APIs. By using **Gemma open-weights models** hosted on **Google Cloud Run with scale-to-zero (`--min-instances 0`)**, teams retain 100% data privacy and control while paying **$0 when the application is idle**.

### 3. 🧭 Dual-Purpose: Live Presentation Playbook & Self-Paced Blueprint
- **For DevFest Baku 2026 Attendees:** Acts as the live step-by-step companion guide during the 45-minute interactive workshop.
- **For the Open-Source Community:** Serves as a reference implementation demonstrating how to combine **Google Agent Development Kit (ADK)**, **Pydantic v2 structured JSON schemas**, **Streamlit**, and **Cloud Run** in production.

---

## 🌟 Live Interactive Rail Tracking & Smart Dispatch Demo (Baku 2026)

**RailPulse AI** provides a complete, live interactive rail tracking experience built specifically for my hands-on workshop at **DevFest Baku 2026**.

The live demo features a real-time tracking map and operational dashboard modeled after modern railway transit systems across the **Azerbaijan Railways (ADY)** network:
- **Live GPS & Track Telemetry:** Track active passenger trains (*Baku–Ganja High-Speed Express*, *Baku–Sumgayit Absheron Commuter*, *Baku–Tbilisi Silk Road Express*) moving across real coordinates.
- **Dynamic Station Departure Boards:** Live estimated arrival times (ETAs), delay counters, and track assignments.
- **Interactive Weather & Track Simulator:** Attendees can toggle Caspian coastal crosswinds and block occupancies in real time.
- **Autonomous Dispatch Agent:** When disruptions occur, the open-weights **Gemma** agent assesses options and issues collision-free, guardrail-verified rerouting advisories without ever violating physical railway safety interlocks.

---

## 🏗️ Architecture Overview

I designed RailPulse AI with a strict separation between **autonomous LLM reasoning (Gemma + Google ADK)**, **deterministic railway safety interlocks**, and an **interactive trilingual operations frontend**.

```mermaid
flowchart TD
    subgraph UI ["1. Frontend & Telemetry Layer (Streamlit on Google Cloud Run)"]
        UI_Head["Trilingual Switcher [ 🇬🇧 EN | 🇦🇿 AZ | 🇷🇺 RU ]"]
        UI_KPI["Top Telemetry Strip (Active Train, Clamped Speed, Block, ETA)"]
        UI_Timeline["Station Progression Timeline (Pulsing Live Active Node)"]
        UI_Sim["Live Corridor Simulator (Caspian Crosswinds & Block Status Injector)"]
        UI_Chat["💬 Gemma Rail Assistant (Real-Time Passenger & Dispatch Q&A)"]
        UI_Announce["📢 Passenger Station Audio Board (ADY Audio Synthesizer)"]
        UI_Map["🗺️ Interactive Azerbaijan Transit Map (OpenStreetMap & Running Trains)"]
        UI_Table["📊 Fleet Clearance & Telemetry Table"]
    end

    subgraph Agent ["2. Agent Core (Google ADK + Gemma Open-Weights)"]
        A_Agent["Google ADK Dispatch Agent (railpulse_agent/agent.py)"]
        A_Chat["Gemma Rail Assistant Engine (railpulse_agent/chat.py)"]
        A_Tools{"ADK Registered Tools"}
        A_T1["get_live_train_telemetry()"]
        A_T2["check_corridor_signals_and_wind()"]
        A_T3["calculate_schedule_recovery()"]
    end

    subgraph Safety ["3. Deterministic Safety Interlocks (Rule-Based Hardening)"]
        S_Audit["Safety Audit Engine (railpulse_agent/guardrails.py)"]
        S_Wind{"Caspian Wind > 65 km/h?"}
        S_Clamp["Deterministic Speed Clamping (<= 80 km/h)"]
        S_Block{"Primary Block Occupied / Maint?"}
        S_Divert["Automatic Divert to Siding Passing Loop"]
        S_Schema["Pydantic v2 Schema Enforcement (RailDispatchAdvisory)"]
    end

    subgraph Cloud ["4. Serverless Google Cloud Infrastructure"]
        CR["Google Cloud Run (europe-west1 / us-central1)"]
        CR_Container["Containerized Streamlit App (Dockerfile)"]
        CR_Scale["Scale-to-Zero (0 idle instances = $0.00 cost)"]
        CR_Auth["Allow Unauthenticated / IAM Secured"]
    end

    UI_Sim -->|Live Simulation Events| A_Agent
    UI_Chat -->|Passenger & Dispatch Inquiries| A_Chat
    A_Chat -->|Live Fleet & Weather Context| A_Tools
    A_Agent --> A_Tools
    A_Tools --> A_T1
    A_Tools --> A_T2
    A_Tools --> A_T3
    A_Tools --> S_Audit
    S_Audit --> S_Wind
    S_Wind -->|Yes| S_Clamp
    S_Audit --> S_Block
    S_Block -->|Yes| S_Divert
    S_Audit --> S_Schema
    S_Schema --> UI_Announce
    S_Schema --> UI_KPI
    S_Schema --> UI_Timeline
    UI --> CR_Container
    CR_Container --> CR
    CR --> CR_Scale
```

### 🧩 Key Architectural Subsystems

| Subsystem | File Location | Responsibility |
| :--- | :--- | :--- |
| **Gemma Rail Assistant** | [`railpulse_agent/chat.py`](railpulse_agent/chat.py) | Real-time passenger Q&A, airport-to-hotel transit guidance, ticket rules, station amenities, and corridor operations in English, Azerbaijani, and Russian. |
| **Google ADK Agent Pipeline** | [`railpulse_agent/agent.py`](railpulse_agent/agent.py) | Orchestrates Gemma tool invocation, ordered trajectory execution, and dispatch advisory synthesis. |
| **Railway Telemetry Tools** | [`railpulse_agent/tools.py`](railpulse_agent/tools.py) | Live state of ADY trains (`ADY-104`, `ADY-702`, `ADY-410`), Caspian wind sensors, and track block signals. |
| **Deterministic Guardrails** | [`railpulse_agent/guardrails.py`](railpulse_agent/guardrails.py) | Non-negotiable physical constraints: clamping speeds during high crosswinds and forcing train diversion into passing sidings when blocks are blocked. |
| **Structured Output Schema** | [`railpulse_agent/schema.py`](railpulse_agent/schema.py) | Strict Pydantic v2 model (`RailDispatchAdvisory`) guaranteeing validated JSON output. |
| **Interactive Operations UI** | [`app.py`](app.py) | Streamlit dashboard with full-width KPI cards, station timeline, Leaflet running map, simulator controls, and audio board. |
| **Serverless Containerization** | [`Dockerfile`](Dockerfile), [`deploy/`](deploy/) | Docker packaging with Cloud Run deployment scripts for scale-to-zero serverless hosting. |

---

## ⏱️ 45-Minute Hands-On Workshop Lab Guide (Step-by-Step for Students)

I designed every step with four clear answers:
1. **📌 What is this step?**
2. **❓ Why is this used?**
3. **🔗 How does this connect to the complete system?**
4. **💻 What commands to run & what you see on screen.**

![45-Minute Workshop Steps Flow](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/workshop_steps_roadmap.png)

---

### ❓ Where Does This Code Come From? (How I Architected This Workshop)

> [!NOTE]
> **For Workshop Students & Beginners:**  
> In this 45-minute workshop, **you do not need to write thousands of lines of code from scratch**.  
> - **The Code is Already Pre-Built:** All components (Gemma agent, safety interlocks, Streamlit UI, Dockerfile) were pre-engineered and published in this repository ([`RobinaMirbahar/railpulse-gemma-cloudrun`](https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun)).
> - **Cloud Shell Clones (Extracts) It:** When you click the 1-click launch button in Step 1, Google Cloud Shell automatically downloads (clones) this complete codebase into your session.
> - **`pip install` Downloads Libraries:** Running `pip install -r requirements.txt` downloads the official Python runtime packages (`google-adk`, `streamlit`, `pydantic`) from PyPI directly into your virtual environment so everything runs immediately.

---

### 📍 Step 1: Google Cloud Shell Environment Setup (00:00 – 05:00)

- **📌 What is this step?** Launching a browser-based Linux developer environment provided by Google Cloud and downloading the RailPulse AI code.
- **❓ Why is this used?** Attendees have different laptops (Windows, macOS, Linux, Chromebooks) with different software versions. Google Cloud Shell provides a 100% free, identical Linux machine in your browser with `gcloud`, Python 3.11, and Docker pre-installed—so nobody has to troubleshoot local setup errors.
- **🔗 How does this connect?** This creates the clean workspace where you will inspect Gemma's tools (Step 2), test safety rules (Step 3), launch the web UI (Step 4), and deploy the container (Step 5).

#### 💻 Actions:

[![Open in Google Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun.git)

1. Click the blue **Open in Google Cloud Shell** button above.
2. When the **Open in Cloud Shell** confirmation dialog appears:
   - Check the box **☑️ Trust repo**
   - Click **Confirm**

<br>

> 📸 **[Console Screenshot: Step 1.1 — Trust Repo & Confirm]**

![Step 1.1: Trust Repo and Confirm Dialog](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/01_activate_cloud_shell.png)

<br>

3. When the **Authorize Cloud Shell** popup appears:
   - Click **Authorize** to allow Cloud Shell to use your credentials for Google Cloud commands.

<br>

> 📸 **[Console Screenshot: Step 1.2 — Authorize Cloud Shell]**

![Step 1.2: Authorize Cloud Shell Dialog](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/02_gcloud_auth_list.png)

<br>

4. Verify your active project in the terminal:
```bash
gcloud auth list
gcloud config set project $(gcloud config get-value project)
```

3. Clone and enter the repository:
```bash
git clone https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun.git
cd railpulse-gemma-cloudrun
```

![Step 3: Clone RailPulse AI repository](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/03_git_clone_railpulse.png)

4. Create and activate a Python virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

<br>

> 📸 **[Console Screenshot: Virtual Environment Creation & Dependency Installation]**

![Step 1.4: Virtual Environment & Pip Install](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/03_pip_install_venv.png)

<br>

> 📸 **[Console Screenshot: Step 1.5 — Dependencies Successfully Installed & Ready]**

![Step 1.5: Dependencies Successfully Installed](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/03_pip_install_success.png)

<br>

> 💡 **Why create a Virtual Environment (`.venv`)?**
>
> 1. **Dependency Isolation:** Google Cloud Shell comes with many system-wide Linux packages. Creating `.venv` creates an isolated sandbox for RailPulse AI's libraries (`google-adk`, `streamlit`, `pydantic`), preventing version conflicts with the underlying operating system.
> 2. **Clean Container Parity:** What runs inside `.venv` matches the exact dependencies packaged into the Google Cloud Run Docker container in Step 5, eliminating "works on my machine" deployment bugs.
> 3. **Permission Safety:** It allows packages to be installed cleanly in user space without requiring `sudo` or altering system-level Linux binaries.

---

### 📍 Step 2: Equipping Gemma with Live Railway Telemetry Tools (05:00 – 15:00)

- **📌 What is this step?** Giving Google's open-weights Gemma model access to live Python functions that read train speeds, GPS coordinates, block signals, and weather.
- **❓ Why is this used?** An AI language model on its own only knows text; it has zero real-time awareness of where trains are. Just like live railway transit maps connect to GPS signals to display real-time positions, the Gemma agent uses **Function Calling** to inspect live sensors before generating any dispatch decision.
- **🔗 What is the link?** Takes the environment prepared in **Step 1** and gives Gemma the live data it needs so that **Step 3** can evaluate whether those conditions are physically safe.

#### 💻 How It Works (`railpulse_agent/tools.py`):
- `get_live_train_telemetry(train_id)`: Queries live train speed (`km/h`), delay (`minutes`), and track block (e.g. *Baku–Ganja Express* `ADY-EXP-101`).
- `check_corridor_signals_and_wind(corridor_id)`: Checks whether downstream track blocks are `FREE` or `OCCUPIED` and checks Caspian coastal crosswinds.
- `calculate_schedule_recovery(train_id, target_speed_kmh, use_passing_siding)`: Calculates timetable adjustments and headway recovery.

Run the terminal demonstration to see Gemma calling these tools:
```bash
python scripts/run_demo.py
```

<br>

> 📸 **[Console Screenshot: Step 2 — Gemma Function Calling & Dispatch Execution Output]**

![Step 2: Run CLI Demo in Cloud Shell Terminal](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/04_run_demo_terminal.png)

<br>

> 📸 **[Console Screenshot: Structured JSON Output & All 3 ADY Corridors Verified]**

![Step 2.2: Validated JSON Dispatch Advisory](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/04_run_demo_json_output.png)

<br>

---

### 📍 Step 3: Enforcing Deterministic Safety Guardrails & Schemas (15:00 – 25:00)

- **📌 What is this step?** Wrapping Gemma's output in non-negotiable software interlocks (`guardrails.py`) and a strict JSON data schema (`schemas.py`).
- **❓ Why is this used?** In mission-critical railway operations, an AI hallucination could cause a collision or derailment. A language model must **never** have the final say on physical safety. If a track is blocked, a software guardrail must *physically force* a diversion regardless of what the LLM generated.
- **🔗 What is the link?** Protects the telemetry gathered in **Step 2** from hallucinations and outputs a strictly verified `RailDispatchAdvisory` JSON object that **Step 4** can safely render on a visual map.

#### 🛡️ The Two Non-Negotiable Safety Rules:
1. **Block Collision Interlock:** If the main line block is `OCCUPIED`, the agent strictly overrides any forward clearance and diverts the train into a verified `FREE` passing loop siding (`BLK-BILAJARI-SIDING-S1`).
2. **Caspian Wind Speed Cap:** If crosswinds off the Caspian Sea exceed `65 km/h`, the speed advisory is capped to `<= 80 km/h` to prevent aerodynamic instability.

Run the automated test suite to verify the guardrails block hallucinations:
```bash
python -m pytest tests/test_railpulse.py -v
```

<br>

> 💡 **Troubleshooting Tip: `ModuleNotFoundError: No module named 'railpulse_agent'`**  
> If students run standalone `pytest` instead of `python -m pytest`, Linux may not automatically include the current working directory in Python's module path (`sys.path`), producing this error:

<br>

![Step 3 Troubleshooting: ModuleNotFoundError](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_pytest_import_error_solution.png)

<br>

> **How to Solve:** Simply execute with `python -m pytest tests/test_railpulse.py -v` (or run `PYTHONPATH=. pytest`), which ensures the root directory is recognized by Python's module resolver.

<br>

![Step 3: All 4 Safety Guardrail Tests Passing](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_pytest_all_passed.png)

<br>

---

### 📍 Step 4: Launching the Interactive Web Rail Tracker & Simulator (25:00 – 35:00)

- **📌 What is this step?** Launching an interactive Streamlit web dashboard in Cloud Shell that displays train positions on a map, live departure boards, and a 1-click **Caspian Wind & Block Occupancy Simulator**.
- **❓ Why is this used?** Train dispatchers and station masters cannot operate by reading raw command-line JSON. They need an interactive visual interface to see where trains are, test scenarios, and review the AI agent's recommendations in human-friendly format.
- **🔗 What is the link?** Connects the verified backend agent from **Steps 2 & 3** to a user-friendly frontend that students can click and explore before deploying to production in **Step 5**.

#### 💻 Actions:

Start the Streamlit application on port 8080 (with CORS & XSRF disabled for Cloud Shell proxy routing):
```bash
streamlit run app.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
```

<br>

![Step 4: Streamlit Server Running on Port 8080](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_server_started.png)

<br>

#### 🌐 Opening the Live Dashboard:
1. In the top-right toolbar of Google Cloud Shell, click the **Web Preview** icon (the small window/eye icon next to the blue terminal icon).
2. Select **Change port > 8080 > Preview and Run** (or click **Preview on port 8080**).
<br>

> 🔄 **How to Pull Code Updates During the Workshop:**  
> Whenever new features, prompt templates, or UI fixes are pushed to the GitHub repository, attendees do not need to re-clone the repository or recreate their virtual environment! Simply update the running Cloud Shell workspace with these quick steps:  
>  
> 1. In your Cloud Shell terminal, press **`Ctrl + C`** to stop the current Streamlit process.  
> 2. Fetch the latest code from GitHub:  
>    ```bash  
>    git pull origin main  
>    ```  
> 3. Restart the interactive server with Cloud Shell reverse-proxy routing permitted:  
>    ```bash  
>    streamlit run app.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false  
>    ```  
> 4. Refresh your **Web Preview** browser tab (`F5`) to immediately see the changes!

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_git_pull_cloudshell_update.png" width="48%" alt="Live Git Pull in Cloud Shell" />
  &nbsp;
  <img src="https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_restart_command.png" width="48%" alt="Streamlit Server Restart Command" />
</p>

<br>

![Step 4: Interactive Trilingual RailPulse AI Dashboard](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_trilingual_dashboard.png)

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_kpi_corridor_view.png" width="48%" alt="Updated Balanced KPI Strip and Corridors" />
  &nbsp;
  <img src="https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_azerbaijan_running_map.png" width="48%" alt="Highlighted Azerbaijan Map with Live Running Trains" />
</p>

<br>


<br>



![Step 4: RailPulse AI Telemetry Metrics](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_railpulse_dashboard.png)

<br>

![Step 4: Live GIS Map, Station Board Announcement, and ADK Guardrail Audit](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_map_and_audit.png)

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_train_selector.png" width="48%" alt="ADY Train Fleet Selector" />
  &nbsp;
  <img src="https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_block_occupancy_selector.png" width="48%" alt="Track Block Occupancy Selector" />
</p>

<br>

<br>

> 💡 **Troubleshooting Tip: `Rejecting WebSocket connection with disallowed Origin or Host header`**  
> If you see repeated warning logs like:  
> `Rejecting WebSocket connection with disallowed Origin or Host header: origin https://8080-cs-...cloudshell.dev, host localhost:8080`  
> this happens because Google Cloud Shell serves Web Preview through a secure proxy (`cloudshell.dev`), whereas Streamlit defaults to strictly expecting `localhost:8080`.

<br>

![Step 4 Troubleshooting: Streamlit WebSocket CORS Disallowed Origin](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/05_streamlit_websocket_cors_fix.png)

<br>

> **How to Solve:**  
> 1. Press `Ctrl + C` in your Cloud Shell terminal to stop the process.  
> 2. Restart with the CORS flags explicitly disabled:  
>    ```bash
>    streamlit run app.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
>    ```  
>    *(I have also added `.streamlit/config.toml` in the repository so a simple `git pull` configures this automatically!)*  
> 3. Refresh your **Web Preview** browser tab.

<br>

#### 🧪 Try This in the Dashboard:

* **Ask Gemma Live Departures & Schedules:** Type in the new **Gemma Rail Assistant Chat** (e.g. *"When is the next train to Sumgayit?"*, *"Show all departures"*, *"Is Baku-Ganja on time?"*) to get instant real-time ETAs and availability.
* **Test High Winds:** Slide the Caspian Wind speed slider to `78 km/h`. Watch the deterministic guardrail automatically engage the `80 km/h` safety limit.
* **Test Track Blockage:** Toggle Primary Block status to `OCCUPIED`. Watch the agent automatically reroute the train into the safe passing siding loop.
* **Test Trilingual Voice & Chat:** Tap **`AZ`** or **`RU`** at the top right to switch the entire dashboard, chat answers, and station announcements into Azerbaijani or Russian in real time.

---

### 📍 Step 5: Deploying to Google Cloud Run with Scale-to-Zero (35:00 – 45:00)

- **📌 What is this step?** Packaging the entire application into a Docker container and deploying it as a production serverless web service on Google Cloud Run.
- **❓ Why is this used?** Inside Cloud Shell, the app only runs while your browser tab is open. Cloud Run gives you a permanent, secure `https://...run.app` URL accessible from anywhere in the world. With `--min-instances 0`, Cloud Run automatically scales to zero instances when idle—meaning **students pay $0** after the workshop ends.
- **🔗 How does this connect?** Takes everything built in **Steps 1 through 4** (Gemma + Google ADK + Safety Guardrails + Streamlit UI) and turns it into a live public product for your portfolio or resume.

#### 💻 Actions:

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run/?git_repo=https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun.git)

1. Click the **Run on Google Cloud** button above, or run the automated script in your Cloud Shell terminal:
```bash
chmod +x deploy/deploy_cloud_run.sh
./deploy/deploy_cloud_run.sh
```

Or deploy directly via `gcloud`:
```bash
gcloud run deploy railpulse-gemma   --source .   --region europe-west1   --allow-unauthenticated   --memory 2Gi   --cpu 2   --min-instances 0   --max-instances 5
```

<br>

> 📸 **[Your Console Screenshot Here]**  
> *Capture your Google Cloud Shell terminal showing the Cloud Run deployment success, 100% traffic serving, and the active `https://...run.app` service URL.*

![Step 6: Google Cloud Run Deployment Success](https://raw.githubusercontent.com/RobinaMirbahar/railpulse-gemma-cloudrun/main/assets/screenshots/06_cloud_run_deploy_success.png)

<br>

2. Open the printed **Service URL** in your browser:
```text
https://railpulse-gemma-xxxxxxxxxx-ew.a.run.app
```
Congratulations! You have built, verified, and deployed an open-source AI agent powered by Gemma on Google Cloud! 🎉


## 📁 Repository Structure

```text
railpulse-gemma-cloudrun/
├── app.py                      # Interactive Streamlit live rail tracking UI & simulator
├── Dockerfile                  # Container definition for Google Cloud Run
├── requirements.txt            # Python dependencies (streamlit, pydantic, google-genai)
├── pyproject.toml              # Build & test configuration
├── deploy/
│   └── deploy_cloud_run.sh     # One-click Cloud Run deployment script
├── railpulse_agent/
│   ├── __init__.py
│   ├── agent.py                # Google ADK agent orchestrator
│   ├── guardrails.py           # Deterministic railway safety interlocks
│   ├── schemas.py              # Pydantic v2 structured JSON advisory models
│   └── tools.py                # Telemetry, signal & timetable recovery tools
├── scripts/
│   └── run_demo.py             # CLI demonstration runner for terminal walkthroughs
├── tests/
│   └── test_railpulse.py       # Unit tests for tools, interlocks & schemas
└── assets/
    ├── railpulse_cover.jpg
    ├── railpulse_architecture.jpg
    └── screenshots/            # Step-by-step workshop screenshots (1 to 6)
```

<!-- AUTHOR_SIGNATURE_START -->
---

## 👩‍💻 About the Author

**Robina Mirbahar — Google Cloud & AI Architect**  
*Google Developer Expert (GDE) in Cloud & AI • Published Author • Multi-Agent Systems & Serverless GPU Builder*

[![GitHub](https://img.shields.io/badge/GitHub-RobinaMirbahar-181717?style=for-the-badge&logo=github)](https://github.com/RobinaMirbahar)
[![Medium](https://img.shields.io/badge/Medium-@robinamirbahar-000000?style=for-the-badge&logo=medium)](https://medium.com/@robinamirbahar)
[![DEV.to](https://img.shields.io/badge/DEV.to-robinamirbahar-0A0A0A?style=for-the-badge&logo=devdotto)](https://dev.to/robinamirbahar)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Robina_Mirbahar-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/robina-mirbahar)
[![GDE Profile](https://img.shields.io/badge/Google_Developer_Expert-Profile-4285F4?style=for-the-badge&logo=google)](https://g.dev/RobinaMirbahar)
[![YouTube](https://img.shields.io/badge/YouTube-@RobinaMirbahar-FF0000?style=for-the-badge&logo=youtube)](https://www.youtube.com/@RobinaMirbahar)
[![X](https://img.shields.io/badge/X-@RobinaMirbahar-000000?style=for-the-badge&logo=x)](https://x.com/RobinaMirbahar)
[![Amazon Author](https://img.shields.io/badge/Amazon_Book-Cloud_Computing_Voyage-FF9900?style=for-the-badge&logo=amazon)](https://www.amazon.com/dp/B0D146249R)

<!-- AUTHOR_SIGNATURE_END -->
