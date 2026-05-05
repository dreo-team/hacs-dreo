# Official Dreo Smart Device Integration for Home Assistant

This is the official integration component developed and maintained by the Dreo engineering team for Home Assistant. It enables direct control and monitoring of Dreo smart devices including fans, air conditioners, ceiling fans, and humidifiers through your Home Assistant installation.

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)

If you like Dreo products and want to support this integration, you can purchase our devices through this link: [Dreo Fans on Amazon](https://www.amazon.com/s?k=Dreo+Smart+Fan). For more information about our products, please visit our official website at [official website](https://www.dreo.com/).

**Special Offer**: If you submit issues or provide valuable suggestions for our products that we adopt, we will offer you a 15% discount coupon (85% of original price) for purchases on our official website.

## Version Information

This integration offers two release channels:

1. **Beta Testing**: Pre-release versions available for early access to new features. These builds may contain bugs but provide the latest functionality.
2. **Stable Release**: Thoroughly tested versions recommended for regular users.

We recommend most users to use the stable releases for reliability, while beta versions are available for those interested in testing new features and providing early feedback.

We welcome you to subscribe to our GitHub repository to stay updated with our latest releases and announcements.

**Important Notice**: Dreo is currently working on becoming an official Home Assistant integration. In the near future, this integration will be available directly through the official Home Assistant channels. The current HACS plugin version is not considered stable. Once Dreo is integrated into the official Home Assistant repository, we recommend transitioning to the official integration.

## Interested in Contributing?

We welcome enthusiasts and hobbyists who are interested in contributing to the Dreo integration for Home Assistant. Your valuable contributions help improve this project for everyone. For more information on how to contribute, please check [Contributing](contributing.md).

## Table of Contents

- [Acknowledgments](#acknowledgments)
- [Compatibility](#compatibility)
- [Installation](#installation)
- [Initial Configuration](#initial-configuration)
- [Debugging](#debugging)
- [Troubleshooting](#troubleshooting)
  - [If HomeAssistant Doesn't Show Your Device](#if-homeassistant-doesnt-show-your-device)
- [Adding New Products](#adding-new-products)

## Compatibility

Currently supported device models are listed below. Nearly every Dreo model has been integrated; only the `KCM001` and `KCM002` devices remain unsupported at this time.
> **Note:** The tables below highlight representative models for each category and are not exhaustive—additional supported models exist beyond those listed.

### Supported Products

The following product types are supported. All variants have been tested.

| Product Type | Model Prefix(es) | Notes |
| -------- | ------------ | ------ |
| Tower Fans | DR-HTF | Tower fans |
| Circulation Fans | DR-HAF, DR-HPF | Circulation fans with oscillation control |
| Ceiling Fans | DR-HCF | Ceiling fans with light control |
| Air Conditioners | DR-HAC | Portable air conditioners |
| Humidifiers | DR-HHM, DR-HEC | Smart humidifiers and evaporative coolers |

Models that have been specifically tested can be found below.

#### Tower Fans

Typically, DREO tower fans with the name ending with an `S` support this feature.
The specified product names and models that have been specifically tested can be found below.

- Nomad One S (DR-HTF007S)
- Cruiser Pro T1 S (DR-HTF001S)
- Cruiser Pro T2 S (DR-HTF002S)
- Cruiser Pro T2 S 2nd Gen (DR-HTF009S)
- Cruiser Pro T3 S (DR-HTF008S/DBTF08S)
- Pilot Pro S (DR-HTF005S)
- Pilot Max S (DR-HTF004S/DBTF04S)
- MC710S (DR-HTF010S)

Features for Tower Fans include:
- Power (true, false)
- Preset modes (Normal, Natural, Sleep, Auto)
- Set Speed (varies by model: 1-4, 1-6, 1-9, or 1-12)
- Oscillate (true, false)


#### TurboPoly™ Fans

- TurboPoly™ Table Fan 511S (DR-HAF001S)
- TurboPoly™ Fan 513S (DR-HAF003S)
- TurboPoly™ Table Fan 714S (DR-HAF004S)
- TurboPoly™ Fan 311S (DR-HPF001S)
- TurboPoly™ Fan 502S (DR-HPF002S)
- TurboPoly™ Fan 704S (DR-HPF004S)
- TurboPoly™ Fan 715S (DR-HPF005S)
- TurboPoly™ Fan 707S (DR-HPF007S)
- TurboPoly™ Fan 508S (DR-HPF008S)
- TurboPoly™ Fan 765S (DR-HPF010S)

Features for Circulation Fans include:
- Power (true, false)
- Preset modes (Normal, Natural, Sleep, Auto, Turbo, Custom)
- Set Speed (varies by model: 1-8, 1-9, or 1-10)
- Oscillation modes (Fixed, Horizontal, Vertical, Pan-tilt, Both)
- Smart follow mode (select models)
- Ambient lighting (DR-HPF008S)

#### Ceiling Fans

- Ceiling Fan 513S (DR-HCF003S)

Features for Ceiling Fans include:
- Fan Power (true, false)
- Light Power (true, false)
- Preset modes (Normal, Natural, Sleep, Reverse)
- Set Speed (1-12)
- Brightness control (1-100)
- Color temperature control (1-100)

#### Air Conditioners

- Portable Air Conditioner 516S (DR-HAC006S)

Features for Air Conditioners include:
- Power (true, false)
- HVAC modes (Cool, Dry, Fan Only)
- Preset modes (Sleep, Eco)
- Set Speed (1-4)
- Temperature control (64-86°F)
- Humidity control (40-70%)

#### Humidifiers

- HM735S Smart Humidifier (DR-HHM005S)
- Evaporative Cooler 712S (DR-HEC002S)

Features for Humidifiers include:
- Power (true, false)
- Preset modes (Normal, Auto, Sleep, Natural)
- Set Speed (1-4)
- Humidity control (40-90%)
- RGB night light (DR-HHM005S)
- Sleep mode switch (DR-HHM005S)
- Oscillate (true, false, DR-HEC002S)


Product name could be found on the package box, user manual, or the label on the device.
**Model name also could be found on the label of the device or user manual in the product package. 
Note: If you cannot find your device name or model, please contact us.


## Installation

**Note**: Dreo integration is currently in the process of being added to HACS. At present, only manual installation is available.

### HACS Installation

You can install this integration by adding this repository as a custom repository in HACS. Here's how:

1. Click the button below to download the integration from HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dreo-team&repository=hass-dreoverse&category=integration)

2. Restart your Home Assistant instance.

3. Start the config flow by clicking this button:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dreo)

### Manual Installation

1. Copy the `dreo` directory into your `/config/custom_components` directory in your Home Assistant installation.

2. Restart your Home Assistant instance to load the integration.

**Note about dependencies**: This integration has `pydreo-cloud` library as a dependency (version 1.0.0), which is specified in the manifest.json file. When you restart Home Assistant after adding the integration (including in Docker environments), the system will automatically install the required dependencies. You do not need to manually install dependencies in most cases.

If for some reason the automatic installation fails, you can manually install the dependency:

```bash
pip install pydreo-cloud==1.0.0
```

## Initial Configuration

> [!IMPORTANT]
> If you used the very early version of this that required editing `configuration.yaml`, you will need to do a one-time reconfiguration. Delete the configuration entries you added and then go through the configuration flow within HomeAssistant.

### Adding the Dreo Integration to Home Assistant

Follow these detailed steps to configure the Dreo integration after installation:

1. **Access Home Assistant Settings**:
   - Open your Home Assistant web interface
   - Click on the gear icon (⚙️) in the lower left sidebar to access **Settings**

2. **Navigate to Integrations**:
   - In the Settings menu, find and click on **Devices & Services**
   - You'll see a list of your currently configured integrations

3. **Add Dreo Integration**:
   - Look for the blue **+ ADD INTEGRATION** button in the bottom right corner of the screen
   - Click this button to open the integration selection dialog

4. **Find and Select Dreo**:
   - In the search box that appears, type `Dreo`
   - The Dreo integration should appear in the search results
   - Click on the Dreo integration to select it

5. **Enter Your Credentials**:
   - You will be prompted to enter your Dreo account credentials
   - Enter the same username (email) and password you use to log in to the Dreo mobile app
   - Click **Submit** to continue

6. **Complete the Setup**:
   - If your credentials are correct, Home Assistant will connect to the Dreo cloud service
   - Your Dreo devices will be automatically discovered and added to Home Assistant
   - You can now control your Dreo devices from the Home Assistant interface

After completion, your Dreo devices will appear in the Home Assistant dashboard where you can control them.

## Debugging

Use the **Diagnostics** feature in HomeAssistant to get diagnostics from the integration. Sensitive info should be redacted automatically.

In your `configuration.yaml` file, add this:

```
logger:
    logs:
        dreo: debug
```

Now restart HomeAssistant. Perform the actions needed to generate some debugging info.

### Collecting Debug Information

When troubleshooting issues with the Dreo integration, you may need to collect debug logs or diagnostic files. These files help developers understand what's happening with your system.

#### Option 1: Download Full Home Assistant Logs

These logs contain detailed information about all Home Assistant operations, including the Dreo integration.

**Steps to download full logs:**
1. Open Home Assistant web interface
2. Click on **Settings** in the left sidebar
3. Select **System** from the menu
4. Click on the **Logs** tab
5. Look for the **Download full log** button at the bottom right
6. Save the log file to your computer

> **Important:** Full logs may contain sensitive information about your Home Assistant setup and connected devices. Always review logs before sharing them with others.

#### Option 2: Download Dreo-specific Diagnostics

For issues specifically related to the Dreo integration, downloading diagnostics provides focused information.

**Steps to download diagnostics:**
1. Open Home Assistant web interface
2. Click on **Settings** in the left sidebar
3. Select **Devices & services**
4. Find and click on **Dreo** integration
5. Click the three-dot menu (⋮) in the top-right corner of the Dreo card
6. Select **Download diagnostics**
7. Save the JSON file to your computer

These diagnostics files are specifically designed to help troubleshoot the Dreo integration while automatically redacting sensitive information.

## Adding New Products

Don't see your model listed above? Create an [issue](https://github.com/dreo-team/hass-dreoverse/issues) and I'll add it.

**Please make sure to include:**

- Model - in the format above (DR-XXX###X)
- Device type (fan, air conditioner, ceiling fan, humidifier, etc.)
- Number of speeds the device supports (not including "off")
- Does the device support oscillating/rotation?
- What preset modes are supported?
- Is temperature/humidity control supported?
- Additional features (lighting, smart follow, etc.)

Depending on answers, I may reach out and need you to pull some debug logs.

## Troubleshooting

### If HomeAssistant Doesn't Show Your Device

If you've installed the Dreo integration but your devices don't appear in HomeAssistant, follow these troubleshooting steps:

#### Step 1: Verify Basic Setup
- **Check Wi-Fi Connection**: Ensure your Dreo device is properly connected to your home Wi-Fi network
- **Test Mobile App**: Confirm the device works correctly in the Dreo mobile app
- **Verify Account**: Make sure you're using the exact same account credentials in HomeAssistant as in your Dreo mobile app
- **Restart Services**: Try restarting both your Dreo device and HomeAssistant instance

#### Step 2: Check Integration Installation
- Confirm the integration was installed properly:
  1. Go to **Settings** → **Devices & services**
  2. Look for "Dreo" in the list of integrations
  3. If not found, try adding it again following the [Initial Configuration](#initial-configuration) steps

#### Step 3: Enable Debugging
1. Add debug logging as described in the [Debugging](#debugging) section
2. Restart HomeAssistant
3. Try using your Dreo device through the mobile app to generate activity
4. Check logs for any information about your device

#### Step 4: Determine Support Status
Look for specific messages in your logs that indicate whether your device model is supported:

- If you see log entries related to your device but it still doesn't appear in the interface, there might be a connection or authentication issue
- If you see this message, your device model is detected but not yet supported:
  ```
  2023-06-29 01:02:25,312 - dreo - DEBUG - Received products for current unsupported device. SN: XXX341964289-77f2977b24191a4a:001:0000000000b
  ```

#### Reporting Unsupported Devices
If your device is not yet supported:

1. Collect the following information:
   - Your exact device model number (found on the device or packaging)
   - The device's firmware version (if available in the Dreo app)
   - Diagnostic information using [Option 2](#option-2-download-dreo-specific-diagnostics) above
   - Screenshots of the device in your Dreo mobile app (if possible)

2. [Create an issue](https://github.com/dreo-team/hass-dreoverse/issues/new) on GitHub with all the collected information

> **Note:** Our team is actively expanding device support. When reporting unsupported devices, please provide as much detail as possible to help us prioritize and implement support for your model in future updates.

## Acknowledgments

We would like to thank [Jeff Steinbok](https://github.com/JeffSteinbok) for his pioneering work on the unofficial Dreo integration at [https://github.com/JeffSteinbok/hass-dreo](https://github.com/JeffSteinbok/hass-dreo)

We also extend our gratitude to all community members who have supported the Dreo ecosystem through testing, feedback, and development.
