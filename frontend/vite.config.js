import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
// https://vite.dev/config/
export default defineConfig(function () { return ({
    plugins: [react()],
    base: '/hb_grabber/',
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
}); });
