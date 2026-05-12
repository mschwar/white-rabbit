import type { HTMLAttributes } from 'react';

type BrandWordmarkProps = HTMLAttributes<HTMLDivElement> & {
  caption?: string;
  inverted?: boolean;
  size?: 'rail' | 'hero' | 'login';
};

const WORDMARK_SIZE = {
  rail: 'text-[17px] leading-none',
  hero: 'text-4xl leading-none sm:text-5xl lg:text-6xl',
  login: 'text-3xl leading-none',
} as const;

const CAPTION_SIZE = {
  rail: 'mt-1 text-[11px]',
  hero: 'mt-4 text-sm sm:text-base',
  login: 'mt-3 text-sm',
} as const;

export function BrandWordmark({
  caption,
  className = '',
  inverted = false,
  size = 'rail',
  ...props
}: BrandWordmarkProps) {
  return (
    <div className={className} {...props}>
      <p
        aria-label="White Rabbit"
        className={`${WORDMARK_SIZE[size]} font-semibold tracking-normal ${
          inverted ? 'text-white' : 'text-[#0a1226]'
        }`}
      >
        White<span className="text-[#2d7bff]">Rabbit</span>
      </p>
      {caption ? (
        <p
          className={`${CAPTION_SIZE[size]} font-medium leading-5 tracking-normal ${
            inverted ? 'text-white/62' : 'text-[#536175]'
          }`}
        >
          {caption}
        </p>
      ) : null}
    </div>
  );
}

export function BrandSignal({ className = '' }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={`grid place-items-center rounded-lg border border-[#2d7bff]/35 bg-[#2d7bff]/15 ${className}`}
    >
      <span className="h-2.5 w-2.5 rounded-full bg-[#2d7bff] shadow-[0_0_18px_rgba(45,123,255,0.55)]" />
    </div>
  );
}
