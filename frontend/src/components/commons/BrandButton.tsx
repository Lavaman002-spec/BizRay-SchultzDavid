import React from 'react';
import { LucideIcon } from 'lucide-react';

export type ButtonVariant = 'primary' | 'secondary' | 'link';

export interface BrandButtonProps {
  text: string;
  leftIcon?: LucideIcon;
  rightIcon?: LucideIcon;
  variant?: ButtonVariant;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export default function BrandButton({
  text,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  variant = 'primary',
  onClick,
  disabled = false,
  type = 'button',
  className = '',
}: BrandButtonProps) {
  // Base styles shared across all variants
  const baseStyles =
    'inline-flex items-center justify-center gap-1.5 font-medium text-base leading-6 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer';

  // Variant-specific styles
  const variantStyles = {
    primary: `
      bg-[#010101]
      text-white
      rounded-md
      px-4 py-1.5
      border-2 border-[rgba(255,255,255,0.12)]
      hover:bg-[#141414]
      active:bg-[#010101]
    `,
    secondary: `
      bg-white
      text-[#414651]
      rounded-md
      px-4 py-1.5
      border border-[#d5d7da]
      hover:bg-neutral-100
      active:bg-white
    `,
    link: `
      bg-transparent
      text-[#414651]
      rounded-lg
      px-1.5 py-1
      hover:text-[#010101]
      active:text-[#414651]
    `,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`.trim()}
    >
      {LeftIcon && <LeftIcon className="w-4 h-4" />}
      <span className="px-0.5">{text}</span>
      {RightIcon && <RightIcon className="w-4 h-4" />}
    </button>
  );
}
