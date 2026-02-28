## WECS 2026 - The Anti Loop
*Get focused with fun*

A gamified productivity app that uses face detection and biological feedback principles to combat doomscrolling and maintain focus during work sessions.

## Biological Inspiration

We designed app with two biological brain mechanisms in mind:
ack mechanisms:

### Negative Feedback Loop (Distraction Management)
Just like your body regulates cortisol levels when stressed, "The Anti Loop" creates a **negative feedback system** for distractions:

1. **Detection Phase**: Face detection monitors your attention
2. **Response Phase**: Looking away triggers escalating "punishments" (popup spam, audio alerts)
3. **Correction Phase**: The discomfort motivates you to refocus
4. **Stabilization**: Once focused again, the system returns to baseline

The discomfort signals you to change behavior, then rewards you with relief when you comply.

### Positive Reinforcement Loop (Break Activities)
Physical activity during breaks creates a **positive feedback cycle**:

- **Exercise**: Increased blood flow to brain
- **Movement**: Dopamine & endorphin release  
- **Enhanced Focus**: Better work performance
- **Success**: Motivation to maintain healthy habits

The app encourages "touching grass" (literally going outside) because:
- Natural light regulates circadian rhythm
- Physical movement increases neuroplasticity
- Breaking the screen-time cycle prevents digital fatigue
- Real-world interaction provides genuine dopamine (not the fake hits from doomscrolling)

## 🎮 Features

### 1. **Focus Tracker** (main.py)
- Real-time face detection using OpenCV
- Tracks distraction events and duration
- Visual feedback via camera overlay
- Integrates with Pomodoro timer bar

### 2. **Punishment System** (punisher.py)
When you look away from your work:
- Plays the sus sound effect at 10 frames (subtle warning)
- After 30 frames of looking away, triggers "punishment mode":
  - Spawns popup windows with images/videos/GIFs from media folder
  - Plays overlapping audio files for maximum annoyance
  - All popups appear at random screen positions
  - Continues until you refocus

This artificial "stress" mimics hormonal stress responses, making distraction genuinely uncomfortable.

### 3. **Pomodoro Timer Bar** (pomodoro_timer.py)
- Minimalist bottom-screen timer (25-minute default)
- Live status updates: `FOCUSED` / `LOOKING AWAY` / `DOOMSCROLLING`
- Visual companions:
  - **Cat mascot**: Eyes closed when focused, open when distracted
  - **Cortisol gauge**: Shows "stress level" based on behavior
- Drag to hide/show the bar

### 4. **Challenge Wheel** (spinningWheel.py)
After 5 distractions, you must:
- Spin the wheel (rigged to land on "touch grass")
- Complete a physical challenge:
  - **Touch Grass**: Take a timed photo outside (with fake "grass detection AI")
  - **Shower**: Reset mentally and physically  
  - **Exercise**: Get blood flowing

### 5. **Break Timer** (break_timer.py)
- 5-minute guided break with face detection
- Ensures you physically move away from your desk
- Displays exercise demonstration video
- Monitors distance from screen (detects if face is too close)

### 6. **Social Accountability** (combinedMsg.py)
- Sends Telegram message to your "crush" when you fail to focus
- Terminal-style interface with typewriter effect
- Receives responses in real-time
- Creates social pressure to stay on task

> **Note**: Requires Telegram Bot API token and chat ID in .env file

## Why This Works (The Science)

### The Dopamine Problem
Doomscrolling hijacks your brain's reward system:
- Infinite scroll = unpredictable rewards
- Each refresh = potential dopamine hit
- Your brain gets addicted to the *possibility* of interesting content

### Our Solution
1. **Make distraction painful** (negative feedback)
   - Interrupts the doomscroll dopamine loop
   - Associates looking away with immediate discomfort
   - Your brain learns: "Focus = peace, distraction = chaos"

2. **Make breaks rewarding** (positive reinforcement)
   - Physical activity releases *real* dopamine
   - Sunlight and movement improve mood naturally
   - Creates a healthier dopamine cycle

3. **Social accountability** 
   - Humans are social creatures
   - Fear of judgment is a powerful motivator
   - Telegram integration adds real-world consequences

## Installation

```sh
pip install -r requirements.txt
```

### Dependencies
- `opencv-python`: Face detection and camera access
- `tkinter`: GUI framework (usually pre-installed with Python)
- `PIL/Pillow`: Image processing
- `pygame`: Audio playback
- `python-dotenv`: Environment variable management
- `requests`: Telegram API communication

## 🚀 Usage

### Basic Setup

1. **Add media files** to the media folder:
   - Images: `.png`, `.jpg`, `.jpeg`
   - Videos: `.mp4`, `.avi`, `.mkv`, `.gif`  
   - Audio: `.mp3`, `.wav`, `.ogg`

2. **(Optional) Configure Telegram**:
   ```env
   # .env
   TOKEN=your_telegram_bot_token
   CHAT_ID=your_chat_id
   ```

3. **Run the app**:
   ```sh
   python main_menu.py
   ```

### Main Menu (main_menu.py)
- **START FOCUS**: Begin a focus session with tracking
- **START BREAK**: Launch the guided break timer

### During Focus Mode
- Stay visible to the camera
- If you look away for >30 frames (~2 seconds), punishment mode activates
- At 5 total distractions, you're forced to take a break or spin the challenge wheel

### Keyboard Shortcuts
- `Escape`: Close challenge wheel or terminal
- `Right-click`: Close timer bar
- Drag timer bar down to minimize it

## 🗂️ Project Structure

```
.
├── face_detector/
│   ├── main.py           # Main face tracking logic
│   ├── punisher.py       # Punishment system (popup spam)
│   └── sus.mp3          # Warning sound effect
├── media/               # Your distraction punishment media
├── main_menu.py         # Application entry point
├── pomodoro_timer.py    # Bottom-screen timer bar
├── break_timer.py       # Guided break mode
├── spinningWheel.py     # Challenge wheel + grass touching
├── combinedMsg.py       # Telegram integration
└── requirements.txt     # Python dependencies
```

### The Cortisol Connection
The app deliberately shows a **cortisol level gauge** (pomodoro_timer.py) because:
- High cortisol = stress hormone = distraction mode active
- Low cortisol = relaxed state = focused work
- Visual metaphor helps users understand their mental state

### Why Exercise Matters
The break timer monitors your distance from the screen because:
- Sitting too close = poor posture = restricted blood flow
- Moving away = muscles engage = oxygen to brain
- This break from screens prevents **digital eye strain** and **decision fatigue**

## 🛠️ Technical Details

### Face Detection
- Uses OpenCV's [`haarcascade_frontalface_default.xml`](https://github.com/opencv/opencv/tree/master/data/haarcascades)
- Detects faces in real-time at ~30 FPS
- Adjustable sensitivity via `scaleFactor` and `minNeighbors` parameters

### Multi-Threading
- Camera processing runs on main thread (Tkinter requirement)
- Telegram API calls use background threads to prevent UI freezing
- Punishment spawner uses threading for simultaneous popups

### State Management
Key variables in main.py:
- `distraction_frames`: Counter for consecutive frames without face detection
- `is_currently_distracted`: Boolean flag for punishment mode
- `total_distractions`: Cumulative distraction count per session

## ⚠️ Known Issues

- **Camera Index**: May need to adjust camera index in main.py (line 23) and break_timer.py (line 42)
- **Telegram Polling**: Aggressive polling can hit API rate limits - consider increasing delay in combinedMsg.py
- **Window Management**: Punishment windows may persist if app crashes - use Task Manager to kill orphaned processes

## 📄 License

GNU General Public License v3.0 - See LICENSE for details.

This is free software: you are free to change and redistribute it. There is NO WARRANTY, to the extent permitted by law.

---

## 🧪 The Experiment

This app is essentially a **behavioral psychology experiment** for your own brain:

1. **Hypothesis**: Making distraction painful and breaks rewarding will reduce doomscrolling
2. **Independent Variable**: Your attention/distraction behavior  
3. **Dependent Variable**: Changed habits and improved focus over time
4. **Control**: Your pre-app baseline behavior

Track your distraction count over multiple sessions to see if the negative feedback loop successfully rewires your habits. The goal isn't perfection - it's **progress** through biological principles.

**Remember**: Your brain is plastic. Every time you resist distraction and refocus, you're literally building new neural pathways. This app just makes that process... *highly motivated*. 💚