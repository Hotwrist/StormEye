import argparse
import asyncio
import aiohttp
import socket
import subprocess
import json

API_KEY = "<YOUR SECURITY TRAILS API KEY>"
COMMON_PORTS = [80, 443, 8080, 8443, 8000, 8888, 3000, 5000]

def banner():
    print(r"""
███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗███████╗██╗   ██╗███████╗
██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║██╔════╝╚██╗ ██╔╝██╔════╝
███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║█████╗   ╚████╔╝ █████╗  
╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║██╔══╝    ╚██╔╝  ██╔══╝  
███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗   ██║   ███████╗
╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝   ╚═╝   ╚══════╝

StormEye — SecurityTrails-powered Subdomain Recon & Nuclei Scanner

Author  : John Ebinyi Odey (Redhound | Hotwrist)
Purpose : Passive recon + automated vulnerability detection
Note    : For authorized security testing only
""")


# ----------------------------
# SUBDOMAIN ENUMERATION
# ----------------------------

async def fetch_subdomains(session, domain):
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {"apikey": API_KEY}

    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            print(f"[!] SecurityTrails error: {resp.status}")
            return []

        data = await resp.json()
        subs = [f"{s}.{domain}" for s in data.get("subdomains", [])]

        print(f"[+] Found {len(subs)} subdomains")
        return subs

# ----------------------------
# ALIVE CHECK (HTTPS/HTTP)
# ----------------------------

async def probe(session, sub):
    urls = [f"https://{sub}", f"http://{sub}"]

    for url in urls:
        try:
            async with session.get(url, timeout=5, ssl=False) as resp:
                if resp.status < 500:
                    print(f"[ALIVE] {url}  →  {resp.status}")
                    return url
        except:
            pass
    return None

# ----------------------------
# PORT SCAN (ASYNC)
# ----------------------------

async def scan_port(host, port):
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=1)
        writer.close()
        await writer.wait_closed()
        print(f"[OPEN] {host}:{port}")
        return port
    except:
        return None

async def scan_ports(sub):
    try:
        host = socket.gethostbyname(sub)
    except:
        return []

    tasks = [scan_port(host, p) for p in COMMON_PORTS]
    results = await asyncio.gather(*tasks)
    open_ports = [p for p in results if p]
    return open_ports

# ----------------------------
# MAIN LOGIC
# ----------------------------

async def main(domain):
    async with aiohttp.ClientSession() as session:
        print(f"[+] Enumerating subdomains for: {domain}")
        subs = await fetch_subdomains(session, domain)

        print("[+] Checking which subdomains are alive...")
        probe_tasks = [probe(session, s) for s in subs]
        results = await asyncio.gather(*probe_tasks)

        alive = [r for r in results if r]

        with open("alive.txt", "w") as f:
            for url in alive:
                f.write(url + "\n")

        print(f"\n[+] Total alive: {len(alive)} (saved to alive.txt)")

        # ----- PORT SCAN -----
        print("\n[+] Scanning ports for alive hosts...")
        port_results = {}

        for url in alive:
            host = url.split("://")[1]
            ports = await scan_ports(host)
            port_results[host] = ports

        with open("ports.json", "w") as f:
            json.dump(port_results, f, indent=4)

        print("[+] Port scan saved to ports.json")

        # ----- RUN NUCLEI -----
        print("\n[+] Running Nuclei on alive hosts...")
        try:
            subprocess.run(["nuclei", "-l", "alive.txt", "-o", "nuclei.txt"])
            print("[+] Nuclei results saved to nuclei.txt")
        except FileNotFoundError:
            print("[!] Nuclei is not installed or not in PATH")

# ----------------------------
# CMD ARGUMENT PARSER
# ----------------------------

if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="StormEye — Asynchronous Subdomain Recon and Nuclei Automation Tool")
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    args = parser.parse_args()

    asyncio.run(main(args.domain))

