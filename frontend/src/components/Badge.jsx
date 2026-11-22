import React from 'react';

export default function Badge({ children, variant = 'slate', size = 'sm' }) {
  const variants = {
    green: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    amber: 'bg-amber-50 text-amber-800 border-amber-200',
    red: 'bg-rose-50 text-rose-700 border-rose-200',
    slate: 'bg-slate-100 text-slate-700 border-slate-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200'
  };

  const sizes = {
    xs: 'text-[10px] px-1.5 py-0.5',
    sm: 'text-xs px-2.5 py-1',
    md: 'text-sm px-3 py-1.5'
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${variants[variant] || variants.slate} ${sizes[size]}`}>
      {children}
    </span>
  );
}
