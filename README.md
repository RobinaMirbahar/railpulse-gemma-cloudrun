# 🚆 RailPulse AI — Building & Deploying Open-Source AI Agents with Gemma and Google Cloud Run (DevFest Baku 2026)

![RailPulse AI Cover](assets/railpulse_cover.jpg)

> **Accepted 45-Minute Hands-On Workshop — DevFest Baku 2026**
>
> Build, containerize, and deploy a real-time **Rail Tracking & Smart Dispatch AI Agent (`RailPulse AI`)** powered by **open-weights Gemma**, **Google Agent Development Kit (ADK)**, **Streamlit**, and **Google Cloud Run (scale-to-zero)**.

---

## 🏗️ Architecture Overview

![RailPulse AI Architecture](assets/railpulse_architecture.jpg)

1. **Interactive Streamlit Rail Tracker (`app.py`):** Visualizes active trains across **Azerbaijan Railways (ADY)** corridors (*Baku–Ganja High-Speed Express*, *Baku–Sumgayit Absheron Commuter*, *Baku–Tbilisi Silk Road Express*), includes a 1-click **Caspian Wind & Block Occupancy Simulator**, and renders live station departure boards.
2. **Lightweight Gemma Inference Engine (`Ollama` on Cloud Run):** Runs open-weights Gemma (`gemma3:4b` / `gemma4:e4b`) serverlessly with `--min-instances=0` so idle cost is `$0`.
3. **Python Function Calling (`railpulse_agent/tools.py`):**
   - `get_live_train_telemetry(train_id)` — Live GPS, speed (`km/h`), delay (`minutes`), and active track block.
   - `check_corridor_signals_and_wind(corridor_id)` — Track block occupancy (`FREE`, `OCCUPIED`, `MAINTENANCE`) and live Caspian wind speeds.
   - `calculate_schedule_recovery(train_id, target_speed_kmh, use_passing_siding)` — Deterministic ETA and headway recovery calculator.
4. **Deterministic Railway Interlock Guardrail (`railpulse_agent/guardrails.py`):**
   - **Block Occupancy Interlock:** Prevents routing a train into an `OCCUPIED` primary block and automatically switches onto a verified `FREE` passing loop siding (`BLK-BILAJARI-SIDING-S1`).
   - **Caspian High-Wind Speed Cap:** Clamps train speed to `<= 80 km/h` whenever crosswinds exceed `65 km/h`.
5. **Structured JSON Outputs (`railpulse_agent/schemas.py`):** Enforces a strict Pydantic v2 `output_schema` (`RailDispatchAdvisory`) on the ADK `LlmAgent`.

---

## 🚀 Quickstart (Google Cloud Shell — Zero Local Install)

```bash
git clone https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun.git
cd railpulse-gemma-cloudrun

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1. Run CLI verification & unit tests
python scripts/run_demo.py
pytest -v

# 2. Launch Interactive Streamlit Rail Tracker (Cloud Shell Web Preview on port 8080)
streamlit run app.py --server.port=8080 --server.address=0.0.0.0
```

---

## ☁️ Deploy to Google Cloud Run (Scale-to-Zero)

```bash
chmod +x deploy/deploy_cloud_run.sh
./deploy/deploy_cloud_run.sh
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

---

## Star, Fork & Sponsor This Project

[![Star on GitHub](https://img.shields.io/github/stars/RobinaMirbahar/railpulse-gemma-cloudrun?style=for-the-badge&logo=github&label=Star)](https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun)
[![Fork on GitHub](https://img.shields.io/github/forks/RobinaMirbahar/railpulse-gemma-cloudrun?style=for-the-badge&logo=github&label=Fork)](https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun/fork)
[![Sponsor RobinaMirbahar](https://img.shields.io/badge/Sponsor-%40RobinaMirbahar-ea4aaa?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/RobinaMirbahar)

If this project is helpful to your work:
* **Star this Repository:** [**Star `RobinaMirbahar/railpulse-gemma-cloudrun` on GitHub**](https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun) to bookmark it and help others discover it.
* **Fork & Customize:** [**Fork `RobinaMirbahar/railpulse-gemma-cloudrun`**](https://github.com/RobinaMirbahar/railpulse-gemma-cloudrun/fork) to build and experiment with your own workflows.
* **Sponsor on GitHub:** [**Sponsor `@RobinaMirbahar` on GitHub Sponsors (`github.com/sponsors/RobinaMirbahar`)**](https://github.com/sponsors/RobinaMirbahar) to support open-source AI, Google Cloud, and Gemini engineering projects!

