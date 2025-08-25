---
applyTo: "{frontend/**/*.{vue,ts,js}}"
---

# AI Agent Frontend

Vue.js-based frontend for the AI Agent system with real-time chat, session management, and VNC visualization.

## 🚀 Features

- **Vue.js 3**: Modern reactive framework with Composition API
- **TypeScript**: Full type safety and better development experience
- **Real-time Chat**: Server-Sent Events (SSE) for live updates
- **Session Management**: Create, manage, and delete conversation sessions
- **VNC Visualization**: Remote desktop viewing for browser automation
- **Tool Panel**: Access to various MCP tools and integrations
- **Responsive Design**: Mobile-friendly interface
- **Markdown Support**: Rich text rendering with syntax highlighting

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── components/      # Reusable Vue components
│   │   ├── ChatInput.vue    # Message input component
│   │   ├── ChatMessage.vue  # Message display component
│   │   ├── Sidebar.vue      # Session sidebar
│   │   ├── ToolPanel.vue    # Tool management panel
│   │   └── ui/              # UI component library
│   ├── pages/           # Page components
│   │   ├── ChatPage.vue     # Main chat interface
│   │   └── HomePage.vue     # Landing page
│   ├── App.vue          # Root component
│   ├── main.ts          # Application entry point
│   └── index.css        # Global styles and Tailwind CSS
├── public/              # Static assets
├── dist/               # Build output
├── package.json        # Dependencies and scripts
├── vite.config.ts      # Vite configuration
└── tailwind.config.js  # Tailwind CSS configuration
```

## 🛠️ Setup

### Prerequisites

- Node.js 20+
- npm or yarn package manager

### Local Development

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Development server: http://localhost:5173
   - Backend API: http://localhost:8000 (ensure backend is running)

### Environment Configuration

Create `.env` file in frontend directory:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Build for Production

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Preview the build**
   ```bash
   npm run preview
   ```

## 📡 API Integration

### Backend Connection

The frontend connects to the backend API at:
- **Development**: http://localhost:8000
- **Production**: Configured via `VITE_API_BASE_URL`

### Real-time Communication

- **Server-Sent Events**: Used for real-time chat updates
- **WebSocket**: Used for VNC remote viewing
- **HTTP API**: Used for session management and other operations

## 🔧 Configuration

### Vite Configuration

Located in `vite.config.ts`:
- **Proxy**: API proxy for development
- **Build**: Production build settings
- **Plugins**: Vue, TypeScript, and Tailwind CSS

### Tailwind CSS

Located in `tailwind.config.js`:
- **Dark Mode**: Class-based dark mode
- **Theme**: Custom color scheme and spacing
- **Plugins**: Typography and forms plugins

### TypeScript Configuration

- **Strict Mode**: Enabled for better type safety
- **Path Mapping**: Aliases for cleaner imports
- **Vue 3**: Composition API support

## 🧪 Testing

### Run tests
```bash
npm run test
```

### Run tests with coverage
```bash
npm run test:coverage
```

### Run type checking
```bash
npm run type-check
```

## 📦 Production Deployment

### Build Configuration

1. **Set production environment variables**
   ```bash
   export VITE_API_BASE_URL=https://your-api-domain.com
   export VITE_WS_URL=wss://your-api-domain.com
   ```

2. **Build for production**
   ```bash
   npm run build
   ```

3. **Deploy the dist folder**
   - Copy `dist/` contents to your web server
   - Configure nginx/apache to serve the files
   - Set up proper routing for SPA

### Docker Deployment

Using the main project's Docker configuration:
```bash
cd ../
docker-compose up --build
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure port 5173 is available
2. **Backend connection**: Verify backend is running on port 8000
3. **TypeScript errors**: Run `npm run type-check` to identify issues
4. **Build failures**: Check for missing dependencies or configuration issues

### Development Issues

1. **Hot reload not working**: Restart the dev server
2. **API calls failing**: Check proxy configuration in vite.config.ts
3. **Styling issues**: Ensure Tailwind CSS is properly configured

### Debug Mode

Enable Vue devtools and debug logging:
```bash
npm run dev -- --debug
```

## 🔗 Integration

### Backend Integration

The frontend expects the backend to provide:
- **Session management endpoints** at `/api/v1/sessions`
- **Chat endpoints** with SSE support
- **Health check** at `/health`

### MCP Tools

Frontend supports:
- **Browser automation** via Playwright/Puppeteer
- **File operations** via MCP filesystem
- **Web scraping** via MCP fetch
- **Memory management** via MCP memory server

## 🎨 Styling

### Tailwind CSS Classes

- **Layout**: Flexbox and Grid utilities
- **Components**: Pre-built UI components
- **Dark Mode**: Automatic dark/light theme switching
- **Responsive**: Mobile-first responsive design

### Custom Components

- **Chat bubbles**: Styled message containers
- **Sidebar**: Session management panel
- **Tool panel**: MCP tool interface
- **Buttons**: Consistent button styling

## 📄 License

MIT License - see main project LICENSE file.