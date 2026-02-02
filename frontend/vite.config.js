import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import * as fs from 'node:fs';
import { fileURLToPath } from 'node:url';
var __filename = fileURLToPath(import.meta.url);
var __dirname = path.dirname(__filename);
// Read .env.local if it exists
var envLocalPath = path.resolve(__dirname, '.env.local');
var basePath = '/hb_grabber/';
if (fs.existsSync(envLocalPath)) {
    var envContent = fs.readFileSync(envLocalPath, 'utf-8');
    var envMatch = envContent.match(/VITE_BASE_PATH=(.+)/);
    if (envMatch) {
        basePath = envMatch[1].trim();
    }
}
// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    base: basePath,
    build: {
        assetsDir: 'assets',
        rollupOptions: {
            output: {
                assetFileNames: function (assetInfo) {
                    var _a;
                    // Keep image files and XML files in root directory instead of assets folder
                    var info = ((_a = assetInfo.name) === null || _a === void 0 ? void 0 : _a.split('.')) || [];
                    var extType = info[info.length - 1];
                    if (/png|jpe?g|svg|gif|tiff|bmp|ico|xml/i.test(extType)) {
                        return "[name].[ext]";
                    }
                    return "assets/[name]-[hash].[ext]";
                },
            },
        },
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
});
