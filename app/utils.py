from user_agents import parse
import geoip2.database
import os
from django.conf import settings

def anonymize_ip(ip):
    if not ip:
        return None
    
    if '.' in ip:  # IPv4
        return '.'.join(ip.split('.')[:3]) + '.0'
    elif ':' in ip:  # IPv6
        return ':'.join(ip.split(':')[:4]) + '::'
    return ip

def parse_user_agent(user_agent_str):
    if not user_agent_str:
        return None
    
    ua = parse(user_agent_str)
    
    if ua.is_mobile:
        device_type = 'Mobile'
    elif ua.is_tablet:
        device_type = 'Tablet'
    elif ua.is_pc:
        device_type = 'Desktop'
    elif ua.is_bot:
        device_type = 'Bot'
    else:
        device_type = 'Other'
    
    return {
        'browser': f"{ua.browser.family} {ua.browser.version_string}",
        'os': f"{ua.os.family} {ua.os.version_string}",
        'device': ua.device.family,
        'device_type': device_type,
        'is_mobile': ua.is_mobile,
        'is_tablet': ua.is_tablet,
        'is_pc': ua.is_pc,
        'is_bot': ua.is_bot
    }

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # For testing purposes, if the IP is localhost, use a public IP
    if ip == '127.0.0.1':
        return '8.8.8.8'  # Google's public DNS server IP

    return ip

# Construct path to the GeoIP database
GEOIP_DATABASE_PATH = os.path.join(settings.BASE_DIR, 'app', 'data', 'GeoLite2-Country.mmdb')

# Create the reader object once when the module is loaded (caching).
try:
    if os.path.exists(GEOIP_DATABASE_PATH):
        GEOIP_READER = geoip2.database.Reader(GEOIP_DATABASE_PATH)
    else:
        GEOIP_READER = None
except Exception:
    # If the database is corrupt or there's an error, set reader to None
    GEOIP_READER = None

def get_country_from_ip(ip):
    """
    Looks up the country of an IP address using the cached GeoIP database reader.
    """
    if not ip or not GEOIP_READER:
        return None

    try:
        response = GEOIP_READER.country(ip)
        return response.country.name
    except geoip2.errors.AddressNotFoundError:
        # The IP address was not found in the database
        return None
    except Exception:
        # Handle other potential errors
        return None