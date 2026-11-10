import { z } from "zod";

export const propsSchema = z.object({
  slug: z.string(),
});

export type Treatment = "ken-burns" | "zoom-punch" | "blur-bg-fill" | "split" | "shake" | "none";

export type Visual = {
  type: "clip" | "image" | "graphic" | "stat" | "split" | "text-card";
  query?: string;
  source?: string | null;
  file?: string | null;
  in?: number | null;
  out?: number | null;
  treatment?: Treatment;
  volume?: number; // original clip audio volume (default 0 = muted under VO)
  focus?: number; // 0..1 horizontal subject position for 9:16 crops (tools/focus.py)
  zoom?: number; // extra static zoom for full-frame clips (e.g. 1.25) to push burned-in source text out of the caption zone
  anchor?: "top" | "center" | "bottom"; // which edge stays fixed when zooming (top pushes bottom text down, bottom pushes it up)
};

export type Scene = {
  id: string;
  section?: string;
  vo?: string;
  text?: string | null;
  visual?: Visual;
  sfx?: string | null;
  est_sec?: number;
  poster?: { wiki?: string; file?: string | null }; // film/show poster shown top-right (fetched from Wikipedia)
};

export type Spec = {
  slug: string;
  format: "short" | "long";
  title?: string;
  music?: { file?: string; mood?: string; volume?: number; start?: number }; // start = seconds into the track (skip quiet intros)
  framing?: "fill" | "4:5" | "1:1"; // Shorts: how landscape footage is framed
  scenes: Scene[];
};

export type Word = { word: string; start: number; end: number };
export type SceneTiming = { id: string; start: number; duration: number; words: Word[] };
export type Timings = { total: number; scenes: SceneTiming[] };

export type AssetInfo = { file: string; kind: string; width?: number; height?: number; duration?: number };

/** A caption "page": a few words shown together, with the active word highlighted. */
export type CaptionPage = { start: number; end: number; words: Word[] };

export type ResolvedScene = Scene & {
  startFrame: number;
  durationInFrames: number;
  asset?: AssetInfo;
  posterAsset?: AssetInfo;
};

export type ResolvedProps = {
  slug: string;
  framing?: "fill" | "4:5" | "1:1";
  spec?: Spec;
  scenes?: ResolvedScene[];
  pages?: CaptionPage[];
  hasVoice?: boolean;
};
