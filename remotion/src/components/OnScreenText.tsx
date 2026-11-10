import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SHORT_SAFE, theme } from "../lib/theme";

/** The scene's punchy on-screen text (hook text, labels). Sits in the upper safe zone. */
export const OnScreenText: React.FC<{ text: string; format: "short" | "long" }> = ({ text, format }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const short = format === "short";
  return (
    // Short: sits just above the captions (lower third) so it never covers faces, which land in the upper third
    // of full-frame 9:16 crops. Long-form: top of frame.
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: short ? "flex-end" : "flex-start",
        paddingBottom: short ? 1920 - SHORT_SAFE.bottom + 230 : 0,
        paddingTop: short ? 0 : 80,
        paddingLeft: 80,
        paddingRight: 80,
      }}
    >
      <div
        style={{
          fontFamily: theme.font,
          fontWeight: 900,
          fontSize: short ? 96 : 72,
          lineHeight: 1.0,
          textTransform: "uppercase",
          textAlign: "center",
          color: theme.ink,
          background: theme.accent,
          padding: short ? "18px 34px" : "12px 28px",
          borderRadius: 18,
          rotate: "-2deg",
          boxShadow: "0 12px 40px rgba(0,0,0,0.45)",
          scale: interpolate(frame, [0, 0.25 * fps], [0.6, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.34, 1.56, 0.64, 1),
          }),
          opacity: interpolate(frame, [0, 3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
