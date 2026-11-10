import React from "react";
import { AbsoluteFill } from "remotion";
import { ResolvedScene } from "../lib/types";
import { theme } from "../lib/theme";

const bg = `radial-gradient(circle at 30% 20%, #2a0f1f 0%, ${theme.ink} 60%)`;

/** Graphic cards. `stat` text format: "BIG | small caption", e.g. "$2.3M | in 11 months". */
export const Card: React.FC<{ kind: string; text: string; format: "short" | "long" }> = ({ kind, text, format }) => {
  const s = format === "short" ? 1 : 0.8;
  const [big, small] = text.split("|").map((x) => x.trim());
  return (
    <AbsoluteFill style={{ background: bg, justifyContent: "center", alignItems: "center", padding: 100 * s }}>
      {kind === "stat" ? (
        <div style={{ textAlign: "center", fontFamily: theme.font }}>
          <div style={{ fontSize: 210 * s, fontWeight: 900, color: theme.accent, lineHeight: 1 }}>{big}</div>
          {small && (
            <div style={{ fontSize: 64 * s, fontWeight: 800, color: theme.white, marginTop: 30, textTransform: "uppercase" }}>
              {small}
            </div>
          )}
        </div>
      ) : (
        <div
          style={{
            fontFamily: theme.font,
            fontWeight: 900,
            fontSize: (text.length > 40 ? 84 : 120) * s,
            color: theme.white,
            textAlign: "center",
            textTransform: "uppercase",
            lineHeight: 1.05,
          }}
        >
          {big}
          {small && <div style={{ color: theme.hot, fontSize: 60 * s, marginTop: 24 }}>{small}</div>}
        </div>
      )}
    </AbsoluteFill>
  );
};

/** Shown in preview when a scene has no downloaded footage yet: makes gaps obvious. */
export const MissingFootage: React.FC<{ scene: ResolvedScene; format: "short" | "long" }> = ({ scene, format }) => (
  <AbsoluteFill
    style={{
      background: "repeating-linear-gradient(45deg,#1a1a1a 0 40px,#222 40px 80px)",
      justifyContent: "center",
      alignItems: "center",
      padding: 80,
    }}
  >
    <div style={{ fontFamily: theme.font, color: "#ff5c5c", fontSize: format === "short" ? 44 : 36, fontWeight: 800, textAlign: "center" }}>
      MISSING FOOTAGE · {scene.id}
      <div style={{ color: "#bbb", fontWeight: 700, marginTop: 20, fontSize: format === "short" ? 36 : 28 }}>
        {scene.visual?.query ?? "no query"}
      </div>
    </div>
  </AbsoluteFill>
);
