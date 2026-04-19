# Sound It Mobile Apps (iOS & Android)

This project uses **[Capacitor](https://capacitorjs.com)** to wrap the React web app into native iOS and Android apps. Capacitor provides access to native device APIs (camera, push notifications, geolocation, etc.) while keeping the web codebase as the single source of truth.

---

## 📱 Project Structure

```
app/
├── ios/                    # iOS native project (Xcode)
│   └── App/
│       ├── App.xcodeproj
│       └── App/
├── android/                # Android native project (Android Studio)
│   └── app/
│       └── src/main/
├── src/
│   ├── capacitor.ts        # Native bridge initialization
│   └── utils/share.ts      # Native share utility
├── capacitor.config.ts     # Capacitor configuration
└── package.json            # Mobile build scripts
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Frontend build |
| Xcode | 15+ | iOS builds |
| Android Studio | Ladybug+ | Android builds |
| CocoaPods | 1.12+ | iOS dependencies |
| Java JDK | 17+ | Android builds |

---

## Build Commands

All commands are run from the `app/` directory:

```bash
cd app
```

### iOS

```bash
# Build web app + sync to iOS + open Xcode
npm run mobile:ios

# Or manually:
npm run build
npx cap sync ios
npx cap open ios
```

In Xcode:
1. Select your target device (simulator or connected iPhone)
2. Press **Cmd+R** to build and run
3. For physical device: sign with your Apple Developer account

### Android

```bash
# Build web app + sync to Android + open Android Studio
npm run mobile:android

# Or manually:
npm run build
npx cap sync android
npx cap open android
```

In Android Studio:
1. Select a device (emulator or connected Android phone)
2. Press **Run** (▶) to build and deploy

### Live Reload (Development)

To develop with live reload on a device:

```bash
# Terminal 1: Start dev server
npm run dev

# Terminal 2: Sync with live reload URL
npx cap sync
npx cap run ios --livereload --external
# or
npx cap run android --livereload --external
```

---

## 🔌 Native Plugins Installed

| Plugin | Purpose |
|--------|---------|
| `@capacitor/status-bar` | Dark status bar styling |
| `@capacitor/splash-screen` | App launch splash screen |
| `@capacitor/camera` | Native camera for QR scanning |
| `@capacitor/share` | Native share sheet |
| `@capacitor/preferences` | Local key-value storage |

---

## 🔧 Configuration

### API URL for Mobile

The mobile app needs to connect to your backend. Update the API URL:

**For local testing:**
```bash
# Find your computer's IP
ipconfig getifaddr en0

# Set API URL to your computer's IP
VITE_API_URL=http://192.168.x.x:8000/api/v1 npm run build
```

**For production:**
Set `VITE_API_URL=https://api.sounditentsl.com/api/v1` in `app/.env.production` before building.

### CORS (Backend)

The backend already allows Capacitor origins:
- `capacitor://localhost` (iOS)
- `http://localhost` (Android)

For production, add your app bundle ID to `CORS_ORIGINS`:
```bash
CORS_ORIGINS="https://api.sounditentsl.com,capacitor://localhost,http://localhost"
```

---

## 🎨 Native Styling

The app is configured with:
- **Background color:** `#0A0A0A` (matches the web dark theme)
- **Status bar:** Dark style with matching background
- **Safe areas:** iOS notch and Android gesture areas handled automatically

---

## 📦 App Store Deployment

### iOS (App Store)

1. In Xcode: **Product → Archive**
2. Open Organizer: **Window → Organizer**
3. Select archive → **Distribute App**
4. Follow App Store Connect upload flow

### Android (Google Play)

1. In Android Studio: **Build → Generate Signed Bundle / APK**
2. Select **Android App Bundle (.aab)**
3. Upload to Google Play Console

---

## 🐛 Troubleshooting

**iOS build fails with CocoaPods error:**
```bash
cd ios/App && pod install
```

**Android build fails with Gradle error:**
```bash
cd android && ./gradlew clean
npx cap sync android
```

**Changes not reflecting in native app:**
```bash
npm run mobile:sync
```

**White screen after splash:**
- Check browser console for JS errors
- Ensure `dist/` is built: `npm run build`
- Check that `capacitor.config.ts` `webDir` is set to `dist`
