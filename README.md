# WeChat QR Code Login Demo

This project demonstrates WeChat QR code login functionality using Vue 3 + Ant Design for the frontend and Flask for the backend.

## Project Structure
```
.
├── frontend/    # Vue 3 + Ant Design frontend
├── backend/     # Flask backend
├── .env.example # Environment variables example
└── README.md
```

## Setup Instructions

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

5. Update the .env file with your WeChat credentials:
   - WECHAT_APP_ID
   - WECHAT_APP_SECRET

6. Start the Flask server:
   ```bash
   flask run
   ```

## Usage
1. Open your browser and navigate to http://localhost:5173
2. If not logged in, you'll see a WeChat QR code
3. Scan the QR code with WeChat to log in
4. Upon successful login, you'll see a success message

## Note
You'll need to register your application with WeChat and obtain the necessary APP_ID and APP_SECRET to enable QR code login functionality.
