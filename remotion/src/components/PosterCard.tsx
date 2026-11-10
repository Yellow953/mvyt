import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

/** Movie / show poster that slides into the top-right corner while the VO talks about that title. */
export const PosterCard: React.FC<{ src: string; format: "short" | "long"; width?: number; height?: number }> = ({
  src,
  format,
  width: natW,
  height: natH,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const short = format === "short";
  // Fit inside a box (portrait posters fill the height; wide title cards / landscape posters fill the width).
  const boxW = short ? 330 : 300;
  const boxH = short ? 340 : 300;
  const ar = natW && natH ? natW / natH : 2 / 3;
  const w = Math.round(Math.min(boxW, boxH * ar));
  const h = Math.round(w / ar);
  return (
    <AbsoluteFill style={{ alignItems: "flex-end", paddingTop: short ? 270 : 60, paddingRight: short ? 40 : 60 }}>
      <Img
        src={staticFile(src)}
        style={{
          width: w,
          height: h,
          objectFit: "cover",
          border: "6px solid #fff",
          borderRadius: 10,
          boxShadow: "0 18px 50px rgba(0,0,0,0.6)",
          rotate: "4deg",
          translate: interpolate(frame, [0, 0.35 * fps], ["320px 0px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          opacity: interpolate(frame, [0, 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      />
    </AbsoluteFill>
  );
};
