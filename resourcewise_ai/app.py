import json
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="ResourceWise AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Persistent storage helpers ----------
def load_records(filename, default=None):
    path = DATA_DIR / filename
    if not path.exists():
        return [] if default is None else default
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return [] if default is None else default

def save_records(filename, records):
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

def log_event(category, event, details):
    events = load_records("events.json")
    events.insert(0, {
        "time": datetime.now().isoformat(timespec="seconds"),
        "category": category,
        "event": event,
        "details": details,
    })
    save_records("events.json", events[:500])

# ---------- White and blue theme ----------
st.markdown("""
<style>
:root { color-scheme: light; }
.stApp { background: #ffffff; color: #172b4d; }
[data-testid="stSidebar"] { background: #eff6ff; border-right: 1px solid #dbeafe; }
[data-testid="stSidebar"] * { color: #173b70; }
h1, h2, h3 { color: #173b70 !important; }
p, label, .stMarkdown, [data-testid="stMetricLabel"] { color: #243b5a; }
[data-testid="stMetric"] {
  background: #f5f9ff; border: 1px solid #dbeafe;
  padding: 16px; border-radius: 12px;
}
.stButton > button, .stDownloadButton > button {
  background: #2563eb; color: white; border: 1px solid #2563eb;
  border-radius: 9px; font-weight: 600;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: #1d4ed8; color: white; border-color: #1d4ed8;
}
div[data-baseweb="tab-list"] { gap: 8px; }
div[data-baseweb="tab"] { background: #eff6ff; border-radius: 8px 8px 0 0; }
hr { border-color: #dbeafe; }
.resource-card {
  background: #f5f9ff; border: 1px solid #dbeafe;
  border-radius: 14px; padding: 18px; min-height: 125px;
}
.muted { color: #60738f; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar navigation ----------
with st.sidebar:
    st.markdown("## ♻️ ResourceWise AI")
    st.caption("Smart resource waste management")
    page = st.radio(
        "Navigation",
        ["Overview", "💧 Water", "⚡ Electricity", "📄 Paper", "📊 Reports"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("White + blue interface")
    st.caption("Demo software — no physical equipment is controlled.")

st.title("ResourceWise AI")
st.caption("AI-powered resource waste detection and management")
st.markdown(
    "Monitor water, electricity, and paper in one place. Use the sidebar to open each section."
)

# ---------- Overview ----------
if page == "Overview":
    water_events = load_records("water_events.json")
    electricity_records = load_records("electricity_records.json")
    paper_requests = load_records("paper_requests.json")
    recycling_records = load_records("recycling_records.json")
    total_recycled = sum(float(item.get("kilograms", 0)) for item in recycling_records)
    possible_alerts = sum(1 for item in water_events if item.get("alert")) + sum(
        1 for item in electricity_records if item.get("low_occupancy")
    )

    a, b, c, d = st.columns(4)
    a.metric("Water events", len(water_events))
    b.metric("Electricity scans", len(electricity_records))
    c.metric("Paper requests", len(paper_requests))
    d.metric("Paper recycled", f"{total_recycled:.1f} kg")

    st.subheader("Your resource sections")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="resource-card"><h3>💧 Water</h3><p>Simulate occupancy and flow readings, flag possible water waste, and save event records.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="resource-card"><h3>⚡ Electricity</h3><p>Capture or upload a room image and use an object-detection model to count people.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="resource-card"><h3>📄 Paper</h3><p>Record print requests, review request status, and track recycling entries.</p></div>', unsafe_allow_html=True)

    st.subheader("Recent activity")
    events = load_records("events.json")
    if events:
        st.dataframe(pd.DataFrame(events[:10]), use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet. Start in Water, Electricity, or Paper.")

# ---------- Water ----------
elif page == "💧 Water":
    st.header("💧 SmartWash — Water Management")
    st.caption("Occupancy and flow simulator. Readings are simulated, not connected to real sensors or valves.")

    if "water_people" not in st.session_state:
        st.session_state.water_people = 0
    if "water_flow" not in st.session_state:
        st.session_state.water_flow = 0.0
    if "water_extra_used" not in st.session_state:
        st.session_state.water_extra_used = 0.0

    with st.expander("Simulation settings", expanded=False):
        baseline = st.number_input("Baseline water use (litres per period)", min_value=0.0, value=20.0, step=1.0)
        reduction = st.slider("Assumed reduction from avoided waste (%)", 0, 80, 25)
        tariff = st.number_input("Water cost (₹ per 1,000 litres)", min_value=0.0, value=50.0, step=5.0)

    used = max(0.0, baseline * (1 - reduction / 100)) + st.session_state.water_extra_used
    saved = max(0.0, baseline - used)
    cost_saved = saved * tariff / 1000

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated water used", f"{used:.1f} L")
    m2.metric("Estimated saved", f"{saved:.1f} L")
    m3.metric("People inside", st.session_state.water_people)
    m4.metric("Flow rate", f"{st.session_state.water_flow:.1f} L/min")

    left, right = st.columns(2)
    with left:
        st.subheader("Occupancy simulator")
        st.markdown(f"### People currently inside: {st.session_state.water_people}")
        x, y, z = st.columns(3)
        if x.button("＋ Person enters", use_container_width=True):
            st.session_state.water_people += 1
            log_event("Water", "Occupancy updated", f'{st.session_state.water_people} person(s) inside')
            st.rerun()
        if y.button("－ Person exits", use_container_width=True):
            if st.session_state.water_people > 0:
                st.session_state.water_people -= 1
                log_event("Water", "Occupancy updated", f'{st.session_state.water_people} person(s) inside')
                st.rerun()
            else:
                st.warning("Occupancy is already zero.")
        if z.button("Reset", use_container_width=True):
            st.session_state.water_people = 0
            log_event("Water", "Occupancy reset", "People count reset to zero")
            st.rerun()
        st.info("Occupied" if st.session_state.water_people > 0 else "Empty / no occupants counted")

    with right:
        st.subheader("Flow monitoring")
        flow_rate = st.number_input("Simulated flow rate (L/min)", min_value=0.0, max_value=200.0,
                                    value=float(st.session_state.water_flow), step=0.5)
        scenario = st.selectbox("Flow scenario", ["Normal", "Continuous flow", "Flow while empty"])
        q1, q2 = st.columns(2)
        if q1.button("Apply flow reading", use_container_width=True):
            st.session_state.water_flow = float(flow_rate)
            alert = flow_rate > 0 and (scenario == "Flow while empty" or
                                       (scenario == "Normal" and st.session_state.water_people == 0))
            message = f"{flow_rate:.1f} L/min; scenario: {scenario}"
            log_event("Water", "Flow reading applied", message)
            water_events = load_records("water_events.json")
            water_events.insert(0, {"time": datetime.now().isoformat(timespec="seconds"),
                                    "event": "Flow reading", "flow_l_min": flow_rate,
                                    "scenario": scenario, "alert": alert, "details": message})
            save_records("water_events.json", water_events[:500])
            st.rerun()
        if q2.button("Simulate 1 minute", use_container_width=True):
            st.session_state.water_flow = float(flow_rate)
            st.session_state.water_extra_used += float(flow_rate)
            log_event("Water", "Simulated minute", f"{flow_rate:.1f} litres added")
            st.rerun()

        if flow_rate > 0 and (scenario == "Flow while empty" or
                              (scenario == "Normal" and st.session_state.water_people == 0)):
            st.error("Possible waste: water flow is reported while the room is empty. Verify with real measurements.")
        elif scenario == "Continuous flow" and flow_rate > 0:
            st.warning("Continuous flow selected. Check whether a tap may have been left running.")
        elif flow_rate > 0:
            st.success("Flow is present; this alone does not prove wastage.")
        else:
            st.info("No active flow in the simulated reading.")

    st.subheader("Water use comparison")
    st.bar_chart(pd.DataFrame({
        "Litres": [baseline, used, saved]
    }, index=["Baseline", "Estimated used", "Estimated saved"]))
    st.write(f"Estimated cost saving: **₹{cost_saved:.3f}** per simulated period.")
    st.caption("Savings use assumptions entered above; they are not measured real-world savings.")

    water_events = load_records("water_events.json")
    st.subheader("Saved water events")
    if water_events:
        st.dataframe(pd.DataFrame(water_events), use_container_width=True, hide_index=True)
        st.download_button("Download water events JSON", json.dumps(water_events, indent=2),
                           file_name="water_events.json", mime="application/json")
    else:
        st.info("No water events saved yet.")

# ---------- Electricity ----------
elif page == "⚡ Electricity":
    st.header("⚡ Smart Electricity Saver")
    st.caption("AI-assisted people counting to support energy-saving decisions. Controls are recommendations only.")
    threshold = st.number_input("People threshold", min_value=1, max_value=100, value=5)
    st.info("Demo rule: people count ≥ threshold suggests lights/fans ON; below threshold suggests OFF. This does not control electrical equipment.")

    input_method = st.radio("Image source", ["Take a photo with camera", "Upload a room image"], horizontal=True)
    image_file = st.camera_input("Capture room image") if input_method == "Take a photo with camera" else st.file_uploader(
        "Upload a room image", type=["jpg", "jpeg", "png"]
    )

    if image_file is not None:
        st.image(image_file, caption="Input image", use_container_width=True)
        run_detection = st.button("Run AI people detection", type="primary")
        if run_detection:
            try:
                from ultralytics import YOLO
                from PIL import Image
                import numpy as np

                @st.cache_resource
                def load_yolo_model():
                    return YOLO("yolo11n.pt")

                image = Image.open(image_file).convert("RGB")
                with st.spinner("Loading model and detecting people... First run may download model weights."):
                    model = load_yolo_model()
                    results = model.predict(source=np.array(image), imgsz=640, conf=0.35, verbose=False)
                result = results[0]
                people = 0
                if result.boxes is not None and result.boxes.cls is not None:
                    for cls_id in result.boxes.cls.tolist():
                        if result.names[int(cls_id)] == "person":
                            people += 1
                annotated = result.plot()[:, :, ::-1]
                lights = "ON" if people >= threshold else "OFF (recommended)"
                fans = "ON" if people >= threshold else "OFF (recommended)"
                status = "Occupied" if people >= threshold else "Low occupancy"
                record = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "people_count": people,
                    "threshold": int(threshold),
                    "occupancy_status": status,
                    "lights_recommendation": lights,
                    "fans_recommendation": fans,
                    "low_occupancy": people < threshold,
                    "control_mode": "recommendation_only"
                }
                electricity_records = load_records("electricity_records.json")
                electricity_records.insert(0, record)
                save_records("electricity_records.json", electricity_records[:500])
                log_event("Electricity", "AI people detection", f"{people} people detected; {status}")
                st.session_state.last_electricity_record = record
                st.session_state.last_electricity_image = annotated
            except ImportError:
                st.error("AI packages are missing. Install dependencies from requirements.txt.")
            except Exception as exc:
                st.error(f"Detection could not run: {exc}")
                st.caption("Check internet access for first-time model download and ensure the image is clear.")

    if "last_electricity_record" in st.session_state:
        record = st.session_state.last_electricity_record
        if "last_electricity_image" in st.session_state:
            st.image(st.session_state.last_electricity_image, caption="AI detection image with boxes", use_container_width=True)
        a, b, c = st.columns(3)
        a.metric("People detected", record["people_count"])
        b.metric("Room status", record["occupancy_status"])
        c.metric("Threshold", record["threshold"])
        st.write(f"**Lights recommendation:** {record['lights_recommendation']}")
        st.write(f"**Fans recommendation:** {record['fans_recommendation']}")
        st.download_button("Download latest electricity JSON", json.dumps(record, indent=2),
                           file_name="electricity_status.json", mime="application/json")

    electricity_records = load_records("electricity_records.json")
    st.subheader("Saved electricity scans")
    if electricity_records:
        st.dataframe(pd.DataFrame(electricity_records), use_container_width=True, hide_index=True)
    else:
        st.info("No electricity scans saved yet. Capture or upload an image and run detection.")

# ---------- Paper ----------
elif page == "📄 Paper":
    st.header("📄 Paper Management")
    st.caption("Print request tracking and paper recycling records. Records are saved locally in this project.")
    requests = load_records("paper_requests.json")
    recycling = load_records("recycling_records.json")
    departments = ["Biology", "Business", "Computer Science", "Engineering", "Administration", "Other"]

    tab1, tab2, tab3 = st.tabs(["Overview", "Print requests", "Recycling"])
    with tab1:
        total_pages = sum(int(item.get("pages", 0)) for item in requests if item.get("status") == "Printed")
        pending = sum(1 for item in requests if item.get("status") == "Pending")
        recycled_kg = sum(float(item.get("kilograms", 0)) for item in recycling)
        a, b, c = st.columns(3)
        a.metric("Printed pages recorded", f"{total_pages:,}")
        b.metric("Pending requests", pending)
        c.metric("Paper recycled", f"{recycled_kg:.1f} kg")
        st.subheader("Department quota tracker")
        quotas = st.text_input("Illustrative quota per department (pages)", value="10000")
        try:
            quota = max(1, int(quotas))
            usage = {}
            for item in requests:
                if item.get("status") == "Printed":
                    usage[item["department"]] = usage.get(item["department"], 0) + int(item["pages"])
            for department in departments:
                used = usage.get(department, 0)
                st.write(f"**{department}:** {used:,} / {quota:,} pages")
                st.progress(min(1.0, used / quota))
        except ValueError:
            st.warning("Enter a valid whole-number quota.")

    with tab2:
        st.subheader("Create a print request")
        with st.form("paper_request_form", clear_on_submit=True):
            requester = st.text_input("Requester name")
            department = st.selectbox("Department", departments)
            purpose = st.text_input("Purpose")
            pages = st.number_input("Number of pages", min_value=1, max_value=5000, value=1, step=1)
            double_sided = st.checkbox("Double-sided printing requested", value=True)
            submitted = st.form_submit_button("Save print request")
        if submitted:
            if not requester.strip() or not purpose.strip():
                st.error("Enter requester name and purpose.")
            else:
                new_request = {
                    "id": f"request-{int(time.time() * 1000)}",
                    "requester": requester.strip(),
                    "department": department,
                    "purpose": purpose.strip(),
                    "pages": int(pages),
                    "double_sided": double_sided,
                    "status": "Pending",
                    "received": datetime.now().isoformat(timespec="seconds")
                }
                requests.append(new_request)
                save_records("paper_requests.json", requests)
                log_event("Paper", "Print request created", f"{requester.strip()} · {pages} pages")
                st.success("Print request saved.")
                st.rerun()

        st.subheader("Manage requests")
        if requests:
            for item in reversed(requests):
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    with left:
                        st.markdown(f"**{item['requester']}** · {item['department']}")
                        st.write(f"{item['purpose']} — {item['pages']} pages")
                        st.caption(f"Status: {item['status']} · {'Double-sided' if item.get('double_sided') else 'Single-sided'}")
                    with right:
                        if item["status"] == "Pending":
                            c1, c2 = st.columns(2)
                            if c1.button("Approve", key=f"approve-{item['id']}"):
                                item["status"] = "Approved"
                                save_records("paper_requests.json", requests)
                                log_event("Paper", "Request approved", item["id"])
                                st.rerun()
                            if c2.button("Reject", key=f"reject-{item['id']}"):
                                item["status"] = "Rejected"
                                save_records("paper_requests.json", requests)
                                log_event("Paper", "Request rejected", item["id"])
                                st.rerun()
                        elif item["status"] == "Approved":
                            if st.button("Mark printed", key=f"printed-{item['id']}"):
                                item["status"] = "Printed"
                                save_records("paper_requests.json", requests)
                                log_event("Paper", "Request marked printed", item["id"])
                                st.rerun()
        else:
            st.info("No print requests yet. Add one using the form above.")

    with tab3:
        st.subheader("Record paper recycling")
        with st.form("recycling_form", clear_on_submit=True):
            recycling_department = st.selectbox("Department", departments, key="recycling_department")
            kilograms = st.number_input("Recycled paper (kg)", min_value=0.1, max_value=100000.0, value=1.0, step=0.5)
            submitted_recycling = st.form_submit_button("Save recycling record")
        if submitted_recycling:
            entry = {
                "department": recycling_department,
                "kilograms": float(kilograms),
                "recorded_at": datetime.now().isoformat(timespec="seconds")
            }
            recycling.append(entry)
            save_records("recycling_records.json", recycling)
            log_event("Paper", "Recycling recorded", f"{kilograms} kg · {recycling_department}")
            st.success("Recycling record saved.")
            st.rerun()
        if recycling:
            st.dataframe(pd.DataFrame(recycling), use_container_width=True, hide_index=True)
            st.download_button("Download recycling records CSV", pd.DataFrame(recycling).to_csv(index=False),
                               file_name="paper_recycling.csv", mime="text/csv")
        else:
            st.info("No recycling records yet.")

# ---------- Reports ----------
elif page == "📊 Reports":
    st.header("📊 Reports and saved data")
    files = [
        ("Water events", "water_events.json"),
        ("Electricity scans", "electricity_records.json"),
        ("Paper requests", "paper_requests.json"),
        ("Recycling records", "recycling_records.json"),
        ("All activity", "events.json"),
    ]
    for label, filename in files:
        records = load_records(filename)
        with st.expander(f"{label} ({len(records)} records)"):
            if records:
                st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
                st.download_button(
                    f"Download {filename}",
                    json.dumps(records, indent=2, ensure_ascii=False),
                    file_name=filename,
                    mime="application/json",
                    key=f"download-{filename}",
                )
            else:
                st.info("No records saved yet.")

    st.caption("Data is stored as JSON files in the project's data/ folder on this computer.")
