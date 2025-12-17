# Nexus Root Android Client

This directory contains the source code for the Android client of the Nexus Root MMORPG.

## Server Compatibility

This client is designed to connect to the backend server provided in this repository.

**Important**: The client assumes the server is running on `localhost:8080`.
- In the Android Emulator, `http://10.0.2.2:8080` is used to access the host's localhost.
- Ensure you start the server using the instructions in the root `README.md` (e.g., `python3 main.py server`).

## Client Architecture

This client is a "refactored" version of the client logic, implemented in **Kotlin** for Android.

- **Language**: Kotlin
- **Architecture**: MVVM (Model-View-ViewModel)
- **Networking**: Retrofit + OkHttp
- **Asynchronous Handling**: Kotlin Coroutines (`suspend` functions) + LiveData

## Setup

1. Open the `clients/android` directory in Android Studio.
2. The project uses standard Android Gradle plugins.
3. Dependencies included:
   - Retrofit 2.x
   - OkHttp 4.x
   - Kotlin Coroutines
   - AndroidX Core/AppCompat/Lifecycle/Activity

## Usage

1. **Start the Server**:
   Ensure the server is running on your host machine on port 8080.

2. **Run the App**:
   - Run the Android app on an Emulator.
   - The app automatically attempts to connect to the server.
   - If running on a physical device, ensure the device is on the same network and update `BASE_URL` in `NetworkClient.kt` to your computer's local IP.

## Features

- **Auto-Login**: Tries to register/login as `android_user` on startup.
- **Terminal Interface**: A simple command-line interface to execute game commands like `ls`, `status`, etc.
