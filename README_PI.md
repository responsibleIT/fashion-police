# Fashion Police - Raspberry Pi Client (Minimal)

Minimal Raspberry Pi client with dummy server responses for testing.

## What This Branch Does

- ✅ Camera capture on Raspberry Pi
- ✅ Displays dummy style predictions
- ✅ User feedback interface
- ❌ No ML processing (dummy responses only)
- ❌ No actual server calls (placeholder for future)

## Installation on Raspberry Pi

### 1. Clone Repository
```bash
git clone <your-repo>
cd fashion-police
git checkout <pi-branch-name>
```

### 2. Install Dependencies (Super lightweight!)
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements-pi-client.txt
```

Total installation size: **~50MB** (vs 2GB+ for full version!)

### 3. Run the App
```bash
streamlit run pi_client.py
```

### 4. Access
- On Pi: `http://localhost:8501`
- From another device: `http://PI_IP_ADDRESS:8501`

## How It Works

1. **Camera Page**: Take a photo of your outfit
2. **Results Page**: See dummy style predictions (hardcoded)
3. **Feedback Page**: Select the actual style (saved to session only)

## Current Limitations (Dummy Mode)

- Results are fake/hardcoded
- No actual ML processing
- No server communication
- Feedback is not saved anywhere

## Next Steps (When Server is Ready)

Replace the dummy functions in `pi_client.py`:

```python
# Current (dummy):
def get_dummy_response() -> dict:
    return {...}  # Hardcoded response

# Future (real API):
def get_server_response(image: Image.Image) -> dict:
    response = requests.post(f"{SERVER_URL}/predict", files=...)
    return response.json()
```

## Files You Need

**For Pi Client:**
- `pi_client.py` - Main app
- `requirements-pi-client.txt` - Dependencies

**NOT Needed on Pi:**
- ❌ `src/` folder (all ML code)
- ❌ `server_api.py` (server code)
- ❌ `requirements.txt` (heavy dependencies)
- ❌ `data/` folder (models and saved data)
- ❌ `env/` (will be created fresh)

## Testing

Just run and test the UI flow:
1. Camera capture works
2. Results display properly
3. Feedback buttons work
4. Navigation works

Everything functional except actual ML inference!
