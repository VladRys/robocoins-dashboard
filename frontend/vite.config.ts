import kanjou from "@kanjou/plugin/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import unocss from "unocss/vite";
import { defineConfig } from "vite-plus";

export default defineConfig({
  resolve: { tsconfigPaths: true },
  server: {
    proxy: {
      "/api": process.env.API_URL!,
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
