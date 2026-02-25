# Frontend — React Native (Expo)

This is the mobile frontend for ContextMirror, built with [Expo](https://expo.dev) and React Native.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- A way to run the app — see the options below

## Setup

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the development server

   ```bash
   npx expo start
   ```

   This launches the Expo dev server and displays a QR code in your terminal.

## Running the app

Choose whichever option works best for you:

### Option 1: On your physical phone (recommended for quick testing)

1. Install the **Expo Go** app on your phone:
   - [Expo Go for iOS (App Store)](https://apps.apple.com/app/expo-go/id982107779)
   - [Expo Go for Android (Google Play)](https://play.google.com/store/apps/details?id=host.exp.exponent)
2. Run `npx expo start` and wait for the QR code to appear.
3. **iOS:** Open the Camera app and point it at the QR code — tap the banner that appears.
   **Android:** Open the Expo Go app and tap **Scan QR code**, then point it at the QR code.

> Your phone and development machine must be on the **same Wi-Fi network**.

### Option 2: iOS Simulator (macOS only)

Requires Xcode (free from the Mac App Store).

1. Install Xcode and open it at least once to accept the license agreement.
2. Run `npx expo start`, then press `i` in the terminal to open the iOS Simulator automatically.

See the [Expo iOS Simulator guide](https://docs.expo.dev/workflow/ios-simulator/) for detailed setup steps.

### Option 3: Android Emulator

Requires Android Studio.

1. Install [Android Studio](https://developer.android.com/studio) and set up a virtual device (AVD).
2. Run `npx expo start`, then press `a` in the terminal to open the Android Emulator automatically.

See the [Expo Android Emulator guide](https://docs.expo.dev/workflow/android-studio-emulator/) for detailed setup steps.

### Option 4: Web browser

Press `w` in the terminal after running `npx expo start` to open the app in your browser. Note that some native features may not work in the browser.

## Development

Edit files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction), so each file in `app/` maps directly to a route.

## Learn more

- [Expo documentation](https://docs.expo.dev/)
- [Expo Go overview](https://docs.expo.dev/get-started/expo-go/)
- [File-based routing](https://docs.expo.dev/router/introduction/)
