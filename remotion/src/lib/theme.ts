import { loadFont } from "@remotion/google-fonts/Montserrat";

export const { fontFamily } = loadFont("normal", { weights: ["700", "800", "900"], subsets: ["latin"] });

export const theme = {
  font: fontFamily,
  white: "#FFFFFF",
  accent: "#FFE14D", // active caption word / highlights
  hot: "#FF3D6E", // brand pink for cards
  ink: "#0B0B0F",
  stroke: "#000000",
};

/** YouTube Shorts UI covers the top ~20% and bottom ~25%. Keep text inside these bounds. */
export const SHORT_SAFE = { top: 400, bottom: 1440, side: 80 };

export const SFX: Record<string, string> = {
  whoosh: "_lib/sfx/whoosh.wav",
  whip: "_lib/sfx/whip.wav",
  ding: "_lib/sfx/ding.wav",
  "bass-hit": "_lib/sfx/vine-boom.wav",
  "vine-boom": "_lib/sfx/vine-boom.wav",
  "record-scratch": "_lib/sfx/record-scratch.wav",
  shutter: "_lib/sfx/shutter-modern.wav",
  switch: "_lib/sfx/switch.wav",
  riser: "_lib/sfx/whoosh.wav",
  "page-turn": "_lib/sfx/page-turn.wav",
};
