# iOS App Build Template - Complete Guide

Use this template when building a new iOS app with Claude Code. This ensures all necessary components are included from the start.

---

## App Requirements Prompt

```
Build a [APP TYPE] iOS app called "[APP NAME]" using React Native with Expo SDK 54.

### Core Features:
- [List main features]
- [Feature 2]
- [Feature 3]

### Technical Stack:
- React Native with Expo (SDK 54+)
- TypeScript
- Expo Router for navigation
- Zustand for state management (with AsyncStorage persistence)
- expo-av for audio
- expo-haptics for vibrations
- expo-keep-awake (if needed)

### Monetization (INCLUDE FROM START):
1. **RevenueCat Integration**
   - Install: react-native-purchases, react-native-purchases-ui
   - Create purchaseService.ts with:
     - initializePurchases()
     - checkPremiumStatus()
     - getOfferings()
     - purchasePackage()
     - restorePurchases()
   - Use PRODUCTION API key (starts with 'appl_')
   - Set up entitlements in RevenueCat dashboard

2. **Google AdMob Integration**
   - Install: react-native-google-mobile-ads
   - Create adService.ts with:
     - initializeAds()
     - loadRewardedAd()
     - showRewardedAd()
     - getBannerAdUnitId()
   - Add to app.json plugins with App ID
   - Create BannerAd component

3. **In-App Purchase Products** (set up in App Store Connect):
   - [product_id_monthly] - Monthly subscription
   - [product_id_yearly] - Yearly subscription
   - [product_id_lifetime] - Lifetime (non-consumable)

4. **Credits/Freemium System** (if applicable):
   - Free credits per day
   - Watch ads for bonus credits
   - Premium = unlimited

### App Store Requirements (PREPARE FROM START):

1. **Bundle ID**: com.[company].[appname]

2. **Assets Required**:
   - App icon: 1024x1024 PNG (no transparency, no rounded corners)
   - Splash screen image
   - Screenshots:

3. **App Icon Generation Prompt (for Grok/AI image generators)**:
   ```
   Create an app icon for "[APP NAME]" - a [APP DESCRIPTION] iOS app.

   Requirements:
   - Square format, suitable for 1024x1024 iOS app icon
   - Simple, recognizable design that works at small sizes
   - [MASCOT/SYMBOL] as the central element
   - Color palette: [PRIMARY COLOR] with [ACCENT COLOR] accents
   - Modern, clean aesthetic
   - NO text on the icon
   - NO rounded corners (iOS adds these automatically)
   - Solid or gradient background (no transparency)
   - [SPECIFIC STYLE: e.g., "friendly cartoon style", "minimalist", "3D rendered"]

   The icon should convey [EMOTION/FEELING] and appeal to [TARGET AUDIENCE].
   ```

   **Splash Screen Prompt**:
   ```
   Create a splash screen for "[APP NAME]" iOS app.

   Requirements:
   - Portrait orientation (1284x2778 pixels)
   - Same [MASCOT/SYMBOL] character from the app icon
   - App name "[APP NAME]" in clean, modern typography below the mascot
   - Background color: [HEX COLOR matching app theme]
   - Centered composition
   - [SPECIFIC STYLE matching icon]
   ```

   **Example (Owlet Tabata Timer)**:
   ```
   Create an app icon for "Owlet" - a Tabata interval timer iOS app.

   Requirements:
   - Square format, suitable for 1024x1024 iOS app icon
   - Cute, friendly owl as the central character
   - The owl should have a sporty/athletic feel (suggesting fitness)
   - Incorporate a subtle timer/stopwatch element (like a ring around the owl)
   - Color palette: Dark navy background (#1A1A2E) with amber/orange accents (#FFB800, #FF6B35)
   - The owl's eyes should be amber/golden
   - Modern, clean aesthetic with slight 3D depth
   - NO text on the icon
   - NO rounded corners
   - Friendly cartoon style, appealing to fitness enthusiasts

   The icon should convey energy, motivation, and approachability.
   ```

4. **Screenshot Sizes**:
   - 6.7" (1290x2796) - iPhone 15 Pro Max
   - 6.5" (1242x2688) - iPhone 11 Pro Max

5. **Legal Pages** (create on website):
   - Privacy Policy: https://[domain]/[app]/privacy
   - Support: https://[domain]/[app]/support
   - Terms of Service: https://[domain]/[app]/terms

4. **App Store Listing Content**:
   - App name (30 chars max)
   - Subtitle (30 chars max)
   - Description (4000 chars max)
   - Keywords (100 chars max, comma-separated)
   - Primary category
   - Age rating questionnaire answers
   - Copyright holder

5. **App Privacy (Data Collection)**:
   - RevenueCat collects: Purchase History
   - AdMob collects: Device ID, Advertising Data
   - Analytics collects: Product Interaction
   - Prepare answers for Apple's privacy questionnaire

### Configuration Files:

1. **app.json** - Include:
   ```json
   {
     "expo": {
       "name": "App Name",
       "slug": "app-slug",
       "version": "1.0.0",
       "ios": {
         "bundleIdentifier": "com.company.appname",
         "buildNumber": "1",
         "supportsTablet": false,
         "infoPlist": {
           "NSUserTrackingUsageDescription": "This allows us to show you relevant ads and improve your experience."
         }
       },
       "plugins": [
         ["react-native-google-mobile-ads", {
           "iosAppId": "ca-app-pub-XXXXXXXX~XXXXXXXX"
         }]
       ]
     }
   }
   ```

2. **eas.json** - Build configuration:
   ```json
   {
     "cli": { "version": ">= 5.0.0" },
     "build": {
       "development": {
         "developmentClient": true,
         "distribution": "internal",
         "ios": { "simulator": true }
       },
       "preview": {
         "distribution": "internal"
       },
       "production": {
         "autoIncrement": true
       }
     },
     "submit": {
       "production": {
         "ios": {
           "appleId": "your@email.com"
         }
       }
     }
   }
   ```

### Folder Structure:
```
/app
  /_layout.tsx (root layout - initialize services here)
  /(tabs)
    /_layout.tsx
    /index.tsx (home)
    /[other tabs].tsx
  /paywall.tsx
  /[other screens].tsx
/components
  /BannerAd.tsx
  /[other components].tsx
/utils
  /adService.ts
  /purchaseService.ts
  /[other utils].ts
/store
  /[zustand stores].ts
/constants
  /theme.ts
/assets
  /icon.png
  /splash-icon.png
  /[other assets]
```

### Pre-Launch Checklist:

#### Apple Developer Setup:
- [ ] Create App ID with bundle identifier
- [ ] Enable In-App Purchase capability
- [ ] Enable Push Notifications (optional)
- [ ] Create app in App Store Connect
- [ ] Note the Apple ID (for website links)

#### RevenueCat Setup:
- [ ] Create project
- [ ] Add iOS app with bundle ID
- [ ] Upload App Store Connect API key (.p8 file)
- [ ] Create products matching App Store Connect IDs
- [ ] Create entitlement (e.g., "Pro")
- [ ] Create offering with packages (monthly, yearly, lifetime)
- [ ] Get production API key (appl_XXXXX)

#### App Store Connect Setup:
- [ ] Create subscription group
- [ ] Add monthly subscription with localization
- [ ] Add yearly subscription with localization
- [ ] Add lifetime in-app purchase with localization
- [ ] Set pricing for all products
- [ ] Set availability (countries)

#### AdMob Setup:
- [ ] Create app in AdMob
- [ ] Create rewarded ad unit
- [ ] Create banner ad unit
- [ ] Note App ID and Ad Unit IDs

#### Build & Submit:
- [ ] Run: eas build --platform ios --profile production
- [ ] Run: eas submit --platform ios --latest
- [ ] Test on TestFlight
- [ ] Fill in App Store listing
- [ ] Complete App Privacy questionnaire
- [ ] Complete Age Rating questionnaire
- [ ] Add screenshots
- [ ] Add build to version
- [ ] Submit for review

### Commands Reference:
```bash
# Initialize EAS
eas init

# Build for production
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios --latest

# Resize icon to 1024x1024
sips -z 1024 1024 icon.png --out icon.png

# Resize screenshots
sips -z 2796 1290 screenshot.png --out screenshot_6.7.png
sips -z 2688 1242 screenshot.png --out screenshot_6.5.png
```
```

---

## App Store Listing Templates

### App Name (30 chars max)
```
[App Name] - [Key Benefit]
```
Examples:
- Owlet - Tabata Timer
- Sudoku Owl - Daily Puzzles

### Subtitle (30 chars max)
```
[Short value proposition]
```
Examples:
- HIIT Interval Training
- Brain Training & Streaks

### Description Template (4000 chars max)
```
[APP NAME] is your [ADJECTIVE] [WHAT IT IS]. [ONE SENTENCE VALUE PROP].

[WHAT IS IT / HOW IT WORKS SECTION]
[Explain the core concept in 2-3 sentences for users unfamiliar with it]

FEATURES:
• [Feature 1] - [Brief benefit]
• [Feature 2] - [Brief benefit]
• [Feature 3] - [Brief benefit]
• [Feature 4] - [Brief benefit]
• [Feature 5] - [Brief benefit]
• [Feature 6] - [Brief benefit]

PREMIUM FEATURES:
• Unlimited [main feature]
• No advertisements
• All future features included

[CLOSING PARAGRAPH - Who it's for and call to action]

Download now and [start your journey / begin your experience]!
```

### Keywords (100 chars max, comma-separated)
```
[primary keyword],[secondary],[tertiary],[related],[related],[related],[related],[related],[related],[related]
```
Tips:
- Don't repeat words from app name (Apple already indexes those)
- Use singular forms (Apple matches plurals automatically)
- No spaces after commas to save characters
- Research competitor keywords

### Example (Owlet):
**Name:** Owlet - Tabata Timer
**Subtitle:** HIIT Interval Training
**Keywords:** tabata,hiit,timer,workout,fitness,interval,training,exercise,gym,health
**Description:** [See full description we used above]

---

## Website Landing Page (goowldigital.com)

All apps will be hosted on **goowldigital.com/[app-name]/**

### Required Pages:
```
/[app-name]/index.html      - Main landing page
/[app-name]/privacy.html    - Privacy Policy
/[app-name]/support.html    - Support/FAQ page
/[app-name]/terms.html      - Terms of Service
/[app-name]/app-icon.png    - App icon for website
```

### Landing Page Structure (index.html):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>[App Name] - [Tagline] | Go Owl Digital</title>
    <meta name="description" content="[App description for SEO]">
    <meta name="keywords" content="[keywords]">
    <!-- Open Graph -->
    <meta property="og:title" content="[App Name] - [Tagline]">
    <meta property="og:description" content="[Description]">
    <meta property="og:image" content="https://goowldigital.com/[app-name]/og-image.png">
</head>
<body>
    <!-- HEADER -->
    <header>
        <a href="/" class="logo">GO OWL <span>DIGITAL</span></a>
        <nav>
            <a href="#features">Features</a>
            <a href="support">Support</a>
            <a href="privacy">Privacy</a>
        </nav>
    </header>

    <!-- HERO SECTION -->
    <section class="hero">
        <img src="app-icon.png" alt="[App Name] App Icon" class="app-icon">
        <h1>[App Name]</h1>
        <p class="tagline">[Tagline/Subtitle]</p>
        <div class="cta-buttons">
            <a href="https://apps.apple.com/app/id[APP_ID]" class="btn btn-appstore">
                <!-- Apple logo SVG -->
                <div class="btn-text">
                    <small>Download on the</small>
                    <span>App Store</span>
                </div>
            </a>
        </div>
    </section>

    <!-- FEATURES SECTION -->
    <section class="features" id="features">
        <h2>[Features Headline]</h2>
        <div class="features-grid">
            <!-- 6 feature cards with emoji icons -->
            <div class="feature-card">
                <div class="feature-icon">[EMOJI]</div>
                <h3>[Feature Name]</h3>
                <p>[Feature description]</p>
            </div>
            <!-- Repeat for each feature -->
        </div>
    </section>

    <!-- HOW IT WORKS (optional) -->
    <section class="how-it-works">
        <h2>How It Works</h2>
        <div class="steps">
            <!-- 3-4 steps -->
        </div>
    </section>

    <!-- FOOTER -->
    <footer>
        <div class="footer-links">
            <a href="support">Support</a>
            <a href="privacy">Privacy Policy</a>
            <a href="terms">Terms of Service</a>
            <a href="mailto:walsh688@gmail.com">Contact</a>
        </div>
        <div class="footer-links">
            <span>Our Apps:</span>
            <a href="/owlet">Owlet - Tabata Timer</a>
            <a href="/sudoku-owl">Sudoku Owl</a>
            <a href="/[new-app]">[New App Name]</a>
        </div>
        <p class="copyright">&copy; 2026 Go Owl Digital. All rights reserved.</p>
    </footer>
</body>
</html>
```

### Privacy Policy Template (privacy.html):
```
Privacy Policy for [App Name]
Last updated: [Date]

[App Name] is developed by Go Owl Digital.

INFORMATION WE COLLECT:
- Purchase history (via RevenueCat) for subscription management
- Advertising identifiers (via Google AdMob) to show relevant ads
- Basic usage analytics to improve the app

INFORMATION WE DON'T COLLECT:
- Personal information (name, email, etc.)
- Location data
- Contacts or photos

THIRD-PARTY SERVICES:
- RevenueCat (purchases): https://www.revenuecat.com/privacy
- Google AdMob (advertising): https://policies.google.com/privacy

DATA STORAGE:
All app data (settings, history, etc.) is stored locally on your device.

CONTACT:
walsh688@gmail.com
https://goowldigital.com/[app-name]/support
```

### Support Page Template (support.html):
```
Support for [App Name]

FREQUENTLY ASKED QUESTIONS:

Q: How do I [common question 1]?
A: [Answer]

Q: How do I restore my purchase?
A: Go to Settings > Restore Purchases. Your subscription will be restored if you have an active subscription linked to your Apple ID.

Q: How do I cancel my subscription?
A: Subscriptions are managed through Apple. Go to Settings > Apple ID > Subscriptions on your iPhone.

Q: [App-specific question]?
A: [Answer]

CONTACT US:
Email: walsh688@gmail.com

We typically respond within 24-48 hours.
```

### After App Approval - Update Website:
1. Change "Coming Soon on the App Store" to "Download on the App Store"
2. Update href="#" to actual App Store link: https://apps.apple.com/app/id[APP_ID]
3. Add new app to footer links on ALL app pages (owlet, sudoku-owl, etc.)

### Git Commands for Website Updates:
```bash
cd /Users/littlemoons/goowldigital

# Create new app folder
mkdir [app-name]

# Copy template files or create new ones
# Edit index.html, privacy.html, support.html, terms.html

# Add app icon
cp /path/to/icon.png [app-name]/app-icon.png

# Commit and push
git add -A
git commit -m "Add [App Name] landing page and support files"
git push
```

---

## Marketing Copy Templates

### App Store Promotional Text (170 chars, can be updated without review):
```
[Current promotion or seasonal message]. [Key benefit]. [Call to action]!
```
Examples:
- New Year, New You! Get fit in just 4 minutes with Tabata training. Download free today!
- Summer body goals? Burn maximum calories in minimum time. Start your fitness journey!

### Social Media Templates:

**Twitter/X (280 chars):**
```
[EMOJI] Introducing [App Name]!

[One sentence about what it does]

[EMOJI] [Key feature 1]
[EMOJI] [Key feature 2]
[EMOJI] [Key feature 3]

Download free: [App Store link]

#[hashtag] #[hashtag] #iOS #app
```

**Instagram Caption:**
```
[App Name] is here! [EMOJI]

[2-3 sentences about the app and who it's for]

Key features:
[EMOJI] [Feature 1]
[EMOJI] [Feature 2]
[EMOJI] [Feature 3]
[EMOJI] [Feature 4]

Link in bio to download free!

#[hashtag] #[hashtag] #[hashtag] #iosapp #appstore #[niche]
```

### Press/Review Outreach Template:
```
Subject: [App Name] - [Brief hook] (iOS App)

Hi [Name],

I'm Liam from Go Owl Digital. I've just launched [App Name], a [description] app for iOS.

What makes it different:
- [Unique selling point 1]
- [Unique selling point 2]
- [Unique selling point 3]

I'd love to offer you a promo code for premium access to review it.

App Store: https://apps.apple.com/app/id[APP_ID]
Website: https://goowldigital.com/[app-name]
Press kit: [if available]

Thanks,
Liam Walsh
Go Owl Digital
walsh688@gmail.com
```

---

## Quick Start for New App

1. Copy this template
2. Fill in the bracketed values [APP NAME], [product_id], etc.
3. Give to Claude Code with your specific requirements
4. Claude will build with monetization included from the start
5. Generate app icon with Grok using the icon prompt template
6. Create website pages on goowldigital.com/[app-name]/
7. Follow pre-launch checklist before submitting
8. Update all app footers to include new app link after launch
