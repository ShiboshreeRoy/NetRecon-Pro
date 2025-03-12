import socket
import dns.resolver
import geoip2.database
import requests
import logging
import subprocess
from scapy.all import ARP, Ether, srp
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Banner
def display_banner():
    banner = f"""
{Fore.GREEN}
██████╗ ███████╗████████╗██████╗ ███████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔═══██╗████╗  ██║
██████╔╝█████╗     ██║   ██████╔╝███████╗██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝     ██║   ██╔══██╗╚════██║██║   ██║██║╚██╗██║
██║  ██║███████╗   ██║   ██║  ██║███████║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
{Fore.YELLOW}
NetRecon Pro - Network Reconnaissance Tool
{Fore.CYAN}Developed by: Shiboshree Roy
{Fore.MAGENTA}Version: 0.01
{Style.RESET_ALL}
"""
    print(banner)

# Function to get the IP address of a website
def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.error as e:
        logging.error(f"Error resolving IP for {domain}: {e}")
        return None

# Function to get DNS information (A, MX, NS records)
def get_dns_info(domain):
    dns_info = {}
    try:
        # A records
        a_records = dns.resolver.resolve(domain, 'A')
        dns_info['A'] = [rdata.address for rdata in a_records]
        
        # MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        dns_info['MX'] = [rdata.exchange.to_text() for rdata in mx_records]
        
        # NS records
        ns_records = dns.resolver.resolve(domain, 'NS')
        dns_info['NS'] = [rdata.target.to_text() for rdata in ns_records]
        
        return dns_info
    except dns.resolver.NoAnswer:
        logging.warning(f"No DNS records found for {domain}")
        return None
    except dns.resolver.NXDOMAIN:
        logging.error(f"Domain {domain} does not exist")
        return None
    except Exception as e:
        logging.error(f"Error retrieving DNS info for {domain}: {e}")
        return None

# Function to get detailed geolocation information
def get_geolocation(ip_address):
    try:
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        response = reader.city(ip_address)
        geolocation = {
            "Country": response.country.name,
            "City": response.city.name,
            "Postal Code": response.postal.code,
            "Latitude": response.location.latitude,
            "Longitude": response.location.longitude,
            "ISP": response.traits.isp
        }
        return geolocation
    except geoip2.errors.AddressNotFoundError:
        logging.warning(f"Geolocation not found for IP: {ip_address}")
        return None
    except FileNotFoundError:
        logging.error("GeoLite2 database not found. Download it from https://dev.maxmind.com/geoip/geoip2/geolite2/")
        return None
    except Exception as e:
        logging.error(f"Error retrieving geolocation for {ip_address}: {e}")
        return None

# Function to ping a server
def ping_server(ip_address):
    try:
        result = subprocess.run(['ping', '-c', '4', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout.decode('utf-8')
        else:
            logging.error(f"Ping failed for {ip_address}: {result.stderr.decode('utf-8')}")
            return None
    except Exception as e:
        logging.error(f"Error pinging {ip_address}: {e}")
        return None

# Function to perform a traceroute
def traceroute(ip_address):
    try:
        result = subprocess.run(['traceroute', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout.decode('utf-8')
        else:
            logging.error(f"Traceroute failed for {ip_address}: {result.stderr.decode('utf-8')}")
            return None
    except Exception as e:
        logging.error(f"Error performing traceroute for {ip_address}: {e}")
        return None

# Function to get the MAC address (only works on local network)
def get_mac_address(ip_address):
    try:
        arp = ARP(pdst=ip_address)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        result = srp(packet, timeout=2, verbose=0)[0]
        return result[0][1].hwsrc
    except Exception as e:
        logging.error(f"Error retrieving MAC address for {ip_address}: {e}")
        return None

# Main function
def main():
    display_banner()
    domain = input(f"{Fore.CYAN}[+] Enter the website domain: {Style.RESET_ALL}")
    
    # Get IP address
    ip_address = get_ip_address(domain)
    if not ip_address:
        logging.error("Unable to proceed without IP address.")
        return
    print(f"{Fore.GREEN}[+] IP Address: {ip_address}{Style.RESET_ALL}")
    
    # Get DNS info
    dns_info = get_dns_info(domain)
    if dns_info:
        print(f"\n{Fore.YELLOW}[+] DNS Information:{Style.RESET_ALL}")
        for record_type, records in dns_info.items():
            print(f"{Fore.CYAN}  {record_type}: {Fore.WHITE}{', '.join(records)}{Style.RESET_ALL}")
    
    # Get geolocation
    geolocation = get_geolocation(ip_address)
    if geolocation:
        print(f"\n{Fore.YELLOW}[+] Geolocation Information:{Style.RESET_ALL}")
        for key, value in geolocation.items():
            print(f"{Fore.CYAN}  {key}: {Fore.WHITE}{value}{Style.RESET_ALL}")
    
    # Ping the server
    ping_result = ping_server(ip_address)
    if ping_result:
        print(f"\n{Fore.YELLOW}[+] Ping Results:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{ping_result}{Style.RESET_ALL}")
    
    # Perform traceroute
    traceroute_result = traceroute(ip_address)
    if traceroute_result:
        print(f"\n{Fore.YELLOW}[+] Traceroute Results:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{traceroute_result}{Style.RESET_ALL}")
    
    # Get MAC address (local network only)
    mac_address = get_mac_address(ip_address)
    if mac_address:
        print(f"\n{Fore.YELLOW}[+] MAC Address: {Fore.GREEN}{mac_address}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}[+] MAC Address: {Fore.RED}Not retrievable over the internet.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()