# Home LLM — Frontend

React 18 + TypeScript + Vite frontend for the Home LLM chat application.

## Prerequisites

- Node.js 20+
- A running instance of the [backend](../backend) at the URL configured in `.env`

## Setup

```bash
cp .env.example .env
# Edit .env — set VITE_API_BASE_URL and VITE_DEFAULT_MODEL
npm install
```

## Development

```bash
npm run dev
# Opens at http://localhost:3000
```

## Production build

```bash
npm run build
# Output in dist/
npm run preview   # preview the production build locally
```

## Docker

```bash
docker build -t home-llm-frontend .
docker run -p 80:80 home-llm-frontend
```

Or use the root `docker-compose.yml`.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL |
| `VITE_DEFAULT_MODEL` | `llama3.1` | Default LLM model name sent with each message |

## Tech stack

- **Vite** — build tool
- **React 18 + TypeScript** — UI
- **React Router v6** — routing (`/login`, `/register`, `/`, `/chat/:chatId`, `/settings`)
- **Zustand** — global state (auth token, chat list, streaming state)
- **TailwindCSS** — styling with dark mode (`class` strategy)
- **Axios** — API client with `Authorization` header injection and 401 redirect
- **react-markdown + remark-gfm + rehype-highlight** — Markdown + syntax highlighting in assistant messages
- **Lucide React** — icon set
- **Sonner** — toast notifications

## Streaming

The assistant reply arrives via **Server-Sent Events** (SSE) from `GET /chats/{id}/stream`.  
Because the native `EventSource` API cannot send `Authorization` headers, the app uses a
`fetch`-based SSE reader (`src/api/stream.ts`) that passes the JWT as a normal request header.  
All SSE parsing logic is isolated in `parseStreamEvent()` — a one-line change there handles any
backend payload format change.


## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
