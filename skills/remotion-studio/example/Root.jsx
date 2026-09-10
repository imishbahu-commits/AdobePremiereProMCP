import React from 'react';
import { Composition } from 'remotion';
import { PremiumSting } from './PremiumSting';

export const RemotionRoot = () => (
  <>
    <Composition
      id="PremiumSting"
      component={PremiumSting}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ title: 'MOTION', stat: 27, suffix: '%' }}
    />
  </>
);
