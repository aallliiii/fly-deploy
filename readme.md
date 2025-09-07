# Intelligent Search API

A sophisticated semantic search system that combines CLIP embeddings with LLM-powered query enhancement and result reranking to search through events and products data.

## What This Project Does

Imagine you have thousands of events and products in your database, and users want to search for them using natural language like "I need a summer dress for weekend events" or "outdoor music events this weekend". This API:

- **Understands Context**: Knows that "summer dress" relates to summer clothing 
- **Smart Search**: Uses AI to find the most relevant results even if the exact words don't match
- **Explains Results**: Tells you why each result was chosen and ranks them by relevance

## Features

- **Semantic Search**: Uses OpenCLIP embeddings for deep semantic understanding
- **Query Enhancement**: LLM-powered query optimization with intelligent filtering
- **Result Reranking**: GPT-4 powered relevance scoring and explanation
- **Hybrid Search**: Supports both events and products with context-aware filtering
- **Time-aware Filtering**: Advanced date range filtering for events
- **Audience Targeting**: Gender-specific product recommendations


## Project Structure

```
fly-senga-ai/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── config/
│   └── settings.py        # Configuration management
├── schemas/
│   └── search_schemas.py   # Pydantic schemas
│   └── vector_management_schemas.py
│   └── query_enhancements_schemas.py    
├── services/
│   ├── clip_service.py    # CLIP embedding generation
│   ├── qdrant_service.py  # Vector database operations
│   ├── llm_service.py     # OpenAI GPT integration
│   ├── search_service.py  # Search orchestration
│   └── upload_service.py  # Data processing and upload
├── utils/
│   ├── text_processing.py # Text preparation utilities
│   └── date_utils.py      # Date handling utilities
└── routers/
    ├── vector_management.py          # Data management endpoints 
    └── search.py          # Search endpoints
```

## Prerequisites

Before we start, you'll need:
- **OpenAI API key** (for GPT-4 integration) 
- **Qdrant instance** (vector database) 

## Complete Setup Guide

### Step 1: Check if Python is Installed

#### On Windows:
1. Press `Windows + R`, type `cmd`, and press Enter
2. Type `python --version` and press Enter
3. If you see something like `Python 3.8.0` or higher, you're good!
4. If you get an error, go to **Step 2**

#### On Mac:
1. Press `Cmd + Space`, type `Terminal`, and press Enter
2. Type `python3 --version` and press Enter
3. If you see something like `Python 3.8.0` or higher, you're good!
4. If you get an error, go to **Step 2**

### Step 2: Install Python (if not installed)

#### On Windows:
1. Go to [python.org](https://www.python.org/downloads/)
2. Download the latest Python version (3.8 or higher)
3. Run the installer
4. **IMPORTANT**: Check "Add Python to PATH" during installation
5. Click "Install Now"
6. Restart your command prompt and verify with `python --version`

#### On Mac:
**Option 1 - Using Homebrew (Recommended):**
1. Install Homebrew first by pasting this in Terminal:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```

**Option 2 - Direct Download:**
1. Go to [python.org](https://www.python.org/downloads/)
2. Download the latest Python version for macOS
3. Run the installer
4. Verify with `python3 --version`

### Step 3: Download the Project

#### Option 1 - Using Git (if you have it):
```bash
git clone <repository-url>
cd fly-senga-ai
```

#### Option 2 - Download ZIP:
1. Download the project as a ZIP file
2. Extract it to a folder of your choice
3. Open Terminal (Mac) or Command Prompt (Windows)
4. Navigate to the folder:

**Windows:**
```cmd
cd C:\path\to\your\fly-senga-ai
```

**Mac:**
```bash
cd /path/to/your/fly-senga-ai
```

### Step 4: Create a Virtual Environment

A virtual environment keeps this project's dependencies separate from your system Python.

#### On Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your command line.

#### On Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### Step 5: Install Project Dependencies

With your virtual environment activated:

#### On Windows:
```cmd
pip install -r requirements.txt
```

#### On Mac:
```bash
pip install -r requirements.txt
```

This will download and install all the necessary packages. It might take a few minutes.

### Step 6: Set Up Environment Variables

1. **Copy the example environment file:**

   **Windows:**
   ```cmd
   copy .env.example .env
   ```
   
   **Mac:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file:**
   
   Open the `.env` file in any text editor (Notepad on Windows, TextEdit on Mac) and fill in your credentials:
   
   ```env
   QDRANT_URL=your_qdrant_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   EMBEDDINGS=your_embedding_model_here (openclip or openai)
   ```

### Step 7: Run the Application

Now you can start the server:

#### On Windows:
```cmd
cd app
fastapi dev main.py
```

#### On Mac:
```bash
cd app
fastapi dev main.py
```

You should see output like:
```
INFO:     Will watch for changes in these directories: ['/path/to/your/project']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchedFiles
INFO:     Started server process [8856]
INFO:     Waiting for application startup.
INFO:     Application startup complete. (After this line appears you can access the API at http://localhost:8000)
```

🎉 **Success!** Your API is now running at `http://localhost:8000`

### Step 8: Test Your Installation

1. Open your web browser
2. Go to `http://localhost:8000/docs`
3. You should see the interactive API documentation (Swagger UI)

## Using the API

### Initialize the Database

Before uploading any data, initialize the Qdrant collection:

**Using curl (if available):**
```bash
curl -X POST "http://localhost:8000/api/initialize"
```

**Using the web interface:**
1. Go to `http://localhost:8000/docs`
2. Find the `POST /api/initialize` endpoint
3. Click "Try it out" then "Execute"

### Upload Sample Data

#### Upload Events:

```bash
curl -X POST "http://localhost:8000/api/upload" \
-H "Content-Type: application/json" \
-d '{
  "data_type": "event",
  "data": [
    {
      "id": 188,
      "name": "MERLINA PEARL A WINDRUSH JOURNEY THE MUSICAL",
      "description": "Discover the Story Behind the Windrush Journey – Through Music, Drama & Legacy\n\nMerlina Pearl: A Windrush Journey – The Musical invites audiences of all ages to learn about Black British history in a powerful and creative way. Inspired by true events, this moving stage production tells the story of Merlina, a hopeful young woman who arrived on the HMT Empire Windrush in 1948, only to face rejection, resilience, and renewal in a new land.\n\nWith a vibrant mix of music, theatre, and storytelling, Merlina Pearl is a meaningful experience for families, schools, and communities looking to explore the roots and realities of the Windrush generation together.\n\nWhether you're attending with loved ones, students, or colleagues, this is more than a show—it’s a shared cultural moment not to be missed.\n\nGroup or corporate discounts available – email us at enquiries@2chiceventmanagement.co.uk to enquire.",
      "start_date": "26/05/2025",
      "start_time": "19:00",
      "end_date": "26/05/2025",
      "end_time": "21:15",
      "address": "The Stroller Hall Hunts Bank",
      "city": "Manchester",
      "state": "b",
      "country": "United Kingdom",
      "zip_code": "M3 1DA",
      "ticket_price": 30,
      "groups": "24-30",
      "types_name": "Concerts",
      "status": 0,
      "genre": "Theatre/Musical",
      "audience": "General Audience",
      "age_restriction": "",
      "features": "Art Display",
      "indoor_outdoor": "Indoor",
      "dress_code": "",
      "language": "English",
      "season": "Spring",
      "tags": "Concerts, Manchester, Theatre/Musical"
    },
  ]
}'
```

#### Upload Products:

```bash
curl -X POST "http://localhost:8000/api/upload" \
-H "Content-Type: application/json" \
-d '{
  "data_type": "product",
  "data": [
    {
      "id": 140,
      "product_name": "Le Hoodie Epingle",
      "product_description": "This black hoodie features the brand’s name with one large pin and four smaller pins embroidered around the logo. Inspired by the Le Costume épinglé suit, it’s a wearable, ready-to-wear interpretation of the pin double breasted design, merging sophistication with an edgy twist.",
      "category_name": "Hoodies",
      "brand_name": "Aimer Blanche",
      "type_name": "Men",
      "color": "Black",
      "material": "Fleece",
      "style": "Casual",
      "occasion": "Casual wear",
      "fit": "Regular",
      "pattern": "Embroidered",
      "season": "Winter",
      "audience": "Men",
      "special_features": "Hooded, Embroidered, Graphic/Logo Detail",
      "tags": "Aimer Blanche, Hoodies, Men, Black, Embroidered"
    },
  ]
}'
```

### Search an Entry

```bash
curl -X POST "http://localhost:8000/api/search" \
-H "Content-Type: application/json" \
-d '{
  "query": "",
  "top_k": ""
}'
```

### Delete an Entry

```bash
curl -X POST "http://localhost:8000/api/delete-entry" \
-H "Content-Type: application/json" \
-d '{
  "name_space": "product",
  "original_id": "111"
}'
```

**Expected Response:**
```json
{
  "results": [
    {
      "original_id": "1",
      "relevance_score": 9,
      "relevance_reason": "Perfect match for summer dress request",
      "payload": {...},
      "name_space": "product"
    }
  ],
  "enhancement": {
    "enhanced_query": "summer dress casual weekend wear women's clothing",
    "search_type": "product",
    "audience": "female",
    "time_filter": null,
    "is_weekend": true,
    "other_keyword_filters": ["summer", "dress", "weekend", "casual"]
  },
  "total_retrieved": 15,
  "final_count": 5
}
```

## Troubleshooting

### Common Issues:

**1. "Python not found" error:**
- Make sure Python is installed and added to PATH
- On Mac, try `python3` instead of `python`

**2. "Permission denied" errors:**
- Make sure your virtual environment is activated (you should see `(venv)`)
- On Mac, you might need `sudo` for some installations

**3. "Module not found" errors:**
- Ensure your virtual environment is activated
- Re-run `pip install -r requirements.txt`

**4. "Connection error" when testing:**
- Check your .env file has correct API keys
- Verify Qdrant is running and accessible
- Check your internet connection

**5. Port already in use:**
- Another application might be using port 8000
- Stop other applications or change the port in the command


## Stopping the Application

To stop the API server:
- Press `Ctrl + C` in your terminal

To deactivate the virtual environment:

**Windows:**
```cmd
deactivate
```

**Mac:**
```bash
deactivate
```