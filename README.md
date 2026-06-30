# Rewire — Dopamine OS

Rewire is an AI-powered "Dopamine Operating System" designed to help users break bad habits, reset their neural baseline, and reclaim their focus. It moves beyond clinical mental health tools by offering a world-class, premium aesthetic (Apple meets modern editorial design) combined with real-time cognitive interventions.

## ✨ Core Features

*   **Dopamine Stability Dashboard:** A data-rich command center visualizing recovery scores, neural stability trends, and abstinence streaks.
*   **Real-Time AI Recovery Coach:** A specialized cognitive intervention engine that analyzes journal entries, stress levels, and triggers to provide actionable, in-the-moment advice.
*   **Gamification Engine:** Rebuilding a baseline is rewarding. Earn XP, level up, and unlock milestone badges by maintaining streaks and completing AI-assigned daily tasks.
*   **Emergency Mode (Protocol Lockdown):** When cravings hit their peak, the Emergency Mode instantly locks down the environment, logs a critical event, and guides the user through immediate somatic coping tools (like Box Breathing and Urge Surfing).
*   **Contextual Journaling:** A safe space to log thoughts, stress metrics, and craving intensity, allowing the AI coach to identify hidden triggers over time.

---

## 🛤️ End-to-End User Journey (How Rewire Works)

Rewire isn't just a tracking app; it is a holistic, closed-loop behavioral intervention system. Here is exactly how the product functions from end to end:

### 1. Onboarding & Baseline Calibration
When a user registers, they define the specific cheap-dopamine habit they want to break (e.g., Doomscrolling, Gaming, Sugar, Vaping). The system establishes their baseline and assigns a starting Level and XP.

### 2. The Daily Protocol (Dashboard)
The user's primary interface is the **System Status Dashboard**. Every day, they are presented with:
*   **The AI Recovery Program:** A daily, customized checklist of behavioral interventions (e.g., "Remove gaming devices from living space", "Walk for 20 mins").
*   **XP & Level Progression:** Completing these tasks and avoiding relapses earns the user XP, slowly leveling them up as a visual representation of their neural recovery.
*   **The Dopamine Stability Chart:** A data visualization that dynamically plots their emotional stability and craving intensity over time.

### 3. Contextual Data Logging (Journaling)
Throughout the day, users can log Journal entries. Instead of just a text box, the journal captures **Stress Levels** and **Craving Intensity**. 
*   If a user logs an entry indicating high stress, this data is fed directly into the AI Coach's memory.

### 4. Real-time Intervention (AI Coach)
If the user feels an urge, they can open the **AI Coach**. Because the AI has access to their Journal and Dashboard metrics, it doesn't just give generic advice. It provides highly specific, contextual interventions based on *their* tracked triggers and patterns (e.g., "I see your stress level hit an 8 today. Let's redirect that anxiety away from gaming and into a 10-minute walk.").

### 5. Crisis Management (Emergency Mode)
If the urge becomes overpowering, the user clicks the red **Emergency Mode** button. 
*   The system instantly logs a critical "Level 9 Craving" event in the backend.
*   The AI is overridden with a severe crisis prompt.
*   The UI locks down, presenting immediate, hardcoded somatic interventions (Box Breathing, Urge Surfing, Cold Exposure) to force the user through the 20-minute physiological craving window.
*   *Reward:* If the user survives the urge by using the emergency button instead of relapsing, they are awarded 75 XP and a special "Crisis Survivor" badge.

### 6. The Nightly Evaluation
At midnight, a backend cron job runs (`daily_scoring.py`). It evaluates the user's logged data for the day. 
*   If they did not log a relapse, their **Streak** is automatically incremented.
*   If they did log a relapse, their streak is reset to 0, but the AI Coach is primed to offer compassionate, analytical support the next day to help them understand what went wrong, ensuring a continuous loop of learning and recovery.

---

## 🛠️ Tech Stack

**Frontend:**
*   Next.js 14 (App Router)
*   React & TypeScript
*   Tailwind CSS (Styling & Design System)
*   Framer Motion (Micro-animations & transitions)
*   Recharts (Data visualization)
*   Shadcn/UI & Lucide React (Components & Icons)

**Backend:**
*   Python 3.10+ & FastAPI
*   PostgreSQL (Database)
*   SQLAlchemy & Alembic (ORM & Migrations)
*   OpenAI / LLM Integrations (AI Coach engine)

---

## 🚀 Getting Started

Follow these instructions to run the full Rewire application locally.

### 1. Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)
*   PostgreSQL running locally

### 2. Backend Setup
Navigate to the backend directory and set up your Python environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rewire
SECRET_KEY=your_super_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Run Database Migrations:**
```bash
alembic upgrade head
```

**Start the FastAPI Server:**
```bash
uvicorn app.main:app --reload --port 8000
```
*The backend API will now be running at `http://localhost:8000`*

### 3. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install
```

**Environment Variables:**
Create a `.env.local` file in the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Start the Next.js Development Server:**
```bash
npm run dev
```
*The frontend application will now be running at `http://localhost:3000`*

---

## 🎨 Design Philosophy
Rewire embraces a minimalist, luxury aesthetic.
*   **Color Palette:** Warm Ivory background, Rich Black typography, with Calm Teal and Soft Coral accents.
*   **Typography:** Editorial serif and sans-serif pairings to evoke a sense of calm and trust.
*   **Interactions:** Subtle, fluid animations powered by Framer Motion to make the interface feel responsive and alive without causing overstimulation.

## 📄 License
MIT License