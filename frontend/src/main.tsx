import { TranslateProvider } from "@kanjou/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { createRoot } from "react-dom/client";
import locales from "virtual:kanjou/locales";

import { queryClient } from "#/lib/query";

import { routeTree } from "../generated/routeTree.gen";

import "#/assets/styles/global.css";
import "virtual:uno.css";
import { ReactNode } from "react";
import { Typography } from "./components/ui";

const user = null;

const router = createRouter({
  routeTree,
  context: { user },
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const locale = "uk";
const messages = await locales[locale]();

const components = {
  br: () => <br />,
};

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <TranslateProvider
      locale={locale}
      messages={messages}
      components={components}
    >
      <RouterProvider router={router} />
    </TranslateProvider>
  </QueryClientProvider>,
);
