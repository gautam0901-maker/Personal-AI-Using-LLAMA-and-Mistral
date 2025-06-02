# 🤖 Pekko – Your Personal AI Assistant

**Pekko** is a fully personalized smart assistant built for **Gautam**, powered by LLaMA/Mistral through **Ollama**, with intelligent memory, natural language reminders, weather support, and interactive voice and chat UI.

---

## 🌟 Features

- 🧠 **Context-aware chat** (powered by Mistral via Ollama)
- 📝 **Smart reminder system** (Natural language + UI-based)
- 📅 **Date parsing + calendar insights**
- ☁️ **Live weather updates** (via OpenWeatherMap API)
- 🔔 **SMS + Email notifications** (via Twilio + Gmail)
- 🗃️ **Auto chat logging + markdown summaries**
- 🧏 **Voice interaction** with wake word ("Hey Pekko")
- 💾 **Memory management** for chat history, reminders, context
- 📊 **Reminder stats and insights panel**
- 🗂️ **Chat bubble UI with animated transitions**
- 🎨 **Dark-mode themed sidebar with fixed input**
- 🛜 **Offline-friendly fallback support**
- 🌐 **Model powered by Ollama (LLaMA/Mistral)**

---

## ⚙️ Technologies Used

| Component       | Tech Used                         |
|----------------|-----------------------------------|
| UI Framework    | `Flet` (Python UI toolkit)       |
| LLM Backend     | `Mistral` via `Ollama`           |
| Voice Interface | `SpeechRecognition` + `pyttsx3`  |
| Weather API     | `OpenWeatherMap`                 |
| Reminder Alerts | `Twilio SMS` + `Gmail SMTP`      |
| Memory Storage  | `JSON`-based file memory          |
| Chat Scheduling | `Threading`, `datetime`, `plyer` |
| API Integration | `requests`, `toml`, `os`         |

---

## 📂 Project Structure
