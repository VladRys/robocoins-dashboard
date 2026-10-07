import kanjou from "@kanjou/plugin/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import unocss from "unocss/vite";
import { defineConfig } from "vite-plus";
import "dotenv/config";

export default defineConfig({
  resolve: { tsconfigPaths: true },
  server: {
    proxy: {
      "/api": {
        target: process.env.API_URL,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  plugins: [
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
      generatedRouteTree: "./generated/routeTree.gen.ts",
      tmpDir: "./generated/.tanstack/tmp",
    }),
    kanjou({
      baseLocale: "uk",
    }),
    react(),
    unocss(),
  ],
  fmt: {
    sortImports: true,
    ignorePatterns: ["routeTree.gen.ts"],
  },
  lint: {
    rules: {
      "react/exhaustive-deps": "off",
    },
    options: { typeAware: true, typeCheck: true },
    ignorePatterns: ["routeTree.gen.ts"],
  },
});
