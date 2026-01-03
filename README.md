# 🌩️ StormEye

**StormEye** is a high‑performance, asynchronous reconnaissance tool that leverages the **SecurityTrails API** to enumerate subdomains, performs fast liveness and port checks using **async I/O**, and then runs **Nuclei** to identify potential vulnerabilities.

Built with **Python asyncio and aiohttp**, StormEye is designed for speed, scalability, and low‑noise reconnaissance — making it ideal for **bug bounty hunters, penetration testers, and VDP engagements**.

---

## 🚀 Features
> StormEye is built around asynchronous I/O to handle large attack surfaces efficiently without overwhelming the network or the target.

- 🔍 Subdomain enumeration using the **SecurityTrails API**
- ⚡ **Fully asynchronous architecture** using `asyncio` and `aiohttp`
- 🌐 Concurrent HTTP/HTTPS liveness probing
- 🔌 Fast async TCP port scanning on common web ports
- 🧠 Passive‑first reconnaissance (VDP‑friendly)
- ☢️ Automated vulnerability scanning with **Nuclei**
- 🛠️ Lightweight, dependency‑minimal, and automation‑ready

---

## 🔄 How It Works

1. Accepts a target domain as input
2. Asynchronously queries **SecurityTrails** to enumerate subdomains
3. Concurrently probes discovered subdomains over HTTP and HTTPS
4. Performs **async TCP port scanning** on common service ports
5. Saves alive hosts and open ports to output files
6. Executes **Nuclei** against verified alive targets for vulnerability detection

---

## 🧰 Requirements

Ensure the following are installed:

- **Python 3.8+**
- **Nuclei**  
  👉 https://github.com/projectdiscovery/nuclei
- A valid **SecurityTrails API Key**  
  👉 https://securitytrails.com/

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/stodachon/stormeye.git
cd stormeye
pip3 install -r requirements.txt
