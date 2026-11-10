import { Audio } from "@remotion/media";
import React from "react";
import { interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CaptionPage } from "../lib/types";

/**
 * Background music bed with auto-ducking: drops to ~45% while the narrator speaks,
 * swells back up in pauses, fades in at the start and out at the end.
 */
export const Music: React.FC<{ file: string; volume: number; start?: number; speech: CaptionPage[] }> = ({ file, volume, start = 0, speech }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;
  // distance (s) to the nearest speech segment → 0 while talking
  const gap = speech.reduce((m, p) => Math.min(m, t < p.start ? p.start - t : t > p.end ? t - p.end : 0), 99);
  const duck = interpolate(gap, [0, 0.35], [0.6, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fade = interpolate(frame, [0, 0.8 * fps, durationInFrames - 1.2 * fps, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return <Audio name="Music" src={staticFile(file)} volume={volume * duck * fade} trimBefore={Math.round(start * fps)} loop />;
};
