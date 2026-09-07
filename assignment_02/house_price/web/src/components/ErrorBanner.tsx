import React from "react";

interface ErrorBannerProps {
  message: string;
  onDismiss: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="notice err" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span>{message}</span>
      <button onClick={onDismiss} style={{ background: 'none', border: 'none', color: 'inherit', fontWeight: 'bold' }}>✕</button>
    </div>
  );
};
