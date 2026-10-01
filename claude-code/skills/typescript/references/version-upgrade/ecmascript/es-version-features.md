# ECMAScript Version Features Reference

Feature list by ECMAScript edition, ES5 through ES2026. Editions are approved by Ecma each June; check https://tc39.es/ecma262/ and the finished-proposals list (https://github.com/tc39/proposals/blob/main/finished-proposals.md) for the current edition.

**Sources:**
- [ECMAScript-features GitHub](https://github.com/sudheerj/ECMAScript-features)
- [Exploring JavaScript ES2025 Edition](https://exploringjs.com/js/book/ch_new-javascript-features.html)
- [ECMAScript version history - Wikipedia](https://en.wikipedia.org/wiki/ECMAScript_version_history)

---

## ES5 (December 2009)

The foundational modern JavaScript version after a decade-long gap from ES3.

| Feature | Description |
|---------|-------------|
| **Strict Mode** | `"use strict"` directive for safer code |
| **JSON Support** | `JSON.parse()` and `JSON.stringify()` |
| **Object.create()** | Create objects with specified prototype |
| **Object.defineProperty()** | Define property with getters/setters |
| **Object.keys()** | Get array of own property names |
| **Array.isArray()** | Check if value is an array |
| **Array.prototype.forEach()** | Iterate over array elements |
| **Array.prototype.map()** | Transform array elements |
| **Array.prototype.filter()** | Filter array elements |
| **Array.prototype.reduce()** | Reduce array to single value |
| **Array.prototype.reduceRight()** | Reduce from right to left |
| **Array.prototype.every()** | Test if all elements pass |
| **Array.prototype.some()** | Test if any element passes |
| **Array.prototype.indexOf()** | Find index of element |
| **Array.prototype.lastIndexOf()** | Find last index of element |
| **Function.prototype.bind()** | Bind function to context |
| **String.prototype.trim()** | Remove whitespace from ends |
| **Date.now()** | Get current timestamp |
| **Getter/Setter Syntax** | `get` and `set` in object literals |

---

## ES2015 / ES6 (June 2015)

The largest update in JavaScript history. Renamed from ES6 to ES2015 for yearly versioning.

| Feature | Description | Example |
|---------|-------------|---------|
| **let** | Block-scoped variable declaration | `let x = 1;` |
| **const** | Block-scoped constant declaration | `const PI = 3.14;` |
| **Arrow Functions** | Concise function syntax with lexical `this` | `(x) => x * 2` |
| **Classes** | Syntactic sugar for prototype inheritance | `class Foo extends Bar {}` |
| **Template Literals** | String interpolation with backticks | `` `Hello ${name}` `` |
| **Destructuring** | Extract values from objects/arrays | `const {a, b} = obj;` |
| **Default Parameters** | Function parameters with defaults | `function(x = 10) {}` |
| **Rest Parameters** | Collect remaining arguments | `function(...args) {}` |
| **Spread Operator** | Expand iterables | `[...arr1, ...arr2]` |
| **for...of** | Iterate over iterable values | `for (const x of arr) {}` |
| **Modules** | Import/export syntax | `import { foo } from 'mod';` |
| **Promises** | Async operation handling | `new Promise((resolve, reject) => {})` |
| **Symbol** | Unique immutable identifiers | `Symbol('description')` |
| **Map** | Key-value collection | `new Map()` |
| **Set** | Collection of unique values | `new Set()` |
| **WeakMap** | Map with weak object keys | `new WeakMap()` |
| **WeakSet** | Set with weak object references | `new WeakSet()` |
| **Iterators** | Custom iteration protocol | `[Symbol.iterator]()` |
| **Generators** | Pausable functions | `function* gen() { yield 1; }` |
| **Proxy** | Intercept object operations | `new Proxy(target, handler)` |
| **Reflect** | Object operation methods | `Reflect.get(obj, 'prop')` |
| **Binary/Octal Literals** | Number literal formats | `0b1010`, `0o755` |
| **Enhanced Object Literals** | Shorthand properties/methods | `{ x, fn() {} }` |
| **Computed Property Names** | Dynamic property keys | `{ [expr]: value }` |

**Cannot be polyfilled:** Proxy, Symbol (partial), Generators (require transpilation)

---

## ES2016 / ES7 (June 2016)

Small, focused release with only 2 features.

| Feature | Description | Example |
|---------|-------------|---------|
| **Array.prototype.includes()** | Check array membership | `arr.includes(value)` |
| **Exponentiation Operator** | Power calculation | `2 ** 10` → `1024` |

---

## ES2017 / ES8 (June 2017)

Introduced async/await for cleaner asynchronous code.

| Feature | Description | Example |
|---------|-------------|---------|
| **async/await** | Simplified async syntax | `async function() { await promise; }` |
| **Object.values()** | Get object values as array | `Object.values({a:1})` → `[1]` |
| **Object.entries()** | Get key-value pairs | `Object.entries({a:1})` → `[['a',1]]` |
| **Object.getOwnPropertyDescriptors()** | Get all property descriptors | `Object.getOwnPropertyDescriptors(obj)` |
| **String.prototype.padStart()** | Pad string from start | `'5'.padStart(2, '0')` → `'05'` |
| **String.prototype.padEnd()** | Pad string from end | `'5'.padEnd(2, '0')` → `'50'` |
| **Trailing Commas** | Allow trailing commas in params | `function(a, b,) {}` |
| **SharedArrayBuffer** | Shared memory for workers | `new SharedArrayBuffer(1024)` |
| **Atomics** | Atomic operations on shared memory | `Atomics.add(arr, 0, 1)` |

**Note:** async/await requires transpilation for ES5/ES2015 targets.

---

## ES2018 / ES9 (June 2018)

Extended rest/spread to objects and added async iteration.

| Feature | Description | Example |
|---------|-------------|---------|
| **Object Rest Properties** | Rest syntax for objects | `const {a, ...rest} = obj;` |
| **Object Spread Properties** | Spread syntax for objects | `{...obj1, ...obj2}` |
| **Async Iteration** | for-await-of loops | `for await (const x of asyncGen) {}` |
| **Promise.prototype.finally()** | Execute after settle | `promise.finally(() => {})` |
| **RegExp Named Capture Groups** | Named groups in regex | `/(?<year>\d{4})/` |
| **RegExp Lookbehind Assertions** | Lookbehind in regex | `/(?<=\$)\d+/` |
| **RegExp Unicode Property Escapes** | Unicode categories | `/\p{Script=Greek}/u` |
| **RegExp s (dotAll) Flag** | Dot matches newlines | `/foo.bar/s` |

**Cannot be polyfilled:** RegExp features (lookbehind, named groups, Unicode properties)

---

## ES2019 / ES10 (June 2019)

Quality-of-life improvements for arrays, objects, and strings.

| Feature | Description | Example |
|---------|-------------|---------|
| **Array.prototype.flat()** | Flatten nested arrays | `[[1,2],[3]].flat()` → `[1,2,3]` |
| **Array.prototype.flatMap()** | Map then flatten | `arr.flatMap(x => [x, x*2])` |
| **Object.fromEntries()** | Create object from entries | `Object.fromEntries([['a',1]])` |
| **String.prototype.trimStart()** | Trim leading whitespace | `'  foo'.trimStart()` |
| **String.prototype.trimEnd()** | Trim trailing whitespace | `'foo  '.trimEnd()` |
| **Symbol.prototype.description** | Get symbol description | `Symbol('foo').description` |
| **Optional Catch Binding** | Omit catch parameter | `try {} catch {}` |
| **JSON Superset** | Allow U+2028/U+2029 in strings | JSON ⊂ ECMAScript |
| **Well-formed JSON.stringify** | Proper Unicode handling | No lone surrogates |
| **Function.prototype.toString()** | Exact source code | Preserves whitespace/comments |
| **Array.prototype.sort() Stability** | Guaranteed stable sort | Preserves equal element order |

---

## ES2020 / ES11 (June 2020)

Major quality-of-life features: optional chaining and nullish coalescing.

| Feature | Description | Example |
|---------|-------------|---------|
| **Optional Chaining (?.)** | Safe property access | `obj?.prop?.nested` |
| **Nullish Coalescing (??)** | Default for null/undefined | `value ?? 'default'` |
| **BigInt** | Arbitrary precision integers | `9007199254740993n` |
| **Dynamic Import** | Runtime module loading | `await import('./module.js')` |
| **Promise.allSettled()** | Wait for all promises | `Promise.allSettled([p1, p2])` |
| **String.prototype.matchAll()** | All regex matches | `str.matchAll(/\d+/g)` |
| **globalThis** | Universal global object | `globalThis.setTimeout` |
| **import.meta** | Module metadata | `import.meta.url` |
| **export * as ns** | Namespace re-export | `export * as utils from './utils';` |
| **for-in Order** | Guaranteed enumeration order | Spec-defined order |

**Cannot be polyfilled:** BigInt arithmetic operations (comparison can be polyfilled)

---

## ES2021 / ES12 (June 2021)

String improvements and logical assignment operators.

| Feature | Description | Example |
|---------|-------------|---------|
| **String.prototype.replaceAll()** | Replace all occurrences | `'aaa'.replaceAll('a', 'b')` → `'bbb'` |
| **Promise.any()** | First fulfilled promise | `Promise.any([p1, p2])` |
| **WeakRef** | Weak reference to object | `new WeakRef(obj)` |
| **FinalizationRegistry** | Cleanup callbacks | `new FinalizationRegistry(cb)` |
| **Logical Assignment (||=)** | Or-assign | `x ||= default` |
| **Logical Assignment (&&=)** | And-assign | `x &&= value` |
| **Logical Assignment (??=)** | Nullish-assign | `x ??= default` |
| **Numeric Separators** | Underscore in numbers | `1_000_000` |

**Cannot be polyfilled or transpiled:** WeakRef, FinalizationRegistry (garbage-collector features)

---

## ES2022 / ES13 (June 2022)

Supported by every maintained Node line and by all current browsers.

| Feature | Description | Example |
|---------|-------------|---------|
| **Top-Level Await** | await outside async functions | `const data = await fetch(url);` |
| **Class Fields (Public)** | Declare fields in class body | `class Foo { x = 1; }` |
| **Class Fields (Private)** | Private with # prefix | `class Foo { #private = 1; }` |
| **Private Methods** | Private methods with # | `class Foo { #method() {} }` |
| **Static Class Fields** | Static properties | `class Foo { static x = 1; }` |
| **Static Initialization Blocks** | Static class initialization | `class Foo { static { /* init */ } }` |
| **Array.prototype.at()** | Index from start or end | `arr.at(-1)` → last element |
| **String.prototype.at()** | Character at index | `'abc'.at(-1)` → `'c'` |
| **Object.hasOwn()** | Check own property | `Object.hasOwn(obj, 'prop')` |
| **Error.cause** | Attach error context | `new Error('msg', { cause: err })` |
| **RegExp Match Indices** | /d flag for positions | `/a+/d.exec('aaa').indices` |

**Down-levelling:** TypeScript transpiles class fields and private `#fields` (via WeakMaps) for lower targets. Top-level await cannot be transpiled — it needs an ES-module runtime.

---

## ES2023 / ES14 (June 2023)

Non-mutating array methods and enhanced search.

| Feature | Description | Example |
|---------|-------------|---------|
| **Array.prototype.findLast()** | Find from end | `arr.findLast(x => x > 0)` |
| **Array.prototype.findLastIndex()** | Find index from end | `arr.findLastIndex(x => x > 0)` |
| **Array.prototype.toReversed()** | Non-mutating reverse | `arr.toReversed()` |
| **Array.prototype.toSorted()** | Non-mutating sort | `arr.toSorted()` |
| **Array.prototype.toSpliced()** | Non-mutating splice | `arr.toSpliced(1, 1, 'new')` |
| **Array.prototype.with()** | Non-mutating index set | `arr.with(0, 'new')` |
| **Hashbang Syntax** | Unix shebang support | `#!/usr/bin/env node` |
| **Symbols as WeakMap Keys** | Symbol keys in WeakMap | `weakMap.set(Symbol(), value)` |

**TypeScript requirement:** TypeScript 5.5+ required for ES2023 target

---

## ES2024 / ES15 (June 2024)

Grouping, better Unicode, and Promise improvements.

| Feature | Description | Example |
|---------|-------------|---------|
| **Object.groupBy()** | Group into object | `Object.groupBy(arr, x => x.type)` |
| **Map.groupBy()** | Group into Map | `Map.groupBy(arr, x => x.type)` |
| **Promise.withResolvers()** | Externalize resolve/reject | `const {promise, resolve} = Promise.withResolvers()` |
| **String.prototype.isWellFormed()** | Check valid Unicode | `str.isWellFormed()` |
| **String.prototype.toWellFormed()** | Fix invalid Unicode | `str.toWellFormed()` |
| **RegExp v Flag** | Unicode set notation | `/[\p{Letter}--[a-z]]/v` |
| **Atomics.waitAsync()** | Async atomic wait | `Atomics.waitAsync(arr, 0, 0)` |
| **ArrayBuffer.prototype.resize()** | Resizable array buffers | `buffer.resize(1024)` |
| **ArrayBuffer.prototype.transfer()** | Transfer ownership | `buffer.transfer()` |

**TypeScript requirement:** TypeScript 5.7+ required for ES2024 target

---

## ES2025 / ES16 (June 2025)

| Feature | Example |
|---------|---------|
| **Iterator helpers** | `iter.map(f).filter(g).take(3).toArray()` |
| **Set methods** | `a.union(b)`, `a.intersection(b)`, `a.difference(b)`, `a.isSubsetOf(b)` |
| **Import attributes and JSON modules** | `import data from './d.json' with { type: 'json' }` |
| **`RegExp.escape()`** | `new RegExp(RegExp.escape(userText))` |
| **RegExp pattern modifiers** | `/(?i:abc)def/` |
| **Duplicate named capture groups** | The same group name in different alternatives of one pattern |
| **`Promise.try()`** | `Promise.try(() => maybeSync())` |
| **`Float16Array`, `Math.f16round()`** | Half-precision floats |

**TypeScript requirement:** TypeScript 6.0+ for the `es2025` target and lib. Node 24 and 26 support the edition.

---

## ES2026 / ES17 (June 2026)

Approved by the Ecma General Assembly on 2026-06-30. Highlights (verify the full list against the spec before relying on one):

| Feature | Notes |
|---------|-------|
| **Temporal** | Modern date/time API; enabled by default in Node 26 |
| **Explicit resource management** | `using` / `await using` declarations, `Symbol.dispose` |
| **`Array.fromAsync()`** | Build an array from an async iterable |
| **Map upsert** | `map.getOrInsert()`, `map.getOrInsertComputed()` |
| **`Error.isError()`, `Math.sumPrecise()`, `Uint8Array` base64/hex** | Smaller built-in additions |

TypeScript exposes these through `lib: ["esnext"]` or specific `esnext.*` libs until an `es2026` target exists; check `tsc --target es2026` on your compiler before using it.

---

## Native, Transpiled, Polyfilled or Impossible

When the runtime is older than the feature, one of four things applies:

| Category | How it reaches an older runtime | Examples |
|---|---|---|
| **Syntax** | Transpiled by TypeScript, SWC, esbuild or Babel when `target` is lower | `?.`, `??`, `async`/`await`, arrow functions, classes, class fields, private `#fields`, static blocks, `**` |
| **Built-in APIs** | Polyfilled (core-js), because the method is missing at runtime, not a syntax error | `Array.prototype.at`/`findLast`/`toSorted`, `Object.groupBy`, `Promise.withResolvers`, `Set` methods, `String.prototype.replaceAll` |
| **Engine features** | Impossible — no transpile or polyfill reproduces them | `Proxy`, `WeakRef`/`FinalizationRegistry`, BigInt arithmetic, RegExp lookbehind/named groups/`v` flag/modifiers, `SharedArrayBuffer`/`Atomics` |
| **Module-system features** | Need an ES-module runtime | Top-level await, import attributes |

Transpiling syntax costs bundle size and sometimes semantics (class field define semantics — see `es-upgrade-checklist.md`); raising the target removes that cost only when every runtime supports the syntax natively.

---

## Choosing a target

Choose from the runtime, not from this list: use the Node mapping in `es-upgrade-checklist.md` for server code and the browser floor in `browser-support.md` for front ends. The recommended default target is in `../../coding-standards/tooling.md` (tsconfig `target`/`lib`).
