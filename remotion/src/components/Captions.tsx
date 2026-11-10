import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CaptionPage } from "../lib/types";
import { SHORT_SAFE, theme } from "../lib/theme";

/** Word-by-word burned-in captions driven by Kokoro word timestamps. Active word is highlighted. */
export const Captions: React.FC<{ pages: CaptionPage[]; format: "short" | "long" }> = ({ pages, format }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const page = pages.find((p) => t >= p.start && t < p.end);
  if (!page) return null;
  const local = (t - page.start) * fps;
  const short = format === "short";

  return (
    <AbsoluteFill
      style={{
        justifyContent: short ? "flex-end" : "flex-start",
        alignItems: "center",
        // Short: bottom-anchored just above the Shorts UI (like/comment rail + title start ~y=1440).
        paddingBottom: short ? 1920 - SHORT_SAFE.bottom + 10 : 0,
        paddingTop: short ? 0 : 860,
        paddingLeft: short ? SHORT_SAFE.side : 200,
        paddingRight: short ? SHORT_SAFE.side : 200,
      }}
    >
      <div
        style={{
          fontFamily: theme.font,
          fontWeight: 900,
          fontSize: short ? 82 : 58,
          whiteSpace: short ? "nowrap" : "normal",
          lineHeight: 1.1,
          textAlign: "center",
          textTransform: short ? "uppercase" : "none",
          color: theme.white,
          WebkitTextStroke: `${short ? 14 : 10}px ${theme.stroke}`,
          paintOrder: "stroke fill",
          textShadow: "0 6px 18px rgba(0,0,0,0.55)",
          scale: interpolate(local, [0, 4], [0.86, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        {page.words.map((w, i) => {
          const active = t >= w.start && t < (page.words[i + 1]?.start ?? page.end);
          return (
            <span key={i} style={{ color: active ? theme.accent : theme.white }}>
              {w.word.replace(/[.,;:]+$/, "")}
              {i < page.words.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
