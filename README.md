# RotorHazard LED Callsign Image
Image display plugin for RotorHazard

When activated, displays [callsign].png on connected LED panel.

## Installation

Copy the `led_handler_callsign_image` plugin into the `src/server/plugins` directory in your RotorHazard install. Start RotorHazard.

If installation is successful, the RotorHazard log will contain the message `Loaded plugin module led_handler_callsign_image` at startup.

## Usage

- Create images for each user, ideally matching the size of your LED panel display. Name these images for the user's callsign, such as `Hazard.png` for pilot `Hazard`. It's best to assume case-sensitivity.
- Place all images in the `src/server/static/user` directory on the server.
- Confirm your server is correctly configured for your LED panel.
- In the `LED Events` panel on the `Settings` page, choose the `Image: user/[callsign].png` or `Image: user/[callsign].png / Leader` effect where approprite. Effects only appear for events where valid, such as "Lap Recorded" but not "Server Startup".
