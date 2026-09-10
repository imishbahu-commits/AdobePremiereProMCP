import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, Easing, Sequence } from 'remotion';

// motion-graphix grammar: expo-out settle ease, stagger 60ms, count-up 1s,
// pose-ladder camera on ONE wrapper, impact punch <=3 frames.
const EXPO_OUT = Easing.bezier(0.16, 1, 0.3, 1);

const Word = ({ children, frame, start }) => {
  const p = interpolate(frame, [start, start + 18], [0, 1], {
    easing: EXPO_OUT, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <span style={{
      display: 'inline-block', opacity: p,
      transform: `translateY(${(1 - p) * 30}px)`,
      fontFamily: 'DejaVu Sans, sans-serif', fontWeight: 800,
      fontSize: 180, color: '#F7F4FF', letterSpacing: -4, marginRight: 24,
    }}>{children}</span>
  );
};

export const PremiumSting = ({ title = 'MOTION', stat = 27, suffix = '%' }) => {
  const frame = useCurrentFrame();
  // camera pose ladder: hold → slow dolly push (expo-in-out) → hard punch at 210
  const dolly = interpolate(frame, [60, 190], [1, 1.18], {
    easing: Easing.inOut(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const punch = interpolate(frame, [210, 212], [1, 1.24], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const cam = dolly * punch;

  // stat count-up 0.9s starting f120, terminal pulse
  const c = interpolate(frame, [120, 147], [0, stat], { easing: EXPO_OUT, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const pulse = 1 + 0.06 * interpolate(Math.max(0, frame - 147), [0, 6, 12], [0, 1, 0], { extrapolateRight: 'clamp' });

  const words = title.split(' ');
  return (
    <AbsoluteFill style={{ background: '#492488', justifyContent: 'center', alignItems: 'center' }}>
      <AbsoluteFill style={{
        transform: `scale(${cam})`, justifyContent: 'center', alignItems: 'center',
        background: 'radial-gradient(ellipse at 20% 80%, rgba(152,135,198,0.5) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(246,211,112,0.25) 0%, transparent 50%), #492488',
      }}>
        <div style={{ display: 'flex' }}>
          {words.map((w, i) => <Word key={i} frame={frame} start={20 + i * 2}>{w}</Word>) /* 2f ≈ 66ms stagger */}
        </div>
        <Sequence from={110}>
          <div style={{
            transform: `scale(${pulse})`, fontFamily: 'DejaVu Sans, sans-serif', fontWeight: 800,
            fontSize: 260, color: '#F6D370', textShadow: '0 8px 40px rgba(0,0,0,0.35)',
          }}>
            +{Math.round(c)}{suffix}
          </div>
        </Sequence>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
