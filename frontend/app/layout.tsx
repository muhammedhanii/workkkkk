import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Wood Cutting Optimizer',
  description: 'AutoCUT-style cutting optimization for wood boards',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  )
}
