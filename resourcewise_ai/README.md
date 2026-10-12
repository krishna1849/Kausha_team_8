# ResourceWise AI

A single Streamlit website with Water, Electricity, Paper, and Reports sections. The interface uses white and blue shades.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended).
4. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the website:

   ```bash
   streamlit run app.py
   ```

Streamlit will print a local URL, usually http://localhost:8501.

## Sections

- **Overview**: summary of records saved by the modules.
- **Water**: occupancy and water-flow simulation, estimated savings, and saved events.
- **Electricity**: camera capture or image upload, YOLO people detection, and lights/fans recommendations.
- **Paper**: print requests, approvals, printed status, and recycling entries.
- **Reports**: inspect and download saved records.

## Important notes

- Water readings are simulated; no real valve or sensor is connected.
- Electricity detection uses the Ultralytics YOLO `yolo11n.pt` model. The first run may need internet access to download model weights. It counts people in a captured/uploaded image; it is not continuous live video streaming.
- Electricity recommendations do not control physical lights, fans, or mains electricity.
- Paper features are based on the submitted `paper.js` workflow, rebuilt as Streamlit forms because the original JavaScript requires a separate HTML/CSS page that was not included.
- Records are saved to JSON files in `data/`. This is local file storage, not a multi-user cloud database. Keep backups of the `data/` folder.
- The app begins with empty records; it does not prefill the sample paper requests from the original JavaScript.

## Files

- `app.py`: combined website
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: light blue Streamlit theme
- `data/`: created automatically for saved records
