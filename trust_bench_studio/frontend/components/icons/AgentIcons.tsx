
import React from 'react';

const IconWrapper: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    className={`w-8 h-8 ${className}`}
  >
    {children}
  </svg>
);

export const LogosIcon: React.FC<{ className?: string }> = ({ className }) => (
  <IconWrapper className={className}>
    <path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 18a8 8 0 110-16 8 8 0 010 16z" />
    <path d="M12 6a.75.75 0 01.75.75v3.999l2.25.001a.75.75 0 010 1.5l-3 .001a.75.75 0 01-.75-.75V6.75A.75.75 0 0112 6zm-1.03 8.22a.75.75 0 00-1.06-1.06l-1.125 1.125a.75.75 0 101.06 1.06l1.125-1.125zm3.18-1.06a.75.75 0 10-1.06 1.06l1.125 1.125a.75.75 0 001.06-1.06l-1.125-1.125z" />
  </IconWrapper>
);

export const AthenaIcon: React.FC<{ className?: string }> = ({ className }) => (
  <IconWrapper className={className}>
    <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-4.794a.75.75 0 00-1.06 1.06L11.192 12l-1.296 1.734a.75.75 0 101.06 1.06l1.5-2a.75.75 0 000-1.06l-1.5-2z" clipRule="evenodd" />
    <path d="M14.25 9.75a.75.75 0 00-1.06-1.06l-1.5 2a.75.75 0 000 1.06l1.5 2a.75.75 0 101.06-1.06L13.808 12l.442-.594z" />
  </IconWrapper>
);

export const AegisIcon: React.FC<{ className?: string }> = ({ className }) => (
  <IconWrapper className={className}>
    <path fillRule="evenodd" d="M12.5 4.5a8 8 0 100 16 8 8 0 000-16zM11 5.5a7 7 0 110 14 7 7 0 010-14z" clipRule="evenodd" />
    <path d="M12.5 6a1 1 0 011 1v6a1 1 0 11-2 0V7a1 1 0 011-1zM12.5 16a1 1 0 100-2 1 1 0 000 2z" />
  </IconWrapper>
);

export const HeliosIcon: React.FC<{ className?: string }> = ({ className }) => (
  <IconWrapper className={className}>
    <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v3.75a.75.75 0 001.5 0V6zM10.5 10.875a.75.75 0 00-1.5 0v.001a.75.75 0 001.5 0v-.001zM12 12.375a.75.75 0 01.75.75v3.125a.75.75 0 01-1.5 0V13.125a.75.75 0 01.75-.75zM13.5 10.875a.75.75 0 00-1.5 0v.001a.75.75 0 001.5 0v-.001z" clipRule="evenodd" />
  </IconWrapper>
);

export const EidosIcon: React.FC<{ className?: string }> = ({ className }) => (
  <IconWrapper className={className}>
    <path d="M12 3.75a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5a.75.75 0 01.75-.75zM17.61 6.39a.75.75 0 011.06 1.06l-1.06 1.06a.75.75 0 01-1.06-1.06l1.06-1.06zM20.25 12a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5a.75.75 0 01.75.75zM17.61 17.61a.75.75 0 01-1.06 1.06l-1.06-1.06a.75.75 0 111.06-1.06l1.06 1.06zM12 18.75a.75.75 0 01-.75.75v1.5a.75.75 0 011.5 0v-1.5a.75.75 0 01-.75-.75zM6.39 17.61a.75.75 0 01-1.06-1.06l1.06-1.06a.75.75 0 111.06 1.06l-1.06 1.06zM3.75 12a.75.75 0 01.75-.75h1.5a.75.75 0 010 1.5h-1.5a.75.75 0 01-.75-.75zM6.39 6.39a.75.75 0 011.06-1.06l1.06 1.06a.75.75 0 11-1.06 1.06L6.39 6.39z" />
    <path fillRule="evenodd" d="M12 15a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
  </IconWrapper>
);

export const AgentIcon: React.FC<{ name: string; className?: string }> = ({ name, className }) => {
  switch (name) {
    case 'Athena': return <AthenaIcon className={className} />;
    case 'Aegis': return <AegisIcon className={className} />;
    case 'Helios': return <HeliosIcon className={className} />;
    case 'Eidos': return <EidosIcon className={className} />;
    default: return <LogosIcon className={className} />;
  }
};
