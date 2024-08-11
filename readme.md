
# 🎙️ PodAI: Your AI-Powered Podcast Revolution 🚀

![PodAI Logo](podai.png)
![GitHub package.json version](https://img.shields.io/github/package-json/v/team-hashing/hooli)
![GitHub All Releases](https://img.shields.io/github/downloads/team-hashing/hooli/total)
![GitHub last commit](https://img.shields.io/github/last-commit/team-hashing/hooli)
![GitHub issues](https://img.shields.io/github/issues-raw/team-hashing/hooli)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/team-hashing/hooli)
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/team-hashing/hooli)
![GitHub contributors](https://img.shields.io/github/contributors/team-hashing/hooli)
![GitHub language count](https://img.shields.io/github/languages/count/team-hashing/hooli)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/team-hashing/hooli)
![GitHub repo size](https://img.shields.io/github/repo-size/team-hashing/hooli)
![GitHub top language](https://img.shields.io/github/languages/top/team-hashing/hooli)

![GitHub Repo stars](https://img.shields.io/github/stars/team-hashing/hooli?style=social)
![GitHub forks](https://img.shields.io/github/forks/team-hashing/hooli?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/team-hashing/hooli?style=social)

## 🌟 Welcome to the Future of Podcasting

PodAI is not just another podcast creation tool; it's a symphony of AI-driven services working in harmony to revolutionize the way we create, produce, and experience podcasts. Imagine a world where your ideas transform into captivating audio content with just a few clicks. That's the power of PodAI at your fingertips!

### Check out our live demo [here](https://team-hashing.github.io/podai_web_host/)

### Watch the YouTube video [here](https://youtu.be/FgNmPAK_6pg)
---


## 🏗️ Architecture: A Masterpiece of Microservices

PodAI is built on a robust, scalable architecture comprising four key services, each playing a crucial role in the podcast creation orchestra:

1. 🎭 **APIP (Application Programming Interface for Podcasts)**
   - The maestro of our symphony
   - Orchestrates the entire podcast creation process
   - Delegates tasks to other services with precision and finesse

2. 🗣️ **TTS (Text-to-Speech)**
   - The voice of our creation
   - Transforms written scripts into lifelike audio
   - Breathes life into your podcast content

3. 🧠 **Gemini**
   - The creative genius
   - Harnesses the power of Google's Gemini API
   - Generates compelling scripts and eye-catching images

4. 🌐 **Web**
   - The face of our application
   - Provides a sleek, intuitive interface for users
   - Communicates with APIP to bring the magic to your browser

---

## 🛠️ Tech Stack: Cutting-Edge Tools for Cutting-Edge Content

- **Language**: Python 🐍
- **Framework**: FastAPI ⚡
- **Containerization**: Docker 🐳
- **Orchestration**: Docker Compose 🎼
- **Database**: Firebase 🔥
- **AI**: Google Gemini 🤖
- **Mobile**: Flutter 📱 (Android app in `mobile` folder)

---

## 🚀 Getting Started: Embark on Your Podcast Journey

### Prerequisites

Before you dive into the world of PodAI, ensure you have:

- Docker and Docker Compose installed on your system
- A Google Cloud Project with Gemini API enabled
- A Firebase project set up with two collections: `podcasts` and `users`
- Inside Firebase Storage, ensure the existence of two folders: `podcasts` and `voices`. The `voices` folder must contain two Piper compatible voices with the following files:
  - `female.json`
  - `female.onnx`
  - `male.json`
  - `male.onnx`

### Essential Configuration Files

PodAI requires two key configuration files to unlock its full potential:

1. `firebase-key.json`: Your Firebase project credentials
2. `google-key.json`: Your Google Cloud project API key

⚠️ **Important**: Place these files in the appropriate locations within the project structure. Without them, PodAI's wings will be clipped!

### Launch Sequence

1. Clone this repository to your local machine
2. Navigate to the project root directory
3. Fire up the services with a single command:

   ```bash
   docker-compose up -d
   ```

4. Watch as PodAI springs to life, ready to transform your ideas into auditory gold!

---

## 🗂️ Project Structure: A Home for Every Component

```
PodAI/
├── apip/
│   └── ... (APIP service files)
├── tts/
│   └── ... (TTS service files)
├── gemini/
│   └── ... (Gemini service files)
├── web/
│   └── ... (Web service files)
├── mobile/
│   └── ... (Flutter Android app files)
├── docker-compose.yml
├── firebase-key.json
├── google-key.json
└── README.md
```

---

## 🌈 Features: A Tapestry of Possibilities

- 🤖 AI-generated podcast scripts tailored to your topics
- 🎨 Custom image creation for podcast episodes
- 🔊 Lifelike text-to-speech conversion for natural-sounding narration
- 🌐 User-friendly web interface for podcast management
- 📱 Companion Android app for on-the-go podcast creation and management

---

## 🤝 Contributing: Join the PodAI Revolution

We believe in the power of community! If you'd like to contribute to PodAI:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License


---

## 🙏 Acknowledgments

- Hat tip to the incredible people at the Gemini API Developer Competition 
- Built with ❤️ by Team Hashing (Guillermo and Daniel)

---

Embark on your journey with PodAI today and revolutionize the world of podcasting! 🎙️✨
