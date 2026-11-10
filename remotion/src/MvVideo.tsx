import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Captions } from "./components/Captions";
import { Music } from "./components/Music";
import { OnScreenText } from "./components/OnScreenText";
import { PosterCard } from "./components/PosterCard";
import { Visual } from "./components/Visual";
import { SFX } from "./lib/theme";
import { ResolvedProps } from "./lib/types";

/**
 * Data-driven ModelVault video. Everything comes from videos/<slug>/:
 *   scenes.json (script + visuals) · audio/voice.wav + timings.json (Kokoro) · assets/ (footage)
 */
export const MvVideo: React.FC<ResolvedProps> = ({ slug, spec, scenes, pages, hasVoice, framing: framingProp }) => {
  if (!spec || !scenes) return null;
  const format = spec.format;
  const framing = framingProp ?? spec.framing ?? (format === "short" ? "4:5" : "fill");

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Visual track: one sequence per scene */}
      {scenes.map((sc) => (
        <Sequence key={sc.id} name={`${sc.id} · ${sc.section ?? ""}`} from={sc.startFrame} durationInFrames={sc.durationInFrames}>
          <Visual scene={{ ...sc, spec_slug: slug }} format={format} framing={framing} />
          {sc.text && sc.visual && !["stat", "graphic", "text-card"].includes(sc.visual.type) && (
            <OnScreenText text={sc.text} format={format} />
          )}
          {sc.poster?.file && <PosterCard src={`${slug}/${sc.poster.file}`} format={format} width={sc.posterAsset?.width} height={sc.posterAsset?.height} />}
          {sc.sfx && SFX[sc.sfx] && <Audio src={staticFile(SFX[sc.sfx])} volume={0.5} />}
        </Sequence>
      ))}

      {/* Captions track */}
      {pages && <Captions pages={pages} format={format} />}

      {/* Audio track */}
      {hasVoice && <Audio name="Voiceover" src={staticFile(`${slug}/audio/voice.wav`)} />}
      {spec.music?.file && <Music file={spec.music.file} volume={spec.music.volume ?? 0.16} speech={pages ?? []} />}
    </AbsoluteFill>
  );
};
