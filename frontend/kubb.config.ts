import { adapterOas } from "@kubb/adapter-oas";
import { pluginFetch } from "@kubb/plugin-fetch";
import { pluginReactQuery } from "@kubb/plugin-react-query";
import { pluginTs } from "@kubb/plugin-ts";
import { defineConfig } from "kubb";
import "dotenv/config";

export default defineConfig({
  input: `${process.env.API_URL}/openapi.json`,
  output: { path: "./generated/api", clean: true },
  plugins: [pluginTs(), pluginFetch(), pluginReactQuery()],
  adapter: adapterOas(),
});
