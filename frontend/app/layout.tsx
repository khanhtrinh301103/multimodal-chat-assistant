// frontend/app/layout.tsx (MODIFY)
import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/components/Auth/AuthProvider';

export const metadata: Metadata = {
  title: 'Multi-Modal Chat Assistant',
  description: 'Text conversations, image analysis, and CSV data insights',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}