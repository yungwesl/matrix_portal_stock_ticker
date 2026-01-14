# Stock Ticker v0.1

import time
import board
import displayio
import busio
import board
import terminalio
import adafruit_requests as requests

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from os import getenv
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut
from adafruit_esp32spi.adafruit_esp32spi_wifimanager import WiFiManager
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label


ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

# WiFi credentials
WIFI_SSID = getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = getenv("CIRCUITPY_WIFI_PASSWORD")

# Alpha Vantage API key (free from https://www.alphavantage.co/support/#api-key)
API_KEY = getenv("APIKEY")
# STOCK_SYMBOL = getenv("TICKER")
# Define your ticker symbols
tickers = ["ALAB", "BRK.B", "VOO", "GLD", "BTC"]

# Colors
COLOR_GREEN = 0x19650A
COLOR_RED = 0xFF0000
COLOR_WHITE = 0x7F7F7F


# Setup ESP32 WiFi
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = board.SPI()
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

# Setup WiFiManager
wifi = WiFiManager(esp, ssid, password)

wifi.connect()
print(f"Connected! IP: {esp.pretty_ip(esp.ip_address)}")

# Setup networking
#requests_session = requests.Session(wifi._wifi.socket)

# Setup display
matrix = Matrix()
font = terminalio.FONT
display = matrix.display
group = displayio.Group()

# Load arrow bitmaps (if they exist)
try:
    greenup_bitmap = displayio.OnDiskBitmap("/greenup.bmp")    
except Exception as e:
    print(f"Logo not found: {e}")
    
try:
    reddown_bitmap = displayio.OnDiskBitmap("/reddown.bmp")    
except Exception as e:
    print(f"Logo not found: {e}")

# Create text labels
symbol_label = label.Label(font, text="TICKER", color=COLOR_WHITE, x=1, y=5)
price_label = label.Label(font, text="$0.00", color=COLOR_WHITE, x=1, y=18)
change_label = label.Label(font, text="+0.00%", color=COLOR_GREEN, x=1, y=28)

group.append(symbol_label)
group.append(price_label)
group.append(change_label)

display.root_group = group    

def get_stock_data(symbol):
    """Fetch real-time stock data from Finnhub API"""
    global previous_close
    
    # Get current quote
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    
    try:
        print(f"\nFetching data for {symbol}...")
        response = wifi.get(quote_url)
        data = response.json()
        response.close()
        
        if "c" in data and data["c"] != 0:  # c = current price
            current_price = data["c"]
            prev_close = data["pc"]  # pc = previous close
            
            # Calculate percentage change
            if prev_close and prev_close != 0:
                change_percent = ((current_price - prev_close) / prev_close) * 100
            else:
                change_percent = 0
            
            return current_price, change_percent
        else:
            print("Error: Invalid data received", data)
            return None, None
            
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def clear_pixel_by_pixel_animated():
    """Clear with visible animation effect"""
    width = display.width
    height = display.height
    
    # Start with all pixels white
    bitmap = displayio.Bitmap(width, height, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000  # Black
    palette[1] = 0xFFFFFF  # White
    
    # Fill with white
    for y in range(height):
        for x in range(width):
            bitmap[x, y] = 1
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group()
    group.append(tile_grid)
    display.root_group = group
    display.refresh()
    
    time.sleep(0.5)
    
    # Now erase each pixel with animation
    for y in range(height):
        for x in range(width):
            bitmap[x, y] = 0
            if (x * y) % 10 == 0:  # Refresh every few pixels for speed
                display.refresh()

    
def clear_side():
    try:
        logo_bitmap = displayio.OnDiskBitmap("/white.bmp")
        logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=43, y=1)
        group.append(logo_sprite)
    except Exception as e:
        print(f"Logo not found: {e}")
    try:
        logo_bitmap = displayio.OnDiskBitmap("/clear.bmp")
        logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=43, y=1)
        group.append(logo_sprite)
    except Exception as e:
        print(f"Logo not found: {e}")
            
def place_logo(symbol):
    if ticker == "ALAB":
        # Load ALAB logo bitmap (if it exists)
        try:
            logo_bitmap = displayio.OnDiskBitmap("/alab_logo.bmp")
            logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=44, y=1)
            group.append(logo_sprite)
        except Exception as e:
            print(f"Logo not found: {e}")
    elif ticker == "BRK.B":
        # Load BRK logo bitmap (if it exists)
        try:
            logo_bitmap = displayio.OnDiskBitmap("/brk_logo.bmp")
            logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=44, y=5)
            group.append(logo_sprite)
        except Exception as e:
            print(f"Logo not found: {e}")
    elif ticker == "BTC":
        # Load BTC logo bitmap (if it exists)
        try:
            logo_bitmap = displayio.OnDiskBitmap("/btc_logo.bmp")
            logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=44, y=2)
            group.append(logo_sprite)
        except Exception as e:
            print(f"Logo not found: {e}")    
    elif ticker == "GLD":
        # Load GLD logo bitmap (if it exists)
        try:
            logo_bitmap = displayio.OnDiskBitmap("/gld_logo.bmp")
            logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=43, y=4)
            group.append(logo_sprite)
        except Exception as e:
            print(f"Logo not found: {e}")    
    elif ticker == "VOO":
        # Load VOO logo bitmap (if it exists)
        try:
            logo_bitmap = displayio.OnDiskBitmap("/vgd_logo.bmp")
            logo_sprite = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=43, y=1)
            group.append(logo_sprite)
        except Exception as e:
            print(f"Logo not found: {e}")    

    else:
        print("No ticker symbol logo found") 
        
# Main loop
last_update = 0
UPDATE_INTERVAL = 30  # Update every 60 seconds

while True:
    
    for ticker in tickers:

        print(f"Processing: {ticker}")

        price, change_percent = get_stock_data(ticker)
        
        if price is not None:
            print("Placing Logo")
            place_logo(ticker)
            # Update Ticker
            symbol_label.text = ticker
            # Update price label
            price_label.text = f"${price:.2f}"
            
            # Update change label with color
            if change_percent >= 0:
                change_label.text = f"+{change_percent:.2f}%"
                change_label.color = COLOR_GREEN
                arrow_sprite = displayio.TileGrid(greenup_bitmap, pixel_shader=greenup_bitmap.pixel_shader, x=45, y=22)

            else:
                change_label.text = f"{change_percent:.2f}%"
                change_label.color = COLOR_RED
                arrow_sprite = displayio.TileGrid(reddown_bitmap, pixel_shader=reddown_bitmap.pixel_shader, x=45, y=20)
            
            group.append(arrow_sprite)
            print(f"{ticker}: ${price:.2f} ({change_percent:+.2f}%)")
        else:
            print(f"No price found: {price}, {change_percent}")
        time.sleep(UPDATE_INTERVAL)
        clear_side()          
    