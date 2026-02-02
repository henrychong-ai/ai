# Browser Support Matrix for ECMAScript Versions

Minimum browser versions required for each ECMAScript target level.

**Sources:**
- [CanIUse.com](https://caniuse.com/?search=es2023)
- [kangax/compat-table](https://compat-table.github.io/compat-table/es6/)
- [ECMAScript Support Gist](https://gist.github.com/Julien-Marcou/156b19aea4704e1d2f48adafc6e2acbf)

---

## Browser Support by ES Version

### ES2024 (ES15)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 117 | Sep 2023 |
| Firefox | 119 | Oct 2023 |
| Safari | 17.4 | Mar 2024 |
| Edge | 117 | Sep 2023 |
| Opera | 103 | Sep 2023 |
| Samsung | 23 | Oct 2023 |

**Global Coverage:** ~85%

### ES2023 (ES14)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 97 | Jan 2022 |
| Firefox | 104 | Jun 2022 |
| Safari | 15.4 | Mar 2022 |
| Edge | 97 | Dec 2021 |
| Opera | 83 | Jan 2022 |
| Samsung | 18 | Aug 2022 |

**Global Coverage:** ~88%

### ES2022 (ES13) - RECOMMENDED DEFAULT

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 94 | Sep 2021 |
| Firefox | 93 | Oct 2021 |
| Safari | 15 | Sep 2021 |
| Edge | 94 | Sep 2021 |
| Opera | 80 | Sep 2021 |
| Samsung | 16 | Dec 2021 |

**Global Coverage:** ~88%

### ES2021 (ES12)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 85 | Aug 2020 |
| Firefox | 79 | Jul 2020 |
| Safari | 14 | Sep 2020 |
| Edge | 85 | Aug 2020 |
| Opera | 71 | Aug 2020 |
| Samsung | 14 | Dec 2020 |

**Global Coverage:** ~92%

### ES2020 (ES11)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 80 | Feb 2020 |
| Firefox | 74 | Mar 2020 |
| Safari | 13.1 | Mar 2020 |
| Edge | 80 | Feb 2020 |
| Opera | 67 | Mar 2020 |
| Samsung | 13 | Jun 2020 |

**Global Coverage:** ~93%

### ES2019 (ES10)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 73 | Mar 2019 |
| Firefox | 62 | Sep 2018 |
| Safari | 12 | Sep 2018 |
| Edge | 79 | Jan 2020 |
| Opera | 60 | Apr 2019 |
| Samsung | 11.1 | Mar 2019 |

**Global Coverage:** ~95%

### ES2018 (ES9)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 63 | Dec 2017 |
| Firefox | 58 | Jan 2018 |
| Safari | 11.1 | Mar 2018 |
| Edge | 79 | Jan 2020 |
| Opera | 50 | Jan 2018 |
| Samsung | 8.0 | Dec 2017 |

**Global Coverage:** ~96%

### ES2017 (ES8)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 55 | Dec 2016 |
| Firefox | 52 | Mar 2017 |
| Safari | 10.1 | Mar 2017 |
| Edge | 15 | Apr 2017 |
| Opera | 42 | Dec 2016 |
| Samsung | 6.0 | Mar 2017 |

**Global Coverage:** ~97%

### ES2016 (ES7)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 52 | Jul 2016 |
| Firefox | 48 | Aug 2016 |
| Safari | 10 | Sep 2016 |
| Edge | 14 | Aug 2016 |
| Opera | 39 | Aug 2016 |
| Samsung | 5.0 | Sep 2016 |

**Global Coverage:** ~98%

### ES2015 (ES6)

| Browser | Minimum Version | Release Date |
|---------|-----------------|--------------|
| Chrome | 51 | May 2016 |
| Firefox | 45 | Mar 2016 |
| Safari | 10 | Sep 2016 |
| Edge | 14 | Aug 2016 |
| Opera | 38 | Jun 2016 |
| Samsung | 5.0 | Sep 2016 |

**Global Coverage:** ~98%

---

## Not Supported Browsers

The following browsers do NOT support modern ECMAScript features:

| Browser | Last ES Support | Status |
|---------|-----------------|--------|
| Internet Explorer 11 | ES5 | EOL Jun 2022 |
| Opera Mini | ES5 | Limited JS |
| Legacy Edge (EdgeHTML) | ES2017 | EOL Mar 2021 |

---

## Browserslist Configuration

### ES2022 (Recommended Default)

```
# .browserslistrc
chrome >= 94
firefox >= 93
safari >= 15
edge >= 94
```

Or in package.json:

```json
{
  "browserslist": [
    "chrome >= 94",
    "firefox >= 93",
    "safari >= 15",
    "edge >= 94"
  ]
}
```

### ES2020 (Wide Compatibility)

```
# .browserslistrc
> 1%
last 2 versions
not dead
not ie 11
```

### ES2024 (Modern Only)

```
# .browserslistrc
chrome >= 117
firefox >= 119
safari >= 17.4
edge >= 117
```

---

## Feature-Specific Browser Support

Some ES features have different browser support than their version implies:

### Optional Chaining (?.) - ES2020

| Browser | Version |
|---------|---------|
| Chrome | 80 |
| Firefox | 74 |
| Safari | 13.1 |
| Edge | 80 |

### Nullish Coalescing (??) - ES2020

| Browser | Version |
|---------|---------|
| Chrome | 80 |
| Firefox | 72 |
| Safari | 13.1 |
| Edge | 80 |

### Private Class Fields (#) - ES2022

| Browser | Version |
|---------|---------|
| Chrome | 74 |
| Firefox | 90 |
| Safari | 14.1 |
| Edge | 79 |

### Top-Level Await - ES2022

| Browser | Version |
|---------|---------|
| Chrome | 89 |
| Firefox | 89 |
| Safari | 15 |
| Edge | 89 |

### Array.prototype.at() - ES2022

| Browser | Version |
|---------|---------|
| Chrome | 92 |
| Firefox | 90 |
| Safari | 15.4 |
| Edge | 92 |

### Change Array by Copy (toSorted, etc.) - ES2023

| Browser | Version |
|---------|---------|
| Chrome | 110 |
| Firefox | 115 |
| Safari | 16 |
| Edge | 110 |

### Object.groupBy() - ES2024

| Browser | Version |
|---------|---------|
| Chrome | 117 |
| Firefox | 119 |
| Safari | 17.4 |
| Edge | 117 |

---

## Recommendations by Use Case

| Use Case | ES Target | Browserslist | Notes |
|----------|-----------|--------------|-------|
| **Default (all projects)** | ES2022 | `>= 2021 browsers` | Best balance |
| **Modern web apps** | ES2022 | `last 2 versions, not dead` | Good coverage |
| **Internal tools** | ES2024 | `last 1 version` | Latest features |
| **Public websites** | ES2020 | `> 0.5%, not dead` | Wide reach |
| **Legacy support** | ES2017 | `> 0.1%` | Rare requirement |

---

## Checking Browser Support

### Using CanIUse

1. Visit [caniuse.com](https://caniuse.com)
2. Search for specific feature (e.g., "es2023")
3. Check browser version support

### Using browserslist

```bash
# Show which browsers match your config
npx browserslist

# Check coverage percentage
npx browserslist --coverage
```

### Using @mdn/browser-compat-data

For programmatic checks in build tools.

---

## Mobile Browser Considerations

Mobile browsers generally follow their desktop counterparts:

| Desktop | Mobile Equivalent |
|---------|-------------------|
| Chrome | Chrome for Android, Android WebView |
| Safari | Safari on iOS (all iOS browsers use WebKit) |
| Firefox | Firefox for Android |
| Edge | Edge for Android |
| Samsung | Samsung Internet |

**iOS Note:** All browsers on iOS use Safari's WebKit engine, so Safari's support level applies to all iOS browsers (Chrome iOS, Firefox iOS, etc.).
