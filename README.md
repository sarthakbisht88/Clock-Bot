<div align="center">

# ⏱️ Clock Bot

**A lightweight, highly portable Discord utility designed for global timezones, automated reminders, and server tracking.**

[🌐 Live Website](https://clock-bot.netlify.app/) • [🤖 Invite Bot](https://discord.com/oauth2/authorize?client_id=1463741597043789887) • [💬 Support Server](https://top.gg/discord/servers/904636741903486976) • [⭐ Leave a Review](https://top.gg/bot/1463741597043789887)

</div>

---

## ✨ Overview

Clock Bot is built using modern Discord User-App and Guild architectures. It bridges the gap between global communities by giving users precise time conversions, custom timezone linking, and server activity tracking without cluttering channel lists.

---

## 🚀 Key Features

* **Global Time Management:** Instantly check current times, days, and dates across 260+ countries or custom user-linked profiles.
* **Smart Time Conversions:** Convert times between different regions with automated day-shift indicators (`➕ Next day` / `➖ Previous day`).
* **Server Time Tracking:** Calculate exact server membership duration using `/time_spent`.
* **Automated Birthdays & Reminders:** Set timer-based hidden reminders and configure daily server-wide birthday announcements.

---

## 🛠️ Command Reference

### 🌍 Time & Timezone
* `/time country [country]` — Check local time in any specified country.
* `/time user [user]` — Check the local time of a linked user.
* `/time conversion [from] [time] [to]` — Convert time across borders.
* `/timezone set [timezone]` — Link your profile to the global timezone database.
* `/timezone remove` — Unlink your saved timezone profile.

### 📅 Date & Birthdays
* `/day [day] [month] [year]` — Find out what day of the week a date falls on.
* `/birthday set [day] [month] [year]` — Save your birthday for automated server announcements.
* `/birthday setup [channel]` — *(Admins)* Set the channel for daily birthday broadcasts.
* `/birthday remove` — Delete your saved birthday from the system.

### ⚡ Utilities
* `/time_spent [user]` — Check how long a member has been in the server.
* `/reminder [user] [time] [unit] [message]` — Set a timer-based reminder.
* `/ping` — Check connection latency.

---

## 🤖 Hosting & Architecture

Clock Bot is designed for seamless scaling:
* **Backend:** Python (`discord.py`, `pytz`, asynchronous task loops) with JSON-backed persistent data storage.
* **Frontend Portal:** Fully responsive static landing page hosted on [Netlify](https://clock-bot.netlify.app/).

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
