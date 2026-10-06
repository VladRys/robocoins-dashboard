import { defineConfig, presetIcons, presetMini, presetWebFonts } from "unocss";

const custom = {
  asterisk:
    '<svg viewBox="0 0 30 27" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M2.6 22.2C2.2 22 2.1 21.6 2.1 21.1C2.1 20.7 2.2 20.3 2.6 20L7.4 15.4L1.5 14.8C1 14.8.7 14.6.4 14.4C.1 14.1 0 13.7 0 13.3L.1 12.8L1.9 6.1C2 5.8 2.2 5.5 2.4 5.3C2.7 5.1 3 5 3.4 5C3.6 5 3.9 5 4.2 5.2L9.9 7.5L8.7 1.9L8.7 1.5C8.7 1.2 8.8.8 9.1.5C9.4.2 9.8 0 10.2 0H19.9C20.3 0 20.6.2 20.9.5C21.2.8 21.4 1.1 21.4 1.5L21.3 2L20.2 7.5L25.9 5.2C26.2 5 26.4 5 26.7 5C27 5 27.3 5.1 27.6 5.3C27.9 5.5 28 5.8 28.1 6.1L29.9 12.8L30 13.3C30 13.7 29.9 14.1 29.6 14.4C29.3 14.6 29 14.8 28.6 14.8L22.6 15.4L27.4 20C27.8 20.3 28 20.7 28 21.1C28 21.6 27.8 22 27.4 22.3L21.3 26.7C21.1 26.9 20.7 27 20.4 27C20 27 19.7 26.9 19.5 26.7C19.2 26.5 19.1 26.3 19 26.1L15 20L11.1 26.1C11 26.4 10.8 26.6 10.5 26.8C10.3 26.9 10 27 9.7 27C9.3 27 9 26.9 8.7 26.7L2.6 22.2Z"/></svg>',
};

export default defineConfig({
  presets: [
    presetIcons({
      collections: {
        custom,
      },
    }),
    presetMini({
      preflight: false,
    }),
    presetWebFonts({
      provider: "fontsource",
      fonts: {
        sans: "Rubik",
        mono: "Rubik Mono One",
      },
    }),
  ],
});
