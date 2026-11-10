import { CalculateMetadataFunction, staticFile } from "remotion";
import { AssetInfo, CaptionPage, ResolvedProps, ResolvedScene, Spec, Timings, Word } from "./types";

export const FPS = 30;
export const DIMS = {
  short: { width: 1080, height: 1920 },
  long: { width: 1920, height: 1080 },
};

const getJson = async <T,>(path: string, signal?: AbortSignal): Promise<T | null> => {
  try {
    const r = await fetch(staticFile(path), { signal });
    return r.ok ? ((await r.json()) as T) : null;
  } catch {
    return null;
  }
};

/** Group words into short caption pages: break on max words, pauses, or sentence ends. */
export const paginate = (words: Word[], maxWords: number, maxChars = Infinity): CaptionPage[] => {
  const pages: CaptionPage[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (cur.length) pages.push({ start: cur[0].start, end: cur[cur.length - 1].end, words: cur });
    cur = [];
  };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    const chars = cur.reduce((n, x) => n + x.word.length + 1, 0) + w.word.length;
    if (cur.length && (cur.length >= maxWords || chars > maxChars || (prev && w.start - prev.end > 0.35))) flush();
    cur.push(w);
    if (/[.!?]$/.test(w.word)) flush();
  });
  flush();
  // keep each page on screen until the next one starts (no flicker in tiny gaps)
  pages.forEach((p, i) => {
    const next = pages[i + 1];
    p.end = next ? Math.min(next.start, p.end + 0.6) : p.end + 0.4;
  });
  return pages;
};

export const calculateMetadata: CalculateMetadataFunction<ResolvedProps> = async ({ props, abortSignal }) => {
  const { slug } = props;
  const spec = await getJson<Spec>(`${slug}/scenes.json`, abortSignal);
  if (!spec) throw new Error(`videos/${slug}/scenes.json not found`);
  const timings = await getJson<Timings>(`${slug}/audio/timings.json`, abortSignal);
  const assets = (await getJson<AssetInfo[]>(`${slug}/assets/assets.json`, abortSignal)) ?? [];
  const byFile = new Map(assets.map((a) => [a.file, a]));
  const tmap = new Map((timings?.scenes ?? []).map((s) => [s.id, s]));

  let cursor = 0;
  const scenes: ResolvedScene[] = spec.scenes.map((sc) => {
    const t = tmap.get(sc.id);
    const startSec = t ? t.start : cursor;
    const durSec = t ? t.duration + 0.08 : sc.est_sec ?? 3;
    cursor = startSec + durSec;
    return {
      ...sc,
      startFrame: Math.round(startSec * FPS),
      durationInFrames: Math.max(1, Math.round(durSec * FPS)),
      asset: sc.visual?.file ? byFile.get(sc.visual.file) : undefined,
      posterAsset: sc.poster?.file ? byFile.get(sc.poster.file) : undefined,
    };
  });

  const words = (timings?.scenes ?? []).flatMap((s) => s.words);
  const tail = spec.format === "short" ? 0.15 : 0.8;
  const last = scenes[scenes.length - 1];
  const durationInFrames = last ? last.startFrame + last.durationInFrames + Math.round(tail * FPS) : FPS;

  return {
    durationInFrames,
    fps: FPS,
    ...DIMS[spec.format],
    defaultOutName: `${slug}-${spec.format}`,
    props: {
      slug,
      framing: props.framing,
      spec,
      scenes,
      pages: paginate(words, spec.format === "short" ? 3 : 6, spec.format === "short" ? 16 : Infinity),
      hasVoice: Boolean(timings),
    },
  };
};
