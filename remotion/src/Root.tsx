import { Composition } from "remotion";
import { calculateMetadata, DIMS, FPS } from "./lib/load";
import { MvVideo } from "./MvVideo";

// Both compositions render any videos/<slug>/ — pick with --props='{"slug":"<slug>"}'.
// Dimensions/duration are overridden from scenes.json `format` + Kokoro timings in calculateMetadata.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Short"
        component={MvVideo}
        fps={FPS}
        durationInFrames={FPS * 30}
        {...DIMS.short}
        defaultProps={{ slug: "_demo" }}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="Long"
        component={MvVideo}
        fps={FPS}
        durationInFrames={FPS * 60}
        {...DIMS.long}
        defaultProps={{ slug: "_demo-long" }}
        calculateMetadata={calculateMetadata}
      />
    </>
  );
};
