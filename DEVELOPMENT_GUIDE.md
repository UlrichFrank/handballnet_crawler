# Development Guide for Web Mockup Template

This guide will help you set up and develop mockups using this repository, even if you have no prior development experience.

## Table of Contents
1. [What You'll Need](#what-youll-need)
2. [Initial Setup](#initial-setup)
3. [Daily Development Workflow](#daily-development-workflow)
4. [Common Tasks](#common-tasks)
5. [Troubleshooting](#troubleshooting)
6. [Understanding the Project Structure](#understanding-the-project-structure)

## What You'll Need

### Required Software

1. **Node.js** - The runtime environment for the application
2. **pnpm** - Package manager (faster alternative to npm)
3. **Git** - Version control (likely already installed)
4. **A Code Editor** - VS Code is recommended
5. **A Web Browser** - Chrome, Firefox, Safari, or Edge

### Optional but Helpful
- **Terminal/Command Line** knowledge (we'll guide you through this)

## Initial Setup

### Step 1: Install Node.js

#### For Windows Users:
Follow the instructions in `docs/node-windows.md` for detailed Windows setup with nvm-windows.

#### For macOS Users:
1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install nvm (Node Version Manager)**:
   ```bash
   brew install nvm
   ```

3. **Add nvm to your shell profile**:
   ```bash
   echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
   echo '[ -s "/opt/homebrew/bin/nvm" ] && \. "/opt/homebrew/bin/nvm"' >> ~/.zshrc
   echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.zshrc
   ```

4. **Restart your terminal** or run:
   ```bash
   source ~/.zshrc
   ```

5. **Install the latest stable Node.js**:
   ```bash
   nvm install node
   nvm use node
   ```

6. **Verify installation**:
   ```bash
   node --version
   npm --version
   ```

### Step 2: Install pnpm
```bash
npm install -g pnpm
```

### Step 3: Clone and Setup the Project

1. **Navigate to your desired folder** (e.g., Desktop):
   ```bash
   cd ~/Desktop
   ```

2. **Clone the repository** (if you haven't already):
   ```bash
   git clone [YOUR_REPOSITORY_URL]
   cd web-mockup-template
   ```

3. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

4. **Install project dependencies**:
   ```bash
   pnpm install
   ```
   
   This will download all necessary packages. It may take a few minutes.

## Daily Development Workflow

### Starting Development

1. **Open Terminal** and navigate to the project:
   ```bash
   cd path/to/your/web-mockup-template/frontend
   ```

2. **Start the development server**:
   ```bash
   pnpm dev
   ```

3. **Open your browser** and go to the URL shown in the terminal (usually `http://localhost:5173`)

4. **Keep the terminal open** - this is your development server running

### Making Changes

1. **Open the project in VS Code**:
   ```bash
   code .
   ```
   (Run this from the `frontend` directory)

2. **Edit files** in the `src` folder:
   - `src/components/` - Individual UI components
   - `src/pages/` - Different pages of your mockup
   - `src/App.tsx` - Main application file with routing

3. **Save your changes** - the browser will automatically refresh and show your updates

### Stopping Development

- **Stop the development server**: Press `Ctrl+C` (or `Cmd+C` on macOS) in the terminal

## Common Tasks

### Creating a New Page

1. **Create a new file** in `src/pages/` (e.g., `MyNewPage.tsx`)
2. **Copy the structure** from an existing page like `Dashboard.tsx`
3. **Add the route** in `src/App.tsx`
4. **Add navigation link** in `src/components/Navigation.tsx`

### Modifying Existing Components

1. **Find the component** you want to change in `src/components/`
2. **Edit the file** using VS Code
3. **Save** - changes appear automatically in the browser

### Adding New Data

1. **Find the mock data** in the component or page files
2. **Replace or extend** the sample data with your own
3. **Update TypeScript types** in `src/types/index.ts` if needed

### Building for Production

When you're ready to share your mockup:

```bash
pnpm build
```

This creates a `dist` folder with files you can host on any web server.

### Preview Production Build

To test the production build locally:

```bash
pnpm preview
```

## Troubleshooting

### Common Issues and Solutions

#### "Command not found" errors
- **Solution**: Make sure Node.js and pnpm are properly installed
- **Check**: Run `node --version` and `pnpm --version`

#### Port already in use
- **Solution**: Either stop other applications using port 5173, or Vite will automatically use the next available port
- **Check**: Look for the actual URL in the terminal output

#### Dependencies not installing
- **Solution**: Try deleting `node_modules` folder and `pnpm-lock.yaml`, then run `pnpm install` again
- **Alternative**: Use `pnpm install --frozen-lockfile=false`

#### Browser not updating with changes
- **Solution**: 
  1. Check if the development server is still running
  2. Refresh the browser manually (F5 or Cmd+R)
  3. Clear browser cache

#### TypeScript errors
- **Solution**: 
  1. Check the terminal for specific error messages
  2. Make sure all imports are correct
  3. Verify that types match in `src/types/index.ts`

### Getting Help

1. **Check the terminal** for error messages
2. **Read the error carefully** - it often tells you exactly what's wrong
3. **Check the browser console** (F12 → Console tab)
4. **Ask for help** - provide the exact error message

## Understanding the Project Structure

```
web-mockup-template/
├── frontend/                    # Main application folder
│   ├── src/                    # Source code
│   │   ├── components/         # Reusable UI pieces
│   │   │   ├── ui/            # Basic components (buttons, cards)
│   │   │   ├── Navigation.tsx  # Top navigation bar
│   │   │   ├── DataTable.tsx   # Table component
│   │   │   └── ...            # Other components
│   │   ├── pages/             # Different screens/pages
│   │   │   ├── Dashboard.tsx   # Home page
│   │   │   ├── FormExamples.tsx # Form demonstrations
│   │   │   └── ...            # Other pages
│   │   ├── types/             # Data structure definitions
│   │   ├── hooks/             # Reusable logic
│   │   ├── contexts/          # App-wide state management
│   │   └── App.tsx            # Main app with routing
│   ├── public/                # Static files (images, etc.)
│   ├── package.json           # Project dependencies
│   └── ...config files        # Build and tool configuration
├── docs/                      # Documentation
├── README.md                  # Project overview
└── DEVELOPMENT_GUIDE.md       # This file
```

### Key Files to Know

- **`src/App.tsx`** - Main application, defines routes
- **`src/components/Navigation.tsx`** - Top navigation menu
- **`src/pages/Dashboard.tsx`** - Home page content
- **`src/types/index.ts`** - Data type definitions
- **`package.json`** - Lists all dependencies and scripts

### Customization Tips

1. **Start with existing pages** - modify `Dashboard.tsx` or copy it
2. **Use existing components** - browse `src/components/` for ready-made parts
3. **Follow the patterns** - look at how existing code is structured
4. **Test frequently** - save often and check the browser

## Next Steps

1. **Explore the existing pages** - visit all the routes to see what's available
2. **Make small changes** - start by modifying text or colors
3. **Add your content** - replace sample data with your mockup content
4. **Experiment** - try copying and modifying existing components

Remember: Development is iterative. Start small, test often, and build incrementally!
