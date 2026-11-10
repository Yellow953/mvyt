import { Video } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ResolvedScene } from "../lib/types";
import { Card, MissingFootage } from "./Cards";

/** Motion treatment wrapper (zoom-punch, ken-burns, shake). */
const Motion: React.FC<{ treatment?: string; children: React.ReactNode }> = ({ treatment, children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const t = treatment ?? "none";
  return (
    <AbsoluteFill
      style={{
        scale:
          t === "zoom-punch"
            ? interpolate(frame, [0, 0.3 * fps], [1.1, 1.0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
                easing: Easing.bezier(0.16, 1, 0.3, 1),
              })
            : t === "ken-burns"
              ? interpolate(frame, [0, durationInFrames], [1.0, 1.05], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })
              : 1,
        translate:
          t === "shake" && frame < 0.35 * fps
            ? `${Math.round(Math.sin(frame * 2.7) * 14)}px ${Math.round(Math.cos(frame * 3.1) * 10)}px`
            : "0px 0px",
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const Media: React.FC<{ scene: ResolvedScene & { spec_slug: string }; fit: "cover" | "contain"; muted?: boolean }> = ({ scene, fit, muted }) => {
  const v = scene.visual!;
  const src = staticFile(`${scene.spec_slug}/${v.file}`);
  // visual.focus (0..1, set by tools/focus.py face detection) keeps the subject inside a 9:16 crop.
  const style: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: fit,
    objectPosition: `${Math.round((v.focus ?? 0.5) * 100)}% 50%`,
  };
  if (scene.asset?.kind === "image" || v.type === "image") return <Img src={src} style={style} />;
  // Clip shorter than its scene → cinematic slow-mo to fill it (floor 0.55x), loop only as a last resort.
  const sceneSec = scene.durationInFrames / 30;
  const clipSec = scene.asset?.duration ?? sceneSec;
  const rate = clipSec < sceneSec ? Math.max(0.55, clipSec / sceneSec) : 1;
  return (
    <Video src={src} objectFit={fit} style={style} loop playbackRate={rate} muted={muted || !v.volume} volume={v.volume ?? 0} />
  );
};

export type Framing = "fill" | "4:5" | "1:1";

export const Visual: React.FC<{ scene: ResolvedScene & { spec_slug: string }; format: "short" | "long"; framing?: Framing }> = ({
  scene,
  format,
  framing = "fill",
}) => {
  const v = scene.visual;
  if (!v) return <Card kind="text-card" text={scene.text ?? ""} format={format} />;

  if (v.type === "graphic" || v.type === "stat" || v.type === "text-card") {
    return (
      <Motion treatment={v.treatment ?? "zoom-punch"}>
        <Card kind={v.type} text={scene.text ?? ""} format={format} />
      </Motion>
    );
  }

  if (!v.file) return <MissingFootage scene={scene} format={format} />;

  // Default: fill the whole frame (Shorts crop 16:9 → 9:16 around visual.focus).
  // Blurred-band layout only when explicitly requested, or for vertical footage inside a long-form video.
  const frameAR = format === "short" ? 9 / 16 : 16 / 9;
  const ar = scene.asset?.width && scene.asset?.height ? scene.asset.width / scene.asset.height : frameAR;
  const verticalInLong = format === "long" && ar < 1;
  const fill = v.treatment === "blur-bg-fill" || verticalInLong;

  // Window framing for landscape footage in Shorts: show more of the shot inside a 4:5 or 1:1 window on black.
  if (format === "short" && framing !== "fill" && ar > 1) {
    const h = framing === "4:5" ? 1350 : 1080;
    return (
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <div style={{ position: "absolute", top: 230, left: 0, width: 1080, height: h, overflow: "hidden" }}>
          <Motion treatment={v.treatment ?? (v.type === "image" ? "ken-burns" : "none")}>
            <Media scene={scene} fit="cover" />
          </Motion>
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {fill ? (
        <>
          <AbsoluteFill style={{ filter: "blur(40px) brightness(0.55)", scale: 1.2 }}>
            <Media scene={scene} fit="cover" muted />
          </AbsoluteFill>
          <Motion treatment={v.treatment === "blur-bg-fill" ? "ken-burns" : v.treatment}>
            <AbsoluteFill style={{ justifyContent: "center" }}>
              <div style={{ width: "100%", height: format === "short" ? Math.min(1300, (1080 / ar) * 1.55) : "100%" }}>
                <Media scene={scene} fit={format === "short" ? "cover" : "contain"} />
              </div>
            </AbsoluteFill>
          </Motion>
        </>
      ) : (
        <AbsoluteFill
          style={{
            scale: v.zoom ?? 1,
            transformOrigin: `50% ${v.anchor === "top" ? 0 : v.anchor === "bottom" ? 100 : 50}%`,
          }}
        >
          <Motion treatment={v.treatment ?? (v.type === "image" ? "ken-burns" : "none")}>
            <Media scene={scene} fit="cover" />
          </Motion>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
