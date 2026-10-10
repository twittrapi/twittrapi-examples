# Twitter/X API examples in Node.js

Plain JavaScript (ES modules, Node.js 18+) using the official [`twittrapi`](https://www.npmjs.com/package/twittrapi) package, which also ships TypeScript types.

> **Get an API key:** [twittrapi.com/start](https://twittrapi.com/start?utm_source=github&utm_medium=readme&utm_campaign=examples) · also available on [RapidAPI](https://rapidapi.com/viperscores-viperscores-default/api/twitter-aio)

```bash
cd node
npm install
export TWITTRAPI_API_KEY=your_key         # or: export RAPIDAPI_KEY=your_rapidapi_key
node twitter-user-lookup-by-username/lookup.mjs jack
```

`npm run check` syntax-checks every example and `npm run typecheck` type-checks them against the SDK's types (`checkJs`). [`_shared/extract.mjs`](_shared/extract.mjs) holds the small parser for X's raw JSON.

More examples in other languages: [README](../README.md)
