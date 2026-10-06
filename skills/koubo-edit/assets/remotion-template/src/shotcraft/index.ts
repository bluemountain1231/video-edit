/**
 * The small, dependency-light Shotcraft surface wired into koubo-edit.
 *
 * The full library (including Three.js helpers and every reference demo) is
 * shipped beside the template in assets/remotion-library.  These exports are
 * safe to import directly from a normal koubo-edit renderer without adding a
 * 3D runtime dependency.
 */
export { Caption } from "./Caption";
export { ClipCard } from "./ClipCard";
export { DigitRoll } from "./DigitRoll";
export { FlashCut } from "./FlashCut";
export { PageCam } from "./PageCam";
export { VerticalTicker } from "./VerticalTicker";
export { velocityAt, lagged, dampedSettle } from "./helpers/motion";
export { mulberry32 } from "./helpers/rand";
export { handheld } from "./helpers/shake";
